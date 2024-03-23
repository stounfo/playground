from typing import Iterable
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
import asyncio
import time
from icecream import ic

PRODUCT_BASE = "http://127.0.0.1:8000"
INVENTORY_BASE = "http://127.0.0.1:8001"
FAVORITE_BASE = "http://127.0.0.1:8002"
CART_BASE = "http://127.0.0.1:8003"

app = FastAPI()


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


async def get_inventory(product_id: int, session) -> Inventory:
    async with session.get(url=f"{INVENTORY_BASE}/products/{product_id}/inventory") as response:
        response.raise_for_status()
        data = await response.json()
        return Inventory(product_id=product_id, **data)


async def get_inventories(
    product_ids: Iterable[int], *, time_left: float, session
) -> list[Inventory]:
    done, pending = await asyncio.wait(
        [asyncio.create_task(get_inventory(product_id, session)) for product_id in product_ids],
        timeout=time_left,
    )
    for task in pending:
        task.cancel()

    return [await task for task in done]


async def get_products(session) -> list[Product]:
    async with session.get(url=f"{PRODUCT_BASE}/products") as response:
        response.raise_for_status()
        data = await response.json()
        return [Product(**item) for item in data]


async def get_favorites(user_id: int, session) -> list[Favorite]:
    async with session.get(url=f"{FAVORITE_BASE}/users/{user_id}/favorites") as response:
        response.raise_for_status()
        data = await response.json()
        return [Favorite(**item) for item in data]


async def get_cart(user_id: int, session) -> list[Cart]:
    async with session.get(url=f"{CART_BASE}/users/{user_id}/cart") as response:
        response.raise_for_status()
        data = await response.json()
        return [Cart(**item) for item in data]


class ProductResult(BaseModel):
    product_id: int
    inventory: int | None


class Result(BaseModel):
    cart_items: int | None
    favorite_items: int | None
    products: list[ProductResult]


@app.get("/products/all")
async def all_products():
    async with aiohttp.ClientSession() as session:
        user_id = 1
        products_task = asyncio.create_task(get_products(session))
        cart_task = asyncio.create_task(get_cart(user_id, session))
        favorites_task = asyncio.create_task(get_favorites(user_id, session))

        end_time = time.perf_counter() + 1
        time_left = end_time - time.perf_counter()
        try:
            products = await asyncio.wait_for(products_task, timeout=time_left)
        except asyncio.TimeoutError:
            raise HTTPException(407, "Server error reaching product service.")

        time_left = end_time - time.perf_counter()
        inventories = await get_inventories(
            [product.product_id for product in products], session=session, time_left=time_left
        )

        time_left = end_time - time.perf_counter()
        try:
            carts_len = len(await asyncio.wait_for(cart_task, timeout=time_left))
        except asyncio.TimeoutError:
            carts_len = None

        time_left = end_time - time.perf_counter()
        try:
            favorites_len = len(await asyncio.wait_for(favorites_task, timeout=time_left))
        except asyncio.TimeoutError:
            favorites_len = None

    product_id_to_inventory_map = {
        inventory.product_id: inventory.inventory for inventory in inventories
    }

    return Result(
        cart_items=carts_len,
        favorite_items=favorites_len,
        products=[
            ProductResult(
                product_id=product.product_id,
                inventory=product_id_to_inventory_map.get(product.product_id),
            )
            for product in products
        ],
    )
