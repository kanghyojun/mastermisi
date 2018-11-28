import uuid

from flask import Flask
from werkzeug.routing import BaseConverter

from .api import api
from .app import App
from .web import web


class UuidHexConverter(BaseConverter):

    def to_python(self, value: str) -> uuid.UUID:
        return uuid.UUID(hex=value)

    def to_url(self, value: uuid.UUID) -> str:
        return value.hex


def create_wsgi_app(app: App) -> Flask:
    flask_app = Flask(__name__)
    flask_app.url_map.converters['uuidhex'] = UuidHexConverter
    flask_app.config['APP_CONFIG'] = app
    flask_app.secret_key = app.secret_key
    flask_app.register_blueprint(api)
    flask_app.register_blueprint(web)
    return flask_app
