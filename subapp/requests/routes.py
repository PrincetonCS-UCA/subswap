from flask import redirect, url_for, render_template, request, jsonify
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from datetime import time, timedelta, datetime, date

from subapp.models import Request, Shift
from subapp.requests.forms import RequestForm
from subapp import db

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
    form.swaps.choices = [(1, 'dummy'), (1, 'dummyyyy')]

    # shifts in curr user schedule
    all_shifts = Shift.query.all()

    if form.validate_on_submit():
        # create request
        new_request = Request(swap=bool(
            form.isSwap.data),
            date_requested=form.date_requested.data,
            base_price=0,
            bonus=form.bonus.data)

        db.session.add(new_request)
        new_request.shift.append(shift)
        new_request.posted_by.append(current_user)

        # relating with swappable requests
        for shift in all_shifts:
            if shift.id in form.swaps.data:
                new_request = Request(
                    swap=False, date_requested=shift.date, base_price=0, bonus=0)
                new_request.posted_by.append(current_user)
                request.swap_requests.append(new_request)

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
    request_date = datetime.strptime(
        startdate, '%Y-%m-%d')
    num_days = request_date - \
        datetime.combine(date.today(), datetime.min.time())
    dates = [request_date - timedelta(days=x)
             for x in range(1, num_days.days)]
    dates += [request_date + timedelta(days=x)
              for x in range(10 - num_days.days)]
    dates.sort()

    # we have a list of dates
    # need to query by role
    all_shifts = Shift.query.filter_by()
    day_shifts = {}

    for shift in all_shifts:
        if shift not in current_user.schedule:
            if shift.day not in day_shifts:
                day_shifts[shift.day] = [shift]
            else:
                day_shifts[shift.day].append(shift)

    swap_shift_list = []

    # add shifts to each day
    for x in dates:
        # get shifts for that day
        if x.strftime('%A') in day_shifts:
            for shift in day_shifts[x.strftime('%A')]:
                swap_shift_list.append(
                    [shift.id, shift.formatted() + ", " + x.strftime("%m-%d-%Y")])

    return jsonify({'swap_shifts': swap_shift_list})
