import requests
from datetime import datetime
from flask import (redirect, url_for, render_template,
                   request, jsonify, flash, session, current_app)
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from config import PRICING_ALG
from subapp import db
from subapp.models import Request, Shift
from subapp.requests.forms import RequestForm
from subapp.requests.util import (
    get_swap_options, process_shift_str, calc_base_price)
# ----------------------------------------------------------------------

requests = Blueprint('requests', __name__,
                     template_folder='templates',
                     static_folder='static',
                     static_url_path='/requests/static/')
# ----------------------------------------------------------------------


@requests.route("/shift/<shiftid>/request", methods=['POST', 'GET'])
@login_required
def create_request(shiftid):
    # shift requested
    shift = Shift.query.filter_by(id=shiftid).first()
    print(f"shift: {shift.id}, {shift.course}, {shift.start}")
    form = RequestForm()

    # shifts in curr user schedule
    if form.validate_on_submit():
        # create request
        new_request = Request(
            date_requested=form.date_requested.data,
            base_price=calc_base_price(
                shift.id, form.date_requested.data.strftime('%Y-%m-%d'))['price']
        )

        print(
            f"request: {new_request.id}, {new_request.date_requested}, {new_request.posted_by}, {new_request.shift}")
        new_request.shift.append(shift)
        new_request.posted_by.append(current_user)

        print(
            f"request: {new_request.id}, {new_request.date_requested}, {new_request.posted_by}, {new_request.shift}")
        print(f"user: {current_user.id}, {current_user.posted_requests}")

        db.session.add(new_request)
        current_user.balance -= new_request.get_price()
        session['credits'] = current_user.balance
        db.session.commit()

        return redirect(url_for('main.dashboard'))
    else:
        # current_app.logger.error("Request form", form.errors)
        print(form.errors)

    return render_template('requests/create_request.html', form=form, shiftid=int(shiftid), shifts=current_user.schedule, day=shift.day)
# ----------------------------------------------------------------------


@requests.route("/request/<requestid>/edit", methods=['POST', 'GET'])
@login_required
def edit_request(requestid):
    # shift requested
    rqst = Request.query.filter_by(id=requestid).first()
    if current_user != rqst.posted():
        return redirect(url_for('main.dashboard'))
    if rqst.accepted:
        return redirect(url_for('main.dashboard'))

    shift = rqst.shift[0]

    form = RequestForm()

    # shifts in curr user schedule
    if form.validate_on_submit():
        # create request
        old_price = rqst.get_price()
        old_date = rqst.date_requested
        rqst.date_requested = form.date_requested.data
        if old_date != form.date_requested.data:
            rqst.base_price = calc_base_price(
                shift.id, form.date_requested.data.strftime('%Y-%m-%d'))['price']

        db.session.add(rqst)
        current_user.balance += old_price - rqst.get_price()
        session['credits'] = current_user.balance
        db.session.commit()
        flash("The request has been updated.")
        return redirect(url_for('main.dashboard'))
    else:
        print(form.errors)

    form.date_requested.data = rqst.date_requested.date()

    return render_template('requests/edit_request.html', form=form, shiftid=shift.id, shifts=current_user.schedule, base=rqst.base_price, day=shift.day)
# ----------------------------------------------------------------------


@ requests.route("/request/<requestid>/sub", methods=['POST', 'GET'])
@ login_required
def sub_request(requestid):
    """
    Deletes the request from the dashboard and assigns it to the
    current user.
    """
    rqst = Request.query.filter_by(id=requestid).first()
    if rqst.posted() == current_user:
        flash("Cannot accept your own request")
        return redirect(url_for('main.dashboard'))

    if rqst.accepted:
        flash("Request already accepted")
        return redirect(url_for('main.dashboard'))

    rqst.accepted = True
    rqst.accepted_by.append(current_user)
    rqst.date_accepted = datetime.today()
    current_user.balance += rqst.get_price()
    session['credits'] = current_user.balance
    db.session.commit()
    return redirect(url_for('main.profile'))
# ----------------------------------------------------------------------


@ requests.route("/request/<requestid>/swap", methods=['POST', 'GET'])
@ login_required
def swap_request(requestid):
    """
    Swaps the request with the selected shift and date. Deletes the
    original request. Creates a new request with the selected date and
    shift. Credits are not deducted from the user.
    """
    # check if it's not the current user
    rqst = Request.query.filter_by(id=requestid).first()
    if rqst.posted() == current_user:
        flash("Cannot accept your own request")
        return redirect(url_for('main.dashboard'))

    if rqst.accepted:
        flash("Request already accepted")
        return redirect(url_for('main.dashboard'))

    # mark as accepted
    rqst.accepted = True
    rqst.accepted_by.append(current_user)
    rqst.date_accepted = datetime.today()

    # create new request for the swap shift
    shift_data = request.args.get("swap_shift_data")
    idx, date = process_shift_str(shift_data)
    swap_shift = Shift.query.filter_by(id=idx).first()
    price = calc_base_price(idx, date)['price']
    new_swap_request = Request(
        date_requested=date, base_price=price, subsidy=price-rqst.base_price
    )
    new_swap_request.shift.append(swap_shift)
    new_swap_request.posted_by.append(current_user)
    db.session.add(new_swap_request)
    db.session.commit()
    flash("Request successfully accepted.")
    return redirect(url_for('main.dashboard'))
# ----------------------------------------------------------------------


@ requests.route("/request/<requestid>/delete", methods=['POST', 'GET'])
@ login_required
def delete_request(requestid):
    """
    Deletes the request and refunds the credits.
    """
    rqst = Request.query.filter_by(id=requestid).first()
    if rqst.posted() == current_user:
        if rqst.accepted:
            flash("Cannot delete accepted request")
            return redirect(url_for('main.dashboard'))
        db.session.delete(rqst)
        current_user.balance += rqst.get_price()
        session['credits'] = current_user.balance
        db.session.commit()
    else:
        flash("Unauthorized user.")
    return redirect(url_for('main.dashboard'))
# ----------------------------------------------------------------------


@requests.route("/swap_shifts/<requestid>", methods=['POST', 'GET'])
@login_required
def swap_shifts(requestid):
    """
    Called by JS when user tries to Swap with an existing request.
    Returns a list of their own shifts that can be swapped with
    the selected request.
    """
    rqst = Request.query.filter_by(id=requestid).first()
    res = get_swap_options(rqst.date_requested, rqst.get_course())
    return jsonify({'swap_shifts': res})
# ----------------------------------------------------------------------


@requests.route("/calculate_base_price")
@login_required
def calculate_base_price():
    """
    Calculates price of the request based on the pricing scheme and the
    details of the request. Called by JS when user enters the date of
    the new request.
    """
    shiftid = request.args.get('shiftid')
    date = request.args.get('date')
    res = 0
    if PRICING_ALG == "default":
        res = calc_base_price(int(shiftid), date)
    else:
        # generate request for pricing alg
        pass

    return jsonify(res)
# ----------------------------------------------------------------------


@requests.route("/requests/is_duplicate")
@login_required
def is_duplicate():
    """
    Checks if the new request being created is duplicate. Called by
    JavaScript when user enters the date for their request.
    """
    shiftid = request.args.get('shiftid')
    shift = Shift.query.filter_by(id=shiftid).first()
    date = datetime.strptime(
        request.args.get('date'), '%Y-%m-%d')
    rqst = {
        "posted_by": current_user,
        "shift": shift,
        "date_requested": date
    }
    res = {'duplicate': current_user.is_request_duplicate(rqst)}

    return jsonify(res)

# ----------------------------------------------------------------------
# Error handling
# ----------------------------------------------------------------------


@requests.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html', error=error), 404
# ----------------------------------------------------------------------


@requests.app_errorhandler(Exception)
@requests.app_errorhandler(500)
def internal_error(error):
    return render_template('500.html', error=error), 500
# ----------------------------------------------------------------------


@requests.app_errorhandler(403)
def forbidden_error(error):
    return render_template('403.html', error=error), 403
# ----------------------------------------------------------------------
