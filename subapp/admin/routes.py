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
        clear_db = form.clear_db.data
        if files:
            save_files(files)
            paths = {name: os.path.join(
                current_app.root_path, f'admin/static/files/{name}.csv') for name in files.keys()}
            update_schedule(paths, clear_db)
            print("Schedule updated")
        else:
            print('No files found.')
            paths = {'COS2xx': os.path.join(
                current_app.root_path, f'admin/static/files/cos2xx.csv'),
                'COS126': os.path.join(
                current_app.root_path, f'admin/static/files/cos126.csv')}
            print("paths:")
            print(paths)
            update_schedule(paths, clear_db)
            print("Schedule updated")
        return redirect(url_for('main.dashboard'))

    return render_template('admin/add_schedule.html', form=form)


@admin.route("/clear_db", methods=['GET', 'POST'])
@login_required
@admin_required
def clear_db():
    print("Starting clear.")
    db.drop_all()
    print("Dropped tables.")
    db.create_all()
    print("Created new ones.")
    Role.insert_roles()
    print("inserted roles")
    return redirect(url_for('main.dashboard'))
