from flask import url_for


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
