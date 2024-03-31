from fastapi import FastAPI
from flask import Flask
from asgiref.wsgi import WsgiToAsgi
from starlette.types import Receive, Scope, Send
from icecream import ic


flask_app = Flask(__name__)


@flask_app.route("/")
def home():
    return "Hello, Flask!"


flask_app = WsgiToAsgi(flask_app)


class CustomFastAPI(FastAPI):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        ic(scope)
        try:
            _, app = scope["query_string"].decode("utf-8").split("=")
        except Exception:
            app = "flask"

        if app == "flask":
            await flask_app(scope, receive, send)
        else:
            await super().__call__(scope, receive, send)


fast_api_app = CustomFastAPI()


@fast_api_app.get("/")
async def root():
    return {"message": "Hello, FastAPI"}
