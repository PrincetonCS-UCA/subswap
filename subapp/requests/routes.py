from flask import make_response, render_template
from flask.blueprints import Blueprint
from subapp.models import Request

requests = Blueprint('requests', __name__,
                 template_folder='templates',
                 static_folder='static',
                 static_url_path='/requests/static/')

@requests.route("/request/new/<sub>", methods=['GET'])
def create_request(sub):

    sub = True if sub == 'sub' else False
