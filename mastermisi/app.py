from typing import Optional

from settei.base import config_property
from settei.presets.flask import WebConfiguration
from sqlalchemy.engine import Engine, create_engine
from werkzeug.utils import cached_property

from .orm import Session

__all__ = 'App',


class App(WebConfiguration):
    """서버 애플리케이션입니다."""
    secret_key = config_property(
        'web.secret_key', str, '쿠키 암호화용 비밀키'
    )

    database_url = config_property(
        'database.url', str, '데이터베이스 연결용 문자열'
    )

    debug = config_property('web.debug', bool, default=True)

    @cached_property
    def database_engine(self) -> Engine:
        return create_engine(self.database_url)

    def create_session(self, bind: Optional[Engine] = None) -> Session:
        if bind is None:
            bind = self.database_engine
        return Session(bind=bind)
