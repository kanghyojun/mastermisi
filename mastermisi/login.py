import functools
from typing import Any, Callable, NewType
import uuid

from flask import Response, g, jsonify, request

from .entity import Customer
from .orm import session

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
        token = request.args.get('token')
        if not token:
            return jsonify(message='missing token'), 400
        g.customer = session.query(Customer) \
            .filter(Customer.id == uuid.UUID(token)) \
            .first()
        if not g.customer:
            return jsonify(message=':/'), 403
        return handler(*args, **kwargs)

    return deco
