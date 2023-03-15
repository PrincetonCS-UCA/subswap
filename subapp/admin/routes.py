from flask import Blueprint, redirect, url_for, render_template, current_app
from flask_login import login_required
import os
from subapp.admin.forms import AddScheduleForm
from subapp.admin.util import admin_required, save_files
from subapp.admin.scheduler import update_schedule
from subapp.models import Role
from subapp import db

admin = Blueprint('admin', __name__,
                  template_folder='templates',
                  static_folder='static',
                  static_url_path='/admin/static/')


# add schedule
@admin.route("/add_schedule", methods=['GET', 'POST'])
@login_required
@admin_required
def add_schedule():
    form = AddScheduleForm()
    if form.validate_on_submit():
        files = {k: v for k, v in form.data.items() if k.startswith('COS') and v}
        if files:
            save_files(files)
            paths = {name: os.path.join(
                current_app.root_path, f'admin/static/files/{name}.csv') for name in files.keys()}
            update_schedule(paths)
            print("Schedule updated")
        else:
            print("Files not found.")
        return redirect(url_for('main.dashboard'))

    return render_template('admin/add_schedule.html', form=form)
