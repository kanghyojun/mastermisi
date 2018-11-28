from flask import (Blueprint, Response, flash, redirect, render_template,
                   request, session, url_for)
from sqlalchemy.orm.exc import NoResultFound
from wtforms.fields import PasswordField, StringField
from wtforms.form import Form
from wtforms.validators import input_required

from .entity import Account, Customer
from .login import login_required, timestamp
from .orm import session as db_session

__all__ = 'web',
web: Blueprint = Blueprint(__name__, 'web', template_folder='./templates')


class SignForm(Form):
    """이름과 비밀번호를 입력하는 폼."""
    def __init__(self, title: str, action: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.action = action

    name = StringField(u'이름', validators=[input_required()])

    passphrase = PasswordField(u'마스터 암호', validators=[input_required()])


class AccountForm(Form):
    """소유 계정을 입력하는 폼."""
    host = StringField('호스트', validators=[input_required()])

    name = StringField('이름', validators=[input_required()])

    passphrase = PasswordField('암호', validators=[input_required()])

    master_passphrase = PasswordField('마스터 암호',
                                      validators=[input_required()])


@web.route('/', methods=['GET'])
def index() -> Response:
    """메인 페이지."""
    return render_template('index.html')


@web.route('/login/', methods=['GET'])
def login_form() -> Response:
    """로그인 페이지."""
    form = SignForm('로그인', url_for('.login'))
    return render_template('id_pass_form.html', form=form)


@web.route('/login/', methods=['POST'])
def login() -> Response:
    """로그인을 시키고 패스워드 페이지를 볼 수 있게 인증함."""
    form = SignForm('로그인', url_for('.login'), request.form)
    if not form.validate():
        flash('모든 값을 입력해주세요.')
        return redirect(url_for('.login_form'))
    passphrase = Customer.create_passphrase(form.passphrase.data)
    try:
        customer = db_session.query(
            Customer
        ).filter_by(
            name=form.name.data,
            passphrase=passphrase
        ).one()
    except NoResultFound:
        flash('이름 혹은 암호가 잘못되었습니다.')
        return redirect(url_for('.login_form'))
    else:
        session['customer_id'] = customer.id
        session['expired_at'] = timestamp(60 * 5)
        flash(f'{customer.name}님 안녕하세요!')
        return redirect(url_for('.accounts'))


@web.route('/logout/', methods=['GET'])
def logout() -> Response:
    session.clear()
    return redirect(url_for('.login_form'))


@web.route('/signup/', methods=['GET'])
def signup_form() -> Response:
    """가입 페이지."""
    form = SignForm('가입', url_for('.signup'))
    return render_template('id_pass_form.html', form=form)


@web.route('/signup/', methods=['POST'])
def signup() -> Response:
    """가입 처리 핸들러."""
    form = SignForm('가입', url_for('.signup'), request.form)
    if not form.validate():
        flash('모든 값을 입력해주세요.')
        return redirect(url_for('.signup_form'))
    if db_session.query(Customer).filter_by(name=form.name.data).first():
        flash('이미 존재하는 이름입니다.')
        return redirect(url_for('.signup_form'))
    passphrase = Customer.create_passphrase(form.passphrase.data)
    db_session.add(Customer(name=form.name.data, passphrase=passphrase))
    db_session.commit()
    flash('가입이 완료되었습니다.')
    return redirect(url_for('.index'))


@web.route('/passcode/', methods=['GET'])
@login_required
def get_passcode() -> Response:
    return '1234'


@web.route('/accounts/', methods=['GET'])
@login_required
def accounts() -> Response:
    """계정 리스트를 보는 엔드포인트"""
    accounts = db_session.query(Account) \
                         .filter_by(customer_id=session['customer_id'])
    form = AccountForm()
    return render_template('accounts.html', accounts=accounts, form=form)


@web.route('/accounts/', methods=['POST'])
@login_required
def account_new() -> Response:
    """계정을 등록하는 엔드포인트"""
    form = AccountForm(request.form)
    if not form.validate():
        flash('모든 값을 입력해주세요.')
        return redirect(url_for('.accounts'))
    customer = db_session.query(Customer) \
                         .filter_by(id=session['customer_id']) \
                         .one()
    try:
        account = customer.create_account(
            form.host.data,
            form.name.data,
            form.passphrase.data,
            passphrase=form.master_passphrase.data
        )
    except AssertionError:
        flash('마스터 암호가 다릅니다.')
        return redirect(url_for('.accounts'))
    else:
        db_session.add(account)
        db_session.commit()
        flash('등록이 완료되었습니다.')
        return redirect(url_for('.accounts'))


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
