import datetime
import functools
import time
from typing import Any, Callable, NewType
import uuid

from flask import (Response, flash, g, jsonify, redirect, request, session,
                   url_for)

from .entity import Customer
from .orm import session as db_session

__all__ = 'WebHandlerType', 'login_required', 'authorized'
WebHandlerType = NewType('WebHandlerType', Callable[[Any], Response])


def timestamp(offset=0):
    time_ = datetime.datetime.utcnow() + datetime.timedelta(seconds=offset)
    return int(time.mktime(time_.timetuple()))


def login_required(handler: WebHandlerType) -> WebHandlerType:
    @functools.wraps(handler)
    def deco(*args, **kwargs) -> Response:
        if not ('customer_id' in session and 'expired_at' in session):
            flash('로그인을 해 주세요.')
            return redirect(url_for('.signup_form'))
        elif 'expired_at' in session and session['expired_at'] < timestamp():
            flash('세션이 만료되었습니다.')
            return redirect(url_for('.signup_form'))
        session['expired_at'] = timestamp(60 * 5)
        return handler(*args, **kwargs)

    return deco


def authorized(handler: WebHandlerType) -> WebHandlerType:
    @functools.wraps(handler)
    def deco(*args, **kwargs) -> Response:
        token = request.args.get('token')
        if not token:
            return jsonify(message='missing token'), 400
        g.customer = db_session.query(Customer) \
            .filter(Customer.id == uuid.UUID(token)) \
            .first()
        if not g.customer:
            return jsonify(message=':/'), 403
        return handler(*args, **kwargs)

    return deco
