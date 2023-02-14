from flask import Blueprint, redirect, url_for, render_template
from flask_login import login_required
from subapp.models import Shift, Role, User
from subapp.admin.forms import AddScheduleForm, AddUserForm
from subapp.admin.util import admin_required, save_files
from subapp.admin.scheduler import update_schedule
from subapp import db
from config import ICO

admin = Blueprint('admin', __name__,
                  template_folder='templates',
                  static_folder='static',
                  static_url_path='/admin/static/')

# admin dashboard


@admin.route("/admin_dashboard", methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():
    schedule_form = AddScheduleForm()

    # user form options
    shift_choices = [(str(shift.id), shift.formatted())
              for shift in Shift.query.all()]
    role_choices = [(str(role.id), role.name) for role in Role.query.all()]
    user_form = AddUserForm()

    user_form.roles.choices = role_choices
    user_form.shifts.choices = shift_choices

    return render_template('admin/dashboard.html', user_form=user_form, schedule_form=schedule_form)


# add schedule
@admin.route("/add_schedule", methods=['POST'])
@login_required
@admin_required
def add_schedule():
    schedule_form = AddScheduleForm()

    # user form options
    shift_choices = [(str(shift.id), shift.formatted())
              for shift in Shift.query.all()]
    role_choices = [(str(role.id), role.name) for role in Role.query.all()]
    user_form = AddUserForm()

    user_form.roles.choices = role_choices
    user_form.shifts.choices = shift_choices

    if schedule_form.validate_on_submit():
        cos226 = schedule_form.cos226.data
        cos126 = schedule_form.cos126.data
        save_files(cos226, cos126)
        update_schedule()
        return redirect(url_for('main.dashboard'))

    return render_template('admin/dashboard.html', user_form=user_form, schedule_form=schedule_form)

# add/edit user


@admin.route("/add_user", methods=['POST'])
@login_required
@admin_required
def add_user():
    schedule_form = AddScheduleForm()

    # user form options
    shift_choices = [(str(shift.id), shift.formatted())
                     for shift in Shift.query.all()]
    role_choices = [(str(role.id), role.name) for role in Role.query.all()]
    user_form = AddUserForm()

    user_form.roles.choices = role_choices
    user_form.shifts.choices = shift_choices

    if user_form.validate_on_submit():
        user = User.query.filter_by(netid=user_form.netid.data)
        shifts = []
        for ident in user_form.shifts.data:
            shifts.apend(Shift.query.filter(Shift.id == int(ident)).first())

        if user:
            user.schedule.extend(shifts)
            user.role = user_form.role.data
        else:
            user = User(netid=user_form.netid.data,
                        role=user_form.role.data, balance=ICO)
            user.schedule.extend(shifts)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.dashboard'))

    return render_template('admin/dashboard.html', user_form=user_form, schedule_form=schedule_form)
