import json

from flask import Flask

from mastermisi.entity import Customer
from mastermisi.orm import Session


def test_auth(fx_wsgi_app: Flask, fx_session: Session) -> None:
    customer = Customer(
        name='pjs',
        passphrase=Customer.create_password('sol')
    )
    fx_session.add(customer)
    fx_session.flush()
    with fx_wsgi_app.test_client() as client:
        response = client.post(
            '/api/auth/', json={'name': 'pjs', 'passphrase': 'sol'}
        )
        assert response.status_code == 200
        payload = json.loads(response.get_data(as_text=True))
        assert payload['token'] == customer.token
