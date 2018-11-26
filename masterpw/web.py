from flask import Blueprint, render_template


web = Blueprint(__name__, 'web', template_folder='./templates')


@web.route('/')
def hello():
    return render_template('index.html')
