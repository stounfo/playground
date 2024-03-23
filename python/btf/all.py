from typing import Iterable
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import asyncio
import time
from icecream import ic

PRODUCT_BASE = "http://127.0.0.1:8000"
INVENTORY_BASE = "http://127.0.0.1:8001"
FAVORITE_BASE = "http://127.0.0.1:8002"
CART_BASE = "http://127.0.0.1:8003"

app = FastAPI()

client = httpx.AsyncClient()


class Product(BaseModel):
    product_id: int
    product_name: str


class Inventory(BaseModel):
    product_id: int
    inventory: int


class Favorite(BaseModel):
    product_id: int


class Cart(BaseModel):
    product_id: int


async def get_inventory(product_id: int) -> Inventory:
    response = await client.get(url=f"{INVENTORY_BASE}/products/{product_id}/inventory")
    response.raise_for_status()
    return Inventory(product_id=product_id, **response.json())


async def get_inventories(
    product_ids: Iterable[int], *, time_left: float
) -> list[Inventory]:
    done, pending = await asyncio.wait(
        [asyncio.create_task(get_inventory(product_id)) for product_id in product_ids],
        timeout=time_left,
    )
    for task in pending:
        task.cancel()

    return [await task for task in done]


async def get_products() -> list[Product]:
    response = await client.get(url=f"{PRODUCT_BASE}/products")
    response.raise_for_status()
    return [Product(**item) for item in response.json()]


async def get_favorites(user_id: int) -> list[Favorite]:
    response = await client.get(url=f"{FAVORITE_BASE}/users/{user_id}/favorites")
    response.raise_for_status()
    return [Favorite(**item) for item in response.json()]


async def get_cart(user_id: int) -> list[Cart]:
    response = await client.get(url=f"{CART_BASE}/users/{user_id}/cart")
    response.raise_for_status()
    return [Cart(**item) for item in response.json()]


class ProductResult(BaseModel):
    product_id: int
    inventory: int | None


class Result(BaseModel):
    cart_items: int | None
    favorite_items: int | None
    products: list[ProductResult]


@app.get("/products/all")
async def all_products():
    user_id = 1
    products_task = asyncio.create_task(get_products())
    cart_task = asyncio.create_task(get_cart(user_id))
    favorites_task = asyncio.create_task(get_favorites(user_id))

    end_time = time.perf_counter() + 0.7
    time_left = end_time - time.perf_counter()
    products_task_done = False
    carts = None
    favorites = None
    while time_left > 0:
        not_done_tasks = [
            task
            for task in (products_task, cart_task, favorites_task)
            if not task.done()
        ]
        if not_done_tasks:
            done, pending = await asyncio.wait(
                not_done_tasks,
                timeout=time_left,
                return_when=asyncio.FIRST_COMPLETED,
            )
        if products_task in done:
            products = await products_task
            if products_task_done is False:
                inventories_task = asyncio.create_task(
                    get_inventories(
                        [product.product_id for product in products],
                        time_left=time_left,
                    )
                )
                products_task_done = True
        if cart_task in done:
            carts = await cart_task
        if favorites_task in done:
            favorites = await favorites_task
        time_left = end_time - time.perf_counter()

    [task.cancel() for task in pending]

    if products_task in pending:
        raise HTTPException(407, "Server error reaching product service.")

    product_id_to_inventory_map = {
        inventory.product_id: inventory.inventory
        for inventory in await inventories_task
    }

    return Result(
        cart_items=len(carts) if carts is not None else None,
        favorite_items=len(favorites) if favorites is not None else None,
        products=[
            ProductResult(
                product_id=product.product_id,
                inventory=product_id_to_inventory_map.get(product.product_id),
            )
            for product in products
        ],
    )
