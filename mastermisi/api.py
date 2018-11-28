import urllib.parse
import uuid

from flask import Blueprint, Response, g, jsonify, request
from sqlalchemy.orm.exc import NoResultFound

from .entity import Account, Approval, Customer
from .login import authorized
from .orm import session

__all__ = 'api',
api = Blueprint(__name__, 'api', url_prefix='/api')


@api.route('/auth/', methods=['POST'])
def auth() -> Response:
    """브라우저 익스텐션용 로그인 API"""
    payload = request.get_json()
    missing_keys = set()
    for k in {'name', 'passphrase'}:
        if not payload or k not in payload:
            missing_keys.add(k)
    if missing_keys:
        return jsonify(missing_keys=list(missing_keys)), 400
    try:
        customer = session.query(Customer) \
            .filter(Customer.name == payload['name']) \
            .one()
    except NoResultFound:
        return jsonify(payload), 404
    if customer.match_passphrase(payload['passphrase']):
        return jsonify(token=customer.token)
    else:
        return jsonify(payload), 403


@api.route('/passwords/', methods=['POST'])
@authorized
def get_passwords() -> Response:
    """특정 웹사이트의 패스워드가 존재하는지 여부를 판단합니다."""
    payload = request.get_json()
    if 'url' not in payload:
        return jsonify(missing_keys=['url']), 400
    o = urllib.parse.urlparse(payload['url'])
    account = session.query(Account) \
        .filter(Account.host == o.netloc) \
        .filter(Account.customer.has(Customer.id == g.customer.id)) \
        .order_by(Account.created_at.desc()) \
        .first()
    if not account:
        u = payload['url']
        return jsonify(
            message=f'there are no password for {u}'
        ), 404
    return jsonify({'id': account.id.hex})


@api.route('/passwords/<uuidhex:id>/approvals/', methods=['POST'])
@authorized
def create_pending_approvals(id: uuid.UUID) -> Response:
    """로그인을 위한 어프루브를 생성한다."""
    try:
        account = session.query(Account) \
            .filter(Account.id == id,
                    Account.customer.has(Customer.id == g.customer.id)) \
            .one()
    except NoResultFound:
        return jsonify('there are no account'), 404
    approval = session.query(Approval) \
        .filter(Approval.account.has(Account.id == account.id),
                Approval.activated) \
        .order_by(Approval.created_at.desc()) \
        .first()
    if not approval:
        approval = account.create_approval()
        session.add(approval)
        session.commit()
    return jsonify(id=approval.id.hex, quiz_answer=approval.quiz_answer)


@api.route('/pending-approvals/<uuidhex:id>/approved/', methods=['GET'])
@authorized
def is_approved(id: uuid.UUID) -> Response:
    """어프루브가 필요한 로그인 정보를 폴링할때 사용할 API"""
    try:
        session.query(Approval) \
            .filter(Approval.id == id,
                    Approval.activated,
                    Approval.approved) \
            .one()
    except NoResultFound:
        res = False
    else:
        res = True
    return jsonify(result=res)


@api.route('/approvals/<uuidhex:id>/decrypt/', methods=['POST'])
def approvals(id: uuid.UUID) -> Response:
    try:
        approval = session.query(Approval) \
            .options() \
            .filter(Approval.id == id, Approval.activated, Approval.approved) \
            .one()
    except NoResultFound:
        return jsonify(success=False), 404
    payload = request.get_json()
    if 'passphrase' not in payload:
        return jsonify(success=False), 400
    try:
        return jsonify(
            success=True,
            name=approval.account.name,
            passphrase=approval.account.decrypt(payload['passphrase'])
        )
    except Exception as e:
        print(e)
        return jsonify(success=False), 500


@api.route('/pending-approvals/<uuidhex:id>/', methods=['POST'])
@authorized
def approve(id: uuid.UUID) -> Response:
    """로그인 어프루브할 것인지 말것인지 정하는 엔드포인트. 퀴즈가 맞지않다면
    로그인 실패처리하게 하도록해야함.

    """
    payload = request.get_json()
    try:
        approval = session.query(Approval) \
            .filter(Approval.id == id) \
            .one()
    except NoResultFound:
        return jsonify('there are no approval'), 404
    if payload['quiz_answer'] != approval.quiz_answer:
        return jsonify('passphase was incorrect'), 403
    try:
        pass_ = approval.account.decrypt(passphrase=payload['passphrase'])
    except AssertionError:
        return jsonify('passphase was incorrect'), 403
    return jsonify(passphrase=pass_, name=approval.account.name)
