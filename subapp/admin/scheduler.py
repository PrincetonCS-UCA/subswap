import os
from flask import current_app
import pandas as pd
from datetime import time
from subapp.models import User, Shift
from subapp import db


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


def create_users(staff, course, sub):
    res = []
    for person in staff:
        user = User.query.filter_by(netid=person).first()
        if user is None:
            new_user = User(netid=person, balance=500, role=course, sub=sub)
            db.session.add(new_user)
            db.session.commit()
            res.append(new_user)
        else:
            res.append(user)
    return res


def assign_shifts(df, course):
    i = 0
    for key, value in df.iteritems():

        # value is list of users
        value = list(value)
        value = [x for x in value if pd.notnull(x)]

        # all columns execpt subs. create shift and user and create relatioship
        if i < len(df.columns) - 1:
            i += 1
            shift = create_shift(key, course)
            users = create_users(value, course, False)
            shift.staff.extend(users)
            db.session.commit()
        else:
            # subs
            _ = create_users(value, course, True)


def update_schedule():
    # get csv files
    cos226_path = os.path.join(
        current_app.root_path, 'admin/static/files/cos226.csv')
    cos126_path = os.path.join(
        current_app.root_path, 'admin/static/files/cos126.csv')
    cos226 = pd.read_csv(cos226_path)
    cos126 = pd.read_csv(cos126_path)

    db.drop_all()
    db.create_all()

    # asign shifts to users
    assign_shifts(cos226, 'COS226/217')
    assign_shifts(cos126, 'COS126')

    return True
