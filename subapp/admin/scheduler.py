import os
from flask import session
import pandas as pd
from datetime import time
from threading import Thread
from subapp.models import User, Shift, Role, Request
from subapp import db
from config import ICO, ADMINS


def create_shift(shift, course):
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


def create_users(staff, course):
    res = []
    for person in staff:
        user = User.query.filter_by(netid=person).first()
        r = Role.query.filter_by(
            name='Admin').first() if person in ADMINS else Role.query.filter_by(name=course).first()
        if user is None:
            this_user = User(netid=person, balance=ICO, role=r)
            db.session.add(this_user)
        else:
            this_user = user
            this_user.balance += ICO

        db.session.commit()
        session['credits'] = this_user.balance
        res.append(this_user)

    return res


def assign_shifts(df, course):
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
                users = create_users(value, course)
                shift.staff.extend(users)
                db.session.commit()
            else:
                # subs
                _ = create_users(value, course + '-sub')
        print(f"Added {course}")


def update_schedule(files):
    reqs = Request.query.all()
    shifts = Shift.query.all()
    [db.session.query(rq).delete() for rq in reqs]
    [db.session.query(shift).delete() for shift in shifts]
    for name, path in files.items():
        df = pd.read_csv(path)
        db.session.commit()
        assign_shifts(df, name)

    return True
