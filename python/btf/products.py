from fastapi import FastAPI, Depends
from databases import Database
import uvicorn

# Configuration for the database connection
DATABASE_URL = "postgresql://user:secret@localhost:47318/products"

app = FastAPI()
database = Database(DATABASE_URL)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/products")
async def read_products():
    query = "SELECT product_id, product_name FROM product"
    result = await database.fetch_all(query=query)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

