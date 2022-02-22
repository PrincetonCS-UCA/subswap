from flask import make_response, render_template
from flask.blueprints import Blueprint
from subapp.models import User
main = Blueprint('main', __name__,
                 template_folder='templates')


@main.route("/", methods=['GET'])
def homepage():
    user = User.query.first().netid
    html = render_template('index.html', netid=user)
    response = make_response(html)
    return response