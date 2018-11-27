from flask import (Blueprint, Response, flash, redirect, render_template,
                   request, url_for)
from wtforms.fields import PasswordField, StringField
from wtforms.form import Form
from wtforms.validators import input_required

from .login import login_required

__all__ = 'web',
web: Blueprint = Blueprint(__name__, 'web', template_folder='./templates')


class SignForm(Form):
    """이름과 비밀번호를 입력하는 폼."""
    def __init__(self, title: str, action: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.action = action

    name = StringField(u'이름', validators=[input_required()])

    passphrase = PasswordField(u'비밀 번호', validators=[input_required()])


@web.route('/')
def hello() -> Response:
    """메인 페이지, 로그인 페이지 겸해서 있는 페이지."""
    form = SignForm('로그인', url_for('.login'))
    return render_template('id_pass_form.html', form=form)


@web.route('/login/', methods=['POST'])
def login() -> Response:
    """로그인을 시키고 패스워드 페이지를 볼 수 있게 인증함."""
    form = SignForm('로그인', url_for('.login'), request.form)
    if not form.validate():
        flash('에러')
        return redirect(url_for('.passwords'))
    return redirect(url_for('.passwords'))


@web.route('/passcode/', methods=['GET'])
@login_required
def get_passcode() -> Response:
    return '1234'


@web.route('/passwords/', methods=['GET'])
@login_required
def passwords() -> Response:
    """패스워드 리스트를 볼 수 있고, 패스워드 생성도 할 수 있어야함."""
    return 'password list & create'


@web.route('/passwords/', methods=['POST'])
@login_required
def create_password() -> Response:
    """패스워드를 생성하고, ``passwords``로 리디렉션함."""
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
