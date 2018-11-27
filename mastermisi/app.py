from typing import Optional

from settei.base import config_property
from settei.presets.flask import WebConfiguration
from sqlalchemy.engine import Engine, create_engine

from .orm import Session

__all__ = 'App',


class App(WebConfiguration):
    """서버 애플리케이션입니다."""
    database_url = config_property(
        'database.url', str, "데이터베이스 연결용 문자열"
    )

    @property
    def database_engine(self) -> Engine:
        return create_engine(self.database_url)

    def create_session(self, bind: Optional[Engine] = None) -> Session:
        if bind is None:
            bind = self.database_engine
        return Session(bind)