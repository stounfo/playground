from fastapi import FastAPI, Body, Query, Header
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()


class ItemBody(BaseModel):
    """
    Important text about the body model
    """
    name: str = Field(
        ..., min_length=1, max_length=50, description="The name of the item"
    )
    description: str = Field(None, max_length=200, description="The item's description")
    price: float = Field(
        ..., gt=0, description="The price of the item, must be greater than 0"
    )
    quantity: int = Field(
        ..., gt=0, le=100, description="The quantity of the item, between 1 and 100"
    )


@app.post("/items/{item_id}")
async def create_item(
    item_id: int,
    user_agent: Annotated[int, Header()],
    item: ItemBody = Body(...),
    additional_note: int = Query(None, description="An additional note for the item"),
):
    """
    Important text about the endpoint
    """
    return {
        "item_id": item_id,
        "item": item.dict(),
        "additional_note": additional_note,
        "user_agent": user_agent,
    }
