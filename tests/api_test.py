import json
from typing import Sequence
import uuid

from flask import Flask

from mastermisi.entity import Account, Customer
from mastermisi.orm import Session


def test_auth(fx_wsgi_app: Flask, fx_session: Session,
              fx_customer: Customer) -> None:
    with fx_wsgi_app.test_client() as client:
        response = client.post(
            '/api/auth/', json={'name': 'hello', 'passphrase': 'world'}
        )
        assert response.status_code == 200
        payload = json.loads(response.get_data(as_text=True))
        assert payload['token'] == fx_customer.token


def test_get_passwords(fx_wsgi_app: Flask, fx_session: Session,
                       fx_customer: Customer,
                       fx_accounts: Sequence[Account]) -> None:
    client = fx_wsgi_app.test_client()
    response = client.post(
        f'/api/passwords/?token={fx_customer.token}',
        json={'url': 'http://google.com'}
    )
    assert response.status_code == 200
    payload = json.loads(response.get_data(as_text=True))
    expected = uuid.UUID('3e9bce54-003e-4419-8f58-f8b19152c768')
    assert uuid.UUID(payload['id']) == expected


def test_approve(fx_wsgi_app: Flask, fx_session: Session,
                 fx_customer: Customer,
                 fx_accounts: Sequence[Account]):
    one, _ = fx_accounts
    client = fx_wsgi_app.test_client()
    approval = one.create_approval()
    approval.quiz_answer = 'foobar'
    fx_session.add(approval)
    fx_session.commit()
    response = client.post(
        f'/api/pending-approvals/{approval.id!s}/?token={fx_customer.token}',
        json={'passphrase': 'world', 'quiz_answer': 'foobar'}
    )
    assert response.status_code == 200
    payload = json.loads(response.get_data(as_text=True))
    assert payload['passphrase'] == 'abcd'
    assert payload['name'] == 'honggildong'
