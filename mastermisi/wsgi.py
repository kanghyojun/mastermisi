from flask import Flask

from .api import api
from .app import App
from .web import web


def create_wsgi_app(app: App) -> Flask:
    flask_app = Flask(__name__)
    flask_app.config['APP_CONFIG'] = app
    flask_app.register_blueprint(api)
    flask_app.register_blueprint(web)
    return flask_app
