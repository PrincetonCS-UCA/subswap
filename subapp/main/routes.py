from flask import make_response, render_template, redirect, url_for, session, current_app
from flask.blueprints import Blueprint
from subapp.models import Request
from flask_login import login_required, current_user
from config import COURSES, PERMISSIONS
from subapp import dbscript
from datetime import date

main = Blueprint('main', __name__,
                 template_folder='templates',
                 static_folder='static',
                 static_url_path='/main/static/')


# 1. Splash page
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


@main.route("/about", methods=['GET'])
def about():
    return render_template('main/about.html')


@main.route("/dashboard", methods=['GET', 'PUT'])
@login_required
def dashboard():
    if 'credits' not in session:
        session['credits'] = current_user.balance

    # query database for requests
    active_requests = Request.query.filter(
        Request.accepted == False).filter(Request.date_requested >= date.today()).order_by(Request.date_requested.asc()).all()

    requests = {}
    for course in COURSES:
        if current_user.can(PERMISSIONS[course]) or current_user.is_admin():
            requests[course] = [x for x in active_requests if x.get_course()
                                == course]
    html = render_template('main/dashboard.html',
                           requests=requests, current_user=current_user)
    response = make_response(html)
    return response


@main.route("/profile", methods=['GET', 'PUT'])
@login_required
def profile():
    day_order = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }
    html = render_template('main/profile.html', shifts=current_user.schedule.sort(key=lambda x: day_order[x.day]),
                           requests=current_user.accepted_requests.sort(key=lambda x: x.date_posted), history=current_user.inactive_requests().sort(key=lambda x: x.date_posted))
    return make_response(html)


@main.route("/create_dummy_data", methods=['GET', 'POST'])
@login_required
def create_dummy_data():
    dbscript.create_dummy_data(all=True)
    return redirect(url_for('main.dashboard'))
