import os

from flask import Flask
from ormeasy.sqlalchemy import test_connection
from pytest import fixture

from mastermisi.app import App
from mastermisi.entity import Customer
from mastermisi.orm import Base, Session
from mastermisi.wsgi import create_wsgi_app


def pytest_addoption(parser):
    parser.addoption('--database-url',
                     type=str,
                     default=os.environ.get('TEST_DATABASE_URL'),
                     help='Database URL for testing. [default: %default]')


@fixture
def fx_app(request) -> App:
    try:
        database_url = request.config.getoption('--database-url')
    except ValueError:
        database_url = os.environ.get('TEST_DATABASE_URL')
    return App({
        'web': {
            'secret_key': '과민성 쇼크, 피부 장애, 식욕부진, 가슴쓰림, 위통,',
        },
        'database': {
            'url': database_url,
        },
    })


@fixture
def fx_connection(request, fx_app: App):
    with test_connection(
        fx_app, Base.metadata, fx_app.database_engine,
        request.keywords.get('real_transaction') is not None
    ) as connection:
        yield connection


@fixture
def fx_session(fx_app: App, fx_connection) -> Session:
    session = fx_app.create_session(fx_connection)
    try:
        yield session
    finally:
        session.close()


@fixture
def fx_wsgi_app(fx_app: App) -> Flask:
    return create_wsgi_app(fx_app)


@fixture
def fx_customer(fx_session: Session) -> Customer:
    passphrase = Customer.create_passphrase('world')
    customer = Customer(name='hello', passphrase=passphrase)
    fx_session.add(customer)
    fx_session.flush()
    return customer
