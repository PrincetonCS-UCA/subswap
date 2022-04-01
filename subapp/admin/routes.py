from flask import Blueprint, redirect, url_for, render_template, flash, request
from subapp.admin.forms import AddScheduleForm
from subapp.admin.util import login_required, save_files
from subapp.admin.scheduler import update_schedule

admin = Blueprint('admin', __name__,
                 template_folder='templates',
                 static_folder='static',
                 static_url_path='/admin/static/')


# add schedule
@admin.route("/add_schedule", methods=['GET', 'POST'])
@login_required(role="Admin")
def add_schedule():
    form = AddScheduleForm()
    if form.validate_on_submit():
        cos226 = form.cos226.data
        cos126 = form.cos126.data
        save_files(cos226, cos126)
        update_schedule()
        print("Schedule updated")
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/add_schedule.html', form=form)