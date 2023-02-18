from flask import Blueprint, redirect, url_for, render_template, current_app
from flask_login import login_required
import os
from subapp.admin.forms import AddScheduleForm
from subapp.admin.util import admin_required, save_files
from subapp.admin.scheduler import update_schedule

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
        files = {k: v for k, v in form.data.items() if k.startswith('cos') and v}
        clear_db = form.clear_db.data
        if files:
            save_files(files)
            paths = {name: os.path.join(
                current_app.root_path, f'admin/static/files/{name}.csv') for name in files.keys()}
            update_schedule(paths, clear_db)
            print("Schedule updated")
        else:
            print('No files found.')
        return redirect(url_for('main.dashboard'))

    return render_template('admin/add_schedule.html', form=form)
