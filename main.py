import uvicorn
from starlette.middleware.wsgi import WSGIMiddleware
from starlette.applications import Starlette
from starlette.routing import Mount

from website.main import app as flask_app
from website.api import app as fastapi_app

flask_asgi_app = WSGIMiddleware(flask_app)

routes = [
    Mount('/api', app=fastapi_app),
    Mount('/', app=flask_asgi_app),
]

app = Starlette(routes=routes)

if __name__ == "__main__":
    uvicorn.run("main:app")