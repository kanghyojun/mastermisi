from typing import Optional, Union

from flask import current_app, has_request_context
from alembic.config import Config
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker
from ormeasy.sqlalchemy import repr_entity
from werkzeug.local import LocalProxy

__all__ = 'Base', 'Session', 'get_alembic_config'


@as_declarative()
class Base:

    def __repr__(self) -> str:
        return repr_entity(self)


Session = sessionmaker()


@LocalProxy
def session() -> Session:
    if has_request_context():
        ctx = request._get_current_object()
        app_config = current_app.config['APP_CONFIG']
    try:
        session = ctx._current_session
    except AttributeError:
        session = app_config.create_session(bind)
        ctx._current_session = session
    finally:
        return session


def get_alembic_config(
    app: Optional['mastermisi.app.App'] = None,
    engine: Union[None, str, Engine] = None
) -> Config:
    """alembic 설정을 만듭니다."""
    if not (app or engine):
        raise ValueError('`app` 또는 `engine` 값이 있어야 합니다.')
    if app:
        database_url = app.database_url
    elif isinstance(engine, Engine):
        database_url = str(engine.url)
    elif isinstance(engine, str):
        database_url = engine
    else:
        raise ValueError('`engine` 값은 `str` 이거나 '
                         '`sqlalchemy.engine.Engine`. '
                         '이어야 합니다. {!r} 입력됨.'.format(engine))
    cfg = Config()
    # TODO: mastermisi:migraions로 하면 설정이 없다 그러고
    #       mastermisi/migrations로 하면 디렉터리를 잘못 잡음
    cfg.set_main_option('script_location', 'mastermisi/migrations')
    cfg.set_main_option('sqlalchemy.url', database_url)
    cfg.set_main_option('url', database_url)
    return cfg
