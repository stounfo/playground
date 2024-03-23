import functools
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from shared import DB_KEY, destroy_database_pool, create_database_pool
import asyncio
import random

routes = web.RouteTableDef()


@routes.get("/users/{id}/favorites")
async def favorites(request: Request) -> Response:
    try:
        str_id = request.match_info["id"]
        user_id = int(str_id)
        db = request.app[DB_KEY]
        favorite_query = "SELECT product_id from user_favorite where user_id = $1"
        result = await db.fetch(favorite_query, user_id)
        delay: float = random.randint(0, 20) / 10
        await asyncio.sleep(delay)
        if result is not None:
            return web.json_response([dict(record) for record in result])
        else:
            raise web.HTTPNotFound()
    except ValueError:
        raise web.HTTPBadRequest()


app = web.Application()
app.on_startup.append(
    functools.partial(
        create_database_pool,
        host="127.0.0.1",
        port=47318,
        user="user",
        password="secret",
        database="favorites",
    )
)
app.on_cleanup.append(destroy_database_pool)

app.add_routes(routes)
web.run_app(app, port=8002)
