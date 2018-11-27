from flask import current_app, has_request_context
from alembic.config import Config
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
    """Create alembic configuration.

    :param app:
    :param engine:
    :return: The alembic configuration.
    :rtype: :class:`alembic.config.Config`

    """
    if not (app or engine):
        raise ValueError('One of `app` or `engine` MUST be given.')
    if app:
        database_url = app.database_url
    elif isinstance(engine, Engine):
        database_url = str(engine.url)
    elif isinstance(engine, str):
        database_url = engine
    else:
        raise ValueError('`engine` MUST be instance of `str` or '
                         '`sqlalchemy.engine.Engine`. '
                         'not {!r}.'.format(engine))
    cfg = Config()
    cfg.set_main_option('script_location', 'mastermisi:migrations')
    cfg.set_main_option('sqlalchemy.url', database_url)
    cfg.set_main_option('url', database_url)
    return cfg
