from flask import redirect, url_for, render_template, request
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
                new_request.popsted_by.append(current_user)
                request.swap_requests.append(new_request)

        db.session.commit()

        return redirect(url_for('main.dashboard'))

    return render_template('requests/create_request.html', form=form, shiftid=int(shiftid), shifts=current_user.schedule)


@ requests.route("/request/<requestid>/sub", methods=['POST', 'GET'])
@ login_required
def sub_request(requestid):
    request = Request.query.filter_by(id=requestid).first()
    request.accepted = True
    request.accepted_by.append(current_user)
    db.session.commit()
    return redirect(url_for('main.profile'))


@ requests.route("/request/<requestid>/delete", methods=['POST', 'GET'])
@ login_required
def delete_request(requestid):
    request = Request.query.filter_by(id=requestid).first()
    db.session.delete(request)
    db.session.commit()
    return redirect(url_for('main.dashboard'))


@requests.route("/swap_shifts/<shiftid>/<request_date>")
@login_required
def swap_shifts(shiftid, request_date):
    all_shifts = Shift.query.all()
    request_date = datetime.strptime(request_date, "%m/%d/%Y")
    num_days = date - date.today()
    dates = [request_date - timedelta(days=x)
             for x in range(num_days.days)]
    dates += [request_date + timedelta(days=x)
              for x in range(10 - num_days.days)]

    swap_shift_list = [(x.id, x.formatted() + )
                       for x in all_shifts if x not in current_user.schedule]
