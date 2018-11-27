from flask import Blueprint, Response, jsonify, request
from sqlalchemy.orm.exc import NoResultFound

from .entity import Customer
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
    if customer.match_password(payload['passphrase']):
        return jsonify(token=customer.token)
    else:
        return jsonify(payload), 403


@api.route('/passwords/', methods=['POST'])
def get_passwords() -> Response:
    """특정 웹사이트의 패스워드가 존재하는지 여부를 판단합니다."""
    payload = request.get_json()
    assert 'url' in payload
    return jsonify({'id': 1})


@api.route('/passwords/<int:id>/approvals/', methods=['POST'])
@authorized
def create_pending_approvals(id: int) -> Response:
    """로그인을 위한 어프루브를 생성한다."""
    # 패스워드의 id가 아닌 approval의 id가 필요
    return jsonify(id=123)


@api.route('/pending-approvals/<int:id>/approved/', methods=['GET'])
@authorized
def is_approved() -> Response:
    """어프루브가 필요한 로그인 정보를 폴링할때 사용할 API"""
    return jsonify()


@api.route('/pending-approvals/<int:id>/', methods=['POST'])
@authorized
def approve(id) -> Response:
    """로그인 어프루브할 것인지 말것인지 정하는 엔드포인트. 퀴즈가 맞지않다면
    로그인 실패처리하게 하도록해야함.

    """
    return jsonify(password='dmadkrdmfemewk', id='admire93')
