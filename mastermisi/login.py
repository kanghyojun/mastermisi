import functools

from flask import Response

from typing import Any, NewType, Callable


__all__ = 'WebHandlerType', 'login_required', 'authorized'
WebHandlerType = NewType('WebHandlerType', Callable[[Any], Response])


def login_required(handler: WebHandlerType) -> WebHandlerType:
    @functools.wraps(handler)
    def deco(*args, **kwargs) -> Response:
        return handler(*args, **kwargs)

    return deco


def authorized(hanlder: WebHandlerType) -> WebHandlerType:
    @functools.wraps(handler)
    def deco(*args, **kwargs) -> Response:
        return handler(*args, **kwargs)

    return deco
