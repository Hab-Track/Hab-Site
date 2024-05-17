import uvicorn
from starlette.middleware.wsgi import WSGIMiddleware as StarletteWSGIMiddleware
from starlette.applications import Starlette
from starlette.routing import Mount

from website.flask_app import app as flask_app
from website.api_app import app as fastapi_app


def create_app():
    # Envelopper l'application Flask avec WSGIMiddleware
    flask_asgi_app = StarletteWSGIMiddleware(flask_app)

    # Créer une application Starlette pour monter les applications
    routes = [
        Mount('/api', app=fastapi_app),
        Mount('/', app=flask_asgi_app),
    ]

    return Starlette(routes=routes)


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000)