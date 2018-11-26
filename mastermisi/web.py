from flask import (Blueprint, Response, render_template, redirect, url_for,
                   jsonify)

from .login import login_required


__all__ = 'web',
web: Blueprint = Blueprint(__name__, 'web', template_folder='./templates')


@web.route('/')
def hello() -> Response:
    """메인 페이지, 로그인 페이지 겸해서 있는 페이지."""
    return render_template('index.html')


@web.route('/login/', methods=['POST'])
def login() -> Response:
    """로그인을 시키고 패스워드 페이지를 볼 수 있게 인증함."""
    return redirect(url_for('.passwords'))


@web.route('/passwords/', methods=['GET'])
@login_required
def passwords() -> Response:
    """패스워드 리스트를 볼 수 있고, 패스워드 생성도 할 수 있어야함."""
    return 'password list & create'


@web.route('/passwords/', methods=['POST'])
@login_required
def create_password() -> Response:
    """패스워드를 생성하고, ``passwords``\ 로 리디렉션함."""
    return redirect(url_for('.passwords'))


@web.route('/passwords/<int:id>/', methods=['POST'])
@login_required
def delete_password() -> Response:
    """패스워드를 지움."""
    return redirect(url_for('.passwords'))


@web.route('/pending-approvals/', methods=['GET'])
@login_required
def pending_approvals() -> Response:
    """어프루브를 기다리고 있는 로그인 리스트들."""
    return 'pending-approvals'


@web.route('/pending-approvals/<int:id>/', methods=['GET'])
@login_required
def do_approval() -> Response:
    """로그인 리스트를 어프루브하기 위해 퀴즈 같은 것을 맞춰야할 수 있다."""
    return 'do_approval'


@web.route('/pending-approvals/<int:id>/', methods=['DELETE'])
def deny_approvals() -> Response:
    """로그인을 거절함."""
    return redirect(url_for('.do_approval'))
