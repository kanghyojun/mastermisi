from flask import url_for


def get_url(app, *args, **kwargs):
    with app.test_request_context():
        return url_for(*args, **kwargs)
