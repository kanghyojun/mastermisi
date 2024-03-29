from flask import url_for

from mastermisi.entity import Account, Customer
from mastermisi.web import timestamp


def get_url(app, *args, **kwargs):
    with app.test_request_context():
        return url_for(*args, **kwargs)


def test_login(fx_wsgi_app, fx_customer):
    url = get_url(fx_wsgi_app, 'mastermisi.web.login')
    with fx_wsgi_app.test_client() as c:
        resp = c.post(url, data={
            'name': 'hello',
            'passphrase': 'world',
        })
        assert resp.status_code == 302
        with c.session_transaction() as s:
            assert s['_flashes'][0][1] == 'hello님 안녕하세요!'
            assert s['customer_id'] == fx_customer.id
            assert s['expired_at'] - timestamp() <= 60 * 5


def test_login_fail(fx_wsgi_app, fx_customer):
    url = get_url(fx_wsgi_app, 'mastermisi.web.login')
    with fx_wsgi_app.test_client() as c:
        resp = c.post(url, data={
            'name': 'hello',
        })
        assert resp.status_code == 302
        with c.session_transaction() as s:
            assert s['_flashes'][0][1] == '모든 값을 입력해주세요.'
        resp = c.post(url, data={
            'name': 'bye',
            'passphrase': 'world',
        })
        assert resp.status_code == 302
        with c.session_transaction() as s:
            assert s['_flashes'][1][1] == '이름 혹은 암호가 잘못되었습니다.'


def test_signup(fx_wsgi_app, fx_session):
    url = get_url(fx_wsgi_app, 'mastermisi.web.signup')
    assert not fx_session.query(Customer).filter_by(
        name='hello',
        passphrase=Customer.create_passphrase('world')
    ).first()
    with fx_wsgi_app.test_client() as c:
        resp = c.post(url, data={
            'name': 'hello',
            'passphrase': 'world',
        })
        assert resp.status_code == 302
        with c.session_transaction() as s:
            assert s['_flashes'][0][1] == '가입이 완료되었습니다.'
    assert fx_session.query(Customer).filter_by(
        name='hello',
        passphrase=Customer.create_passphrase('world')
    ).one()


def test_signup_fail(fx_wsgi_app, fx_customer):
    url = get_url(fx_wsgi_app, 'mastermisi.web.signup')
    with fx_wsgi_app.test_client() as c:
        resp = c.post(url, data={
            'name': 'hello',
        })
        assert resp.status_code == 302
        with c.session_transaction() as s:
            assert s['_flashes'][0][1] == '모든 값을 입력해주세요.'
        resp = c.post(url, data={
            'name': 'hello',
            'passphrase': 'world',
        })
        assert resp.status_code == 302
        with c.session_transaction() as s:
            assert s['_flashes'][1][1] == '이미 존재하는 이름입니다.'


def test_account_new(fx_wsgi_app, fx_session, fx_customer):
    url = get_url(fx_wsgi_app, 'mastermisi.web.account_new')
    assert not fx_session.query(Account).filter_by(
        host='theseedle.com',
        name='kndantes',
        customer=fx_customer
    ).first()
    with fx_wsgi_app.test_client() as c:
        with c.session_transaction() as s:
            s['customer_id'] = fx_customer.id
            s['expired_at'] = timestamp(60 * 5)
        resp = c.post(url, data={
            'host': 'theseedle.com',
            'name': 'kndantes',
            'passphrase': 'kndantesisbest',
            'master_passphrase': 'world',
        })
        assert resp.status_code == 302
        with c.session_transaction() as s:
            assert s['_flashes'][0][1] == '등록이 완료되었습니다.'
    assert fx_session.query(Account).filter_by(
        host='theseedle.com',
        name='kndantes',
        customer=fx_customer
    ).one()


def test_account_new_fail(fx_wsgi_app, fx_customer, fx_account):
    url = get_url(fx_wsgi_app, 'mastermisi.web.account_new')
    with fx_wsgi_app.test_client() as c:
        with c.session_transaction() as s:
            s['customer_id'] = fx_customer.id
            s['expired_at'] = timestamp(60 * 5)
        resp = c.post(url, data={
            'host': 'theseedle.com',
            'name': 'kndantes',
            'passphrase': 'kndantesisbest',
        })
        assert resp.status_code == 302
        with c.session_transaction() as s:
            assert s['_flashes'][0][1] == '모든 값을 입력해주세요.'
        resp = c.post(url, data={
            'host': 'theseedle.com',
            'name': 'kndantes',
            'passphrase': 'kndantesisbest',
            'master_passphrase': 'vaseline',
        })
        assert resp.status_code == 302
        with c.session_transaction() as s:
            assert s['_flashes'][1][1] == '마스터 암호가 다릅니다.'
