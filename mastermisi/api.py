from flask import Blueprint, Response, jsonify

from .login import authorized

__all__ = 'api',
api = Blueprint(__name__, 'api')


@api.route('/auth/', methods=['POST'])
def auth() -> Response:
    """브라우저 익스텐션용 로그인 API"""
    return jsonify()


@api.route('/passwords/<int:id>/approvals/', methods=['POST'])
@authorized
def create_pending_approvals() -> Response:
    """로그인을 위한 어프루브를 생성한다."""
    return jsonify()



@api.route('/pending-approvals/<int:id>/approved/', methods=['GET'])
@authorized
def is_approved() -> Response:
    """어프루브가 필요한 로그인 정보를 폴링할때 사용할 API"""
    return jsonify()



@api.route('/pending-approvals/<int:id>/', methods=['POST'])
@authorized
def approve() -> Response:
    """로그인 어프루브할 것인지 말것인지 정하는 엔드포인트. 퀴즈가 맞지않다면
    로그인 실패처리하게 하도록해야함.

    """
    return jsonify()
