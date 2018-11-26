from flask import Flask, render_template
from .web import web


def create_wsgi_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(web)
    return app


