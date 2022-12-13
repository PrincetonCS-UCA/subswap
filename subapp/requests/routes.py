from flask import (redirect, url_for, render_template,
                   request, jsonify, flash, session, current_app)
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from datetime import datetime

from subapp.models import Request, Shift
from subapp.requests.forms import RequestForm
from subapp import db
from subapp.requests.util import (
    get_swap_options, process_shift_str, calc_base_price)
from config import PRICING_ALG
import requests

requests = Blueprint('requests', __name__,
                     template_folder='templates',
                     static_folder='static',
                     static_url_path='/requests/static/')


@requests.route("/shift/<shiftid>/request", methods=['POST', 'GET'])
@login_required
def create_request(shiftid):
    # shift requested
    shift = Shift.query.filter_by(id=shiftid).first()

    form = RequestForm()

    # shifts in curr user schedule
    if form.validate_on_submit():
        # create request
        new_request = Request(
            date_requested=form.date_requested.data,
            base_price=calc_base_price(
                shift.id, form.date_requested.data.strftime('%Y-%m-%d'))['price'],
            bonus=form.bonus.data)

        new_request.shift.append(shift)
        new_request.posted_by.append(current_user)

        db.session.add(new_request)
        current_user.balance -= new_request.get_price()
        session['credits'] = current_user.balance
        db.session.commit()

        return redirect(url_for('main.dashboard'))
    else:
        current_app.logger.error("Request form", form.errors)
        print(form.errors)

    return render_template('requests/create_request.html', form=form, shiftid=int(shiftid), shifts=current_user.schedule, day=shift.day)


@requests.route("/request/<requestid>/edit", methods=['POST', 'GET'])
@login_required
def edit_request(requestid):
    # shift requested
    rqst = Request.query.filter_by(id=requestid).first()
    if current_user != rqst.posted():
        # abort(403)
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
        rqst.bonus = form.bonus.data

        db.session.add(rqst)
        current_user.balance += old_price - rqst.get_price()
        session['credits'] = current_user.balance
        db.session.commit()
        flash("The request has been updated.")
        return redirect(url_for('main.dashboard'))
    else:
        print(form.errors)

    form.date_requested.data = rqst.date_requested.date()
    form.bonus.data = rqst.bonus

    return render_template('requests/edit_request.html', form=form, shiftid=shift.id, shifts=current_user.schedule, base=rqst.base_price, day=shift.day)


@ requests.route("/request/<requestid>/sub", methods=['POST', 'GET'])
@ login_required
def sub_request(requestid):
    rqst = Request.query.filter_by(id=requestid).first()
    if rqst.posted() == current_user:
        flash("Cannot accept your own request")
        return redirect(url_for('main.dashboard'))
    rqst.accepted = True
    rqst.accepted_by.append(current_user)
    rqst.date_accepted = datetime.today()
    current_user.balance += rqst.get_price()
    session['credits'] = current_user.balance
    db.session.commit()
    return redirect(url_for('main.profile'))


@ requests.route("/request/<requestid>/swap", methods=['POST', 'GET'])
@ login_required
def swap_request(requestid):
    # check if it's not the current user
    rqst = Request.query.filter_by(id=requestid).first()
    if rqst.posted() == current_user:
        flash("Cannot accept your own request")
        return redirect(url_for('main.dashboard'))

    # mark as accepted
    rqst.accepted = True
    rqst.accepted_by.append(current_user)
    rqst.date_accepted = datetime.today()
    print("Swap request accepted.")

    # create new request for the swap shift
    shift_data = request.args.get("swap_shift_data")
    print(f"Processing {shift_data}")
    idx, date = process_shift_str(shift_data)
    swap_shift = Shift.query.filter_by(id=idx).first()
    price = calc_base_price(idx, date)
    price = price['price']
    print(f"Price of new shift is {price}. Old is {rqst.get_price()}")
    new_swap_request = Request(
        date_requested=date, base_price=price, bonus=0, subsidy=price-rqst.base_price
    )
    new_swap_request.shift.append(swap_shift)
    new_swap_request.posted_by.append(current_user)
    db.session.add(new_swap_request)
    db.session.commit()
    flash("Request successfully accepted.")
    return redirect(url_for('main.dashboard'))


@ requests.route("/request/<requestid>/delete", methods=['POST', 'GET'])
@ login_required
def delete_request(requestid):
    rqst = Request.query.filter_by(id=requestid).first()
    if rqst.posted() == current_user:
        db.session.delete(rqst)
        current_user.balance += rqst.get_price()
        session['credits'] = current_user.balance
        db.session.commit()
    else:
        flash("Unauthorized user.")
    return redirect(url_for('main.dashboard'))


@requests.route("/swap_shifts/<requestid>")
@login_required
def swap_shifts(requestid):
    rqst = Request.query.filter_by(id=requestid).first()
    res = get_swap_options(rqst.date_requested)
    print(res)
    return jsonify({'swap_shifts': res})


@requests.route("/calculate_base_price")
@login_required
def calculate_base_price():
    shiftid = request.args.get('shiftid')
    date = request.args.get('date')
    res = 0
    if PRICING_ALG == "default":
        res = calc_base_price(int(shiftid), date)
    else:
        res = requests.get(PRICING_ALG)

    return jsonify(res)
