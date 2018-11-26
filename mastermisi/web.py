from flask import Blueprint, Response, render_template, redirect, url_for


web: Blueprint = Blueprint(__name__, 'web', template_folder='./templates')


@web.route('/')
def hello() -> Response:
    return render_template('index.html')


@web.route('/login/', methods=['POST'])
def login() -> Response:
    return redirect(url_for('.passwords'))


@web.route('/passwords/', methods=['GET'])
def passwords() -> Response:
    return 'password list'


@web.route('/passwords/', methods=['POST'])
def create_password() -> Response:
    return redirect(url_for('.passwords'))


@web.route('/passwords/<uuid:id>/', methods=['POST'])
def delete_password() -> Response:
    return redirect(url_for('.passwords'))


@web.route('/pending-approvals/', methods=['GET'])
def pending_approvals() -> Response:
    return 'pending-approvals'


@web.route('/pending-approvals/<uuid:id>/', methods=['GET'])
def do_approval() -> Response:
    return 'do_approval'


@web.route('/pending-approvals/<uuid:id>/', methods=['POST'])
def approve() -> Response:
    return redirect(url_for('.pending_approvals'))
