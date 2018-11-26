from mastermisi.wsgi import create_wsgi_app


if __name__ == '__main__':
    wsgi = create_wsgi_app()
    wsgi.run(debug=True)
