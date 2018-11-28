#!/usr/bin/env python3
import argparse
import pathlib

from mastermisi.app import App
from mastermisi.wsgi import create_wsgi_app


parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument('config', type=pathlib.Path)


if __name__ == '__main__':
    args = parser.parse_args()
    app = App.from_path(args.config)
    wsgi = create_wsgi_app(app)
    wsgi.run(debug=app.debug, host='0.0.0.0')
