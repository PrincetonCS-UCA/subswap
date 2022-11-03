from flask import redirect, url_for, render_template, request, jsonify
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from datetime import time, timedelta, datetime, date

from subapp.models import Request, Shift
from subapp.requests.forms import RequestForm
from subapp import db
from subapp.requests.util import get_swap_options, process_shift_str

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
    all_shifts = Shift.query.all()
    form.swaps.choices = [(x.id, x.formatted()) for x in all_shifts]

    # shifts in curr user schedule
    if request.method == 'POST':
        # if swap then update form choices
        if form.isSwap.data:
            choices = []
            for shift_data in form.swaps.data:
                idx, curr_shift = process_shift_str(shift_data)
                choices.append((shift_data, shift_data))
            form.swaps.choices = choices
            print("LOOK: ", form.swaps.choices)

        if form.validate_on_submit():
            # create request
            new_request = Request(swap=bool(
                form.isSwap.data),
                date_requested=form.date_requested.data,
                base_price=0,
                bonus=form.bonus.data)

            new_request.shift.append(shift)
            new_request.posted_by.append(current_user)

            # relating with swappable requests
            for shift_data in form.swaps.data:
                idx, date = process_shift_str(shift_data)
                swap_shift = Shift.query.filter_by(id=idx).first()
                new_swap_request = Request(
                    swap=False, date_requested=date, base_price=0, bonus=0, is_possible_swap=True)
                new_swap_request.posted_by.append(current_user)
                db.session.add(new_swap_request)
                new_request.swap_requests.append(new_swap_request)

            db.session.add(new_request)
            db.session.commit()

            return redirect(url_for('main.dashboard'))
        else:
            print(form.errors)

    return render_template('requests/create_request.html', form=form, shiftid=int(shiftid), shifts=current_user.schedule)


@ requests.route("/request/<requestid>/sub", methods=['POST', 'GET'])
@ login_required
def sub_request(requestid):
    rqst = Request.query.filter_by(id=requestid).first()
    rqst.accepted = True
    rqst.accepted_by.append(current_user)
    db.session.commit()
    return redirect(url_for('main.profile'))


@ requests.route("/request/<requestid>/delete", methods=['POST', 'GET'])
@ login_required
def delete_request(requestid):
    rqst = Request.query.filter_by(id=requestid).first()
    db.session.delete(rqst)
    db.session.commit()
    return redirect(url_for('main.dashboard'))


@requests.route("/swap_shifts/<startdate>")
@login_required
def swap_shifts(startdate):
    res = get_swap_options(startdate)
    return jsonify({'swap_shifts': res})
