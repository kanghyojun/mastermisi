import functools
from typing import Any, Callable, NewType

from flask import Blueprint, Response, render_template, redirect, url_for


web: Blueprint = Blueprint(__name__, 'web', template_folder='./templates')
WebHandler = NewType('WebHandler', Callable[[Any], Response])


def login_required(handler: WebHandler) -> WebHandler:
    @functools.wraps(handler)
    def deco(*args, **kwargs) -> Response:
        return handler(*args, **kwargs)

    return deco


@web.route('/')
def hello() -> Response:
    """메인 페이지, 로그인 페이지 겸해서 있는 페이지.

    """
    return render_template('index.html')


@web.route('/login/', methods=['POST'])
def login() -> Response:
    """로그인을 시키고 
    """
    return redirect(url_for('.passwords'))


@web.route('/passwords/', methods=['GET'])
@login_required
def passwords() -> Response:
    return 'password list & create'


@web.route('/passwords/', methods=['POST'])
@login_required
def create_password() -> Response:
    return redirect(url_for('.passwords'))


@web.route('/passwords/<uuid:id>/', methods=['POST'])
@login_required
def delete_password() -> Response:
    return redirect(url_for('.passwords'))


@web.route('/pending-approvals/', methods=['GET'])
@login_required
def pending_approvals() -> Response:
    return 'pending-approvals'


@web.route('/pending-approvals/<uuid:id>/', methods=['GET'])
@login_required
def do_approval() -> Response:
    return 'do_approval'


@web.route('/pending-approvals/<uuid:id>/approved/', methods=['GET'])
@login_required
def is_approved() -> Response:
    return 'approved?'


@web.route('/pending-approvals/<uuid:id>/', methods=['POST'])
@login_required
def approve() -> Response:
    return redirect(url_for('.pending_approvals'))
