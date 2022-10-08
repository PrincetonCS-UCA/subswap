from flask import redirect, url_for, render_template, request
from flask.blueprints import Blueprint
from subapp.models import Request, Shift
from subapp.requests.forms import RequestForm
from subapp import db
from flask_login import login_required, current_user

requests = Blueprint('requests', __name__,
                     template_folder='templates',
                     static_folder='static',
                     static_url_path='/requests/static/')


@requests.route("/shift/<shiftid>/request", methods=['POST', 'GET'])
@login_required
def create_request(shiftid):
    shift = Shift.query.filter_by(id=shiftid).first()
    shifts = current_user.schedule
    all_shifts = Shift.query.all()
    swappable_shifts = [x for x in all_shifts if x not in shifts]

    form = RequestForm()

    for shift in swappable_shifts:
        some_id = uuid.uuid1()
        select_entry = SwapDateForm()
        # each SwapDateForm() unique
        select_entry.shift.name = f"select_entry-{some_id}"
        select_entry.shift.label = f"{shift.day}, {shift.start} - {shift.end}"
        select_entry.shift.choices = [(x.id, x.start)
                                      for x in swappable_shifts]
        form.shifts.append(select_entry)

    if form.validate_on_submit():
        # create request
        request = Request(swap=bool(
            form.isSwap.data),
            date_requested=form.date_requested.data,
            base_price=0,
            bonus=form.bonus.data)

        db.session.add(request)
        request.shift.append(shift)
        request.posted_by.append(current_user)

        # relating with swappable requests
        for swap_shift in form.swaps.data:
            new_request = Request(
                swap=False, date_requested=swap_shift.date, base_price=0, bonus=0)
            new_request.popsted_by.append(current_user)
            request.swap_requests.append(new_request)

        db.session.commit()

        return redirect(url_for('main.dashboard'))
    else:
        print(form.errors)
    return render_template('requests/create_request.html', form=form, shiftid=int(shiftid), shifts=shifts)


@requests.route("/request/<requestid>/sub", methods=['POST', 'GET'])
@login_required
def sub_request(requestid):
    request = Request.query.filter_by(id=requestid).first()
    request.accepted = True
    request.accepted_by.append(current_user)
    db.session.commit()
    return redirect(url_for('main.profile'))


@requests.route("/request/<requestid>/delete", methods=['POST', 'GET'])
@login_required
def delete_request(requestid):
    request = Request.query.filter_by(id=requestid).first()
    db.session.delete(request)
    db.session.commit()
    return redirect(url_for('main.dashboard'))
