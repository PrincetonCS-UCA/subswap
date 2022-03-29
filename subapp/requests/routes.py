from flask import redirect, url_for, render_template
from flask.blueprints import Blueprint
from subapp.models import Request, Shift
from subapp.requests.forms import RequestForm
from subapp import db
from flask_login import login_required, current_user

requests = Blueprint('requests', __name__,
                 template_folder='templates',
                 static_folder='static',
                 static_url_path='/requests/static/')

@requests.route("/shift/<shiftid>/request", methods=['POST','GET'])
@login_required
def create_request(shiftid):
    shift = Shift.query.filter_by(id=shiftid).first()
    shifts = current_user.schedule
   
    form = RequestForm()
    
    if form.validate_on_submit():
        # create request
        request = Request(swap=bool(form.isSwap.data), date_requested=form.date_requested.data, base_price=0, bonus=form.bonus.data)
        db.session.add(request)
        request.shift.append(shift)
        request.posted_by.append(current_user)
        db.session.commit()

        return redirect(url_for('main.dashboard'))
    else:
        print(form.errors)
    return render_template('requests/create_request.html', form=form, shiftid=int(shiftid), shifts=shifts)

@requests.route("/request/<requestid>/sub", methods=['POST','GET'])
@login_required
def sub_request(requestid):
    request = Request.query.filter_by(id=requestid).first()
    request.accepted = True
    request.accepted_by.append(current_user)
    db.session.commit()
    return redirect(url_for('main.profile'))

@requests.route("/request/<requestid>/delete", methods=['POST','GET'])
@login_required
def delete_request(requestid):
    request = Request.query.filter_by(id=requestid).first()
    db.session.delete(request)
    db.session.commit()
    return redirect(url_for('main.dashboard'))