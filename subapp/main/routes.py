from flask import make_response, render_template, redirect, url_for
from flask.blueprints import Blueprint
from subapp.models import Request
from flask_login import login_required, current_user
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

    if current_user.is_authenticated:
        # Already logged in
        return redirect(url_for('main.dashboard'))

    html = render_template('main/index.html')
    response = make_response(html)
    return response

@main.route("/dashboard", methods=['GET', 'PUT'])
@login_required
def dashboard():

    # query database for requests
    active_requests = Request.query.filter(Request.accepted==False).all()

    html = render_template('main/dashboard.html', requests=active_requests,current_user=current_user)
    response = make_response(html)
    return response

@main.route("/profile", methods=['GET', 'PUT'])
@login_required
def profile():
    html = render_template('main/profile.html', shifts=current_user.schedule, requests=current_user.accepted_requests, history=current_user.inactive_requests())
    return make_response(html)

