import pathlib

from mastermisi.app import App
from mastermisi.wsgi import create_wsgi_app


if __name__ == '__main__':
    wsgi = create_wsgi_app(App.from_path(pathlib.Path('./local.toml')))
    wsgi.run(debug=True)
