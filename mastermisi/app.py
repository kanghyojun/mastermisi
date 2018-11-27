from settei.base import config_property
from settei.presets.flask import WebConfiguration

class App(WebConfiguration):
    """서버 애플리케이션입니다."""
    database_url = config_property(
        'database.url', str, "데이터베이스 연결용 문자열"
    )
