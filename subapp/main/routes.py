from flask import make_response, render_template
from flask.blueprints import Blueprint
from subapp.models import Request
main = Blueprint('main', __name__,
                 template_folder='templates',
                 static_folder='static',
                 static_url_path='/main/static/')


# 1. Splash page
@main.route("/", methods=['GET'])
def homepage():
    """
    Route for the homepage.

    Case 1: Logged in: Redirects to Found Feed (/found)
    Case 2: Logged out: Redirects to Splash Page (/)
    """

    # if current_user.is_authenticated:
    #     # Already logged in
    #     return redirect(url_for('main.found'))

    html = render_template('main/index.html')
    response = make_response(html)
    return response

@main.route("/dashboard", methods=['GET', 'PUT'])
def dashboard():

    # query database for requests
    requests = Request.query.filter(Request.accepted==False).all()
    html = render_template('main/dashboard.html', requests=requests)
    response = make_response(html)
    return response

def profile():
    return render_template('main/profile.html')
