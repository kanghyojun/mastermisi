from flask import Flask

from .api import api
from .app import App
from .web import web


def create_wsgi_app(app: App) -> Flask:
    app = Flask(__name__)
    app.config['APP_CONFIG'] = app
    app.register_blueprint(api)
    app.register_blueprint(web)
    return app
