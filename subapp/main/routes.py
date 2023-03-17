from datetime import date
from flask import make_response, render_template, redirect, url_for, session
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from config import COURSES, PERMISSIONS
from subapp import dbscript
from subapp.models import Request
# ----------------------------------------------------------------------
main = Blueprint('main', __name__,
                 template_folder='templates',
                 static_folder='static',
                 static_url_path='/main/static/')
# ----------------------------------------------------------------------


@main.route("/", methods=['GET'])
def homepage():
    """
    Route for the homepage.

    Case 1: Logged in: Redirects to Dashboard (/dashboard)
    Case 2: Logged out: Redirects to Splash Page (/)
    """

    if current_user.is_authenticated:
        # Already logged in
        return redirect(url_for('main.dashboard'))

    html = render_template('main/index.html')
    response = make_response(html)
    return response
# ----------------------------------------------------------------------


@main.route("/about", methods=['GET'])
def about():
    """
    About page has instructions on how to use the platform.
    """
    return render_template('main/about.html')
# ----------------------------------------------------------------------


@main.route("/dashboard", methods=['GET', 'PUT'])
@login_required
def dashboard():
    """
    Displays active requests based on permissions of the user.
    """
    session['credits'] = current_user.balance

    # query database for requests
    active_requests = Request.query.filter(Request.accepted == False).filter(
        Request.date_requested >= date.today()).order_by(Request.date_requested.asc()).all()

    requests = {}

    for course in COURSES:
        if current_user.can(PERMISSIONS[course + '-accept']) or current_user.is_admin():
            requests[course] = [x for x in active_requests if x.get_course()
                                == course]

    html = render_template('main/dashboard.html',
                           requests=requests, current_user=current_user)
    return make_response(html)
# ----------------------------------------------------------------------


@main.route("/profile", methods=['GET', 'PUT'])
@login_required
def profile():
    """
    Displays permanent schedule, accepted requests, and posting history
    of current user. Also allows user to create new requests.
    """
    session['credits'] = current_user.balance
    day_order = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }
    schedule = sorted(current_user.schedule, key=lambda x: day_order[x.day])
    upcoming_reqs, past_reqs = current_user.accepted_reqs()
    his = sorted(current_user.inactive_requests(), key=lambda x: x.date_posted)

    html = render_template('main/profile.html',
                           shifts=schedule, upcoming_reqs=upcoming_reqs, past_reqs=past_reqs, history=his)
    return make_response(html)

# ----------------------------------------------------------------------
# Error handling
# ----------------------------------------------------------------------


@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html', error=error), 404
# ----------------------------------------------------------------------


@main.app_errorhandler(Exception)
@main.app_errorhandler(500)
def internal_error(error):
    return render_template('500.html', error=error), 500
# ----------------------------------------------------------------------


@main.app_errorhandler(403)
def forbidden_error(error):
    return render_template('403.html', error=error), 403
# ----------------------------------------------------------------------
