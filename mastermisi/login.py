import functools
from typing import Any, Callable, NewType

from flask import Response

__all__ = 'WebHandlerType', 'login_required', 'authorized'
WebHandlerType = NewType('WebHandlerType', Callable[[Any], Response])


def login_required(handler: WebHandlerType) -> WebHandlerType:
    @functools.wraps(handler)
    def deco(*args, **kwargs) -> Response:
        return handler(*args, **kwargs)

    return deco


def authorized(handler: WebHandlerType) -> WebHandlerType:
    @functools.wraps(handler)
    def deco(*args, **kwargs) -> Response:
        return handler(*args, **kwargs)

    return deco
