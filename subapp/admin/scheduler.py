from datetime import time
import pandas as pd
from flask import session
from config import ICO, ADMINS
from subapp import db
from subapp.models import User, Shift, Role, Request
# ----------------------------------------------------------------------


def create_shift(shift, course):
    """
    Creates and adds shift objects to the database.
    """
    days = {
        'Mon': 'Monday',
        'Tues': 'Tuesday',
        'Wed': 'Wednesday',
        'Thurs': 'Thursday',
        'Fri': 'Friday',
        'Sat': 'Saturday',
        'Sun': 'Sunday'
    }

    x = shift.split()
    time_obj = x[1].split("-")
    day = days[x[0]]
    start_time = time(int(time_obj[0])+12)
    end_time = time(int(time_obj[1])+12)

    new_shift = Shift(day=day, start=start_time, end=end_time, course=course)
    db.session.add(new_shift)
    db.session.commit()
    return new_shift
# ----------------------------------------------------------------------


def create_users(staff, course, created_users):
    """
    Creates and adds users to the database. Assigns roles based on the
    course variable as well as allocates initial credits.
    """
    res = []
    for person in staff:
        user = User.query.filter_by(netid=person).first()
        r = Role.query.filter_by(
            name='Admin').first() if person in ADMINS else Role.query.filter_by(name=course).first()
        if user is None:
            this_user = User(netid=person, balance=ICO, role=r)
            db.session.add(this_user)
            created_users.add(person)
        elif person not in created_users:
            this_user = user
            this_user.balance += ICO
        else:
            this_user = user

        db.session.commit()
        session['credits'] = this_user.balance
        res.append(this_user)

    return res
# ----------------------------------------------------------------------


def assign_shifts(df, course, created_users):
    """
    Creates relationships between shifts and users (after calling the
    respective functions to create them).
    """
    from subapp import create_app

    app = create_app()
    with app.app_context():
        i = 0
        for key, value in df.items():

            # value is list of users
            value = list(value)
            value = [x for x in value if pd.notnull(x)]

            # all columns execpt subs. create shift, assign users to that shift
            if i < len(df.columns) - 1:
                i += 1
                shift = create_shift(key, course)
                users = create_users(value, course, created_users)
                shift.staff.extend(users)
                db.session.commit()
            else:
                # subs
                _ = create_users(value, course + '-sub', created_users)
        print(f"Added {course}")
# ----------------------------------------------------------------------


def update_schedule(files):
    """
    Deletes existing requests and shifts from the database. Reads saved
    csv files and calls assign shifts.
    """
    reqs = Request.query.all()
    shifts = Shift.query.all()
    [db.session.delete(rq) for rq in reqs]
    [db.session.delete(shift) for shift in shifts]
    db.session.commit()
    created_users = set()
    for name, path in files.items():
        df = pd.read_csv(path)
        assign_shifts(df, name, created_users)

    return True
# ----------------------------------------------------------------------
