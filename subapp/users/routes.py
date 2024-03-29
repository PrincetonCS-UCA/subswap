from flask import session, Blueprint, redirect, request, url_for, jsonify, render_template
from subapp.models import User, Role
from subapp import db
from flask_login import login_user, current_user, logout_user, login_required
from subapp import cas_client
from config import ADMINS

# ----------------------------------------------------------------------
users = Blueprint('users', __name__, template_folder='templates')
# reference: https://djangocas.dev/blog/python-cas-flask-example/
# ----------------------------------------------------------------------


@users.route('/login')
def login():
    if current_user.is_authenticated and 'username' in session:
        # Already logged in
        return redirect(url_for('main.dashboard'))

    next = request.args.get('next')
    ticket = request.args.get('ticket')
    if not ticket:
        # No ticket, the request come from end user, send to CAS login
        cas_login_url = cas_client.get_login_url()
        return redirect(cas_login_url)

    # user (net id), attributes, pgtiou
    user, _, _ = cas_client.verify_ticket(ticket)

    if not user:
        # return 'Failed to verify ticket. <a href="/login">Login</a>'
        return redirect(url_for(users.login))

    else:  # Login successfully, redirect according `next` query parameter.
        user = user.lower()
        session['username'] = user  # netid

        # check if user exists
        new_user = User.query.filter(User.netid == user).one_or_none()

        if new_user is None:
            new_user = User(netid=user)

            # testing pur
            if user in ADMINS:
                if len(Role.query.all()) == 0:
                    Role.insert_roles()
                new_user.role = Role.query.filter_by(name='Admin').first()

            db.session.add(new_user)
            db.session.commit()

        login_user(new_user)
        session['credits'] = new_user.balance

        return redirect(next)
# ----------------------------------------------------------------------


@users.route('/logout')
@login_required
def logout():
    redirect_url = url_for('users.logout_callback', _external=True)
    cas_logout_url = cas_client.get_logout_url(redirect_url)

    return redirect(cas_logout_url)
# ----------------------------------------------------------------------


@users.route('/logout_callback')
def logout_callback():
    # redirect from CAS logout request after CAS logout successfully
    session.pop('username', None)
    session.pop('credits', None)
    logout_user()
    return redirect(url_for('main.homepage'))
# ----------------------------------------------------------------------


@users.route('/balance')
@login_required
def balance():
    return jsonify({'balance': current_user.balance})

# ----------------------------------------------------------------------
# Error handling
# ----------------------------------------------------------------------


@users.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html', error=error), 404
# ----------------------------------------------------------------------


@users.app_errorhandler(Exception)
@users.app_errorhandler(500)
def internal_error(error):
    return render_template('500.html', error=error), 500
# ----------------------------------------------------------------------


@users.app_errorhandler(403)
def forbidden_error(error):
    return render_template('403.html', error=error), 403
# ----------------------------------------------------------------------
