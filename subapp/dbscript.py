from flask import current_app
from subapp import db
from subapp.models import User, Shift, Request, Role
from subapp.requests.util import calc_base_price
from datetime import time, timedelta, datetime, date
import random
from config import COURSES
# --------------------------------------------------------------------


def create_dummy_data(all=False,
                      reset=False,
                      users=False,
                      requests=False,
                      shifts=False,
                      ushifts=False,
                      rshifts=False,
                      urequests=False,
                      roles=False):
    if all or reset:
        reset_db()
    if all or roles:
        Role.insert_roles()
    if all or users:
        create_users()
    if all or shifts:
        create_shifts()
    if all or requests:
        create_requests()
    if all or ushifts:
        user_shifts()
    if all or urequests:
        user_requests()
    if all or rshifts:
        request_shifts()

    current_app.logger.info("Database initialized with dummy data.")
    print("Dummy data created.")

# --------------------------------------------------------------------
# reset db


def reset_db():
    db.drop_all()
    db.create_all()
    print("Database reset.")

# create dummy users


def create_users():
    users = []
    cos126 = Role.query.filter_by(name='COS126').first()
    cos2xx = Role.query.filter_by(name='COS2xx').first()
    admin = Role.query.filter_by(name='ADMIN').first()
    users.append(User(netid='mmir', balance=1000, role=admin))
    users.append(User(netid='lumbroso', balance=1000, role=admin))
    users.append(User(netid='ramadan', balance=1000, role=cos2xx))
    users.append(User(netid='atli', balance=1000, role=cos126))
    users.append(User(netid='de12', balance=1000, role=cos2xx))
    users.append(User(netid='josephlou', balance=1000, role=cos2xx))
    users.append(User(netid='lanceg', balance=1000, role=cos126))
    users.append(User(netid='ffakhro', balance=1000, role=cos2xx))

    for i, user in enumerate(users):
        db.session.add(user)

    db.session.commit()

    print(f"Added {len(User.query.all())} users")
# --------------------------------------------------------------------

# create dummy requests
def create_requests():
    dates = {}
    weekdays = {1: "Monday",
                2: "Tuesday",
                3: "Wednesday",
                4: "Thursday",
                5: "Friday",
                6: "Saturday",
                7: "Sunday"}

    start_date = date.today()
    end_date = start_date + timedelta(days=30)

    while start_date != end_date:
        if weekdays[start_date.isoweekday()] not in dates:
            dates[weekdays[start_date.isoweekday()]] = [
                start_date]
        else:
            dates[weekdays[start_date.isoweekday()]].append(start_date)
        start_date += timedelta(days=1)

    finalDates = random.sample(sum(dates.values(), []), 30)

    requests = []
    for i in range(30):
        requests.append(Request(date_requested=random.choice(finalDates),
                                base_price=0,
                                accepted=random.choice([True]*5 + [False]*15),
                                bonus=random.randint(5, 50)))

    for request in requests:
        db.session.add(request)

    db.session.commit()
    print(f"Added {len(Request.query.all())} requests")

# --------------------------------------------------------------------

# create dummy shifts


def create_shifts():
    def dummy_enddate(created_date):
        dt = datetime.combine(date.today(), created_date) + timedelta(hours=2)
        return dt.time()

    days = ['Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday']

    start1 = time(15, 00)
    end1 = dummy_enddate(start1)
    start2 = time(17, 00)
    end2 = dummy_enddate(start2)
    start3 = time(18, 00)
    end3 = dummy_enddate(start3)
    start4 = time(21, 00)
    end4 = dummy_enddate(start4)
    start5 = time(15, 30)
    end5 = dummy_enddate(start5)
    start6 = time(19, 00)
    end6 = dummy_enddate(start6)

    shifts = []
    shifts.append(Shift(day=random.choice(days), start=start1,
                  end=end1, course=random.choice(COURSES)))
    shifts.append(Shift(day=random.choice(days), start=start2,
                  end=end2, course=random.choice(COURSES)))
    shifts.append(Shift(day=random.choice(days), start=start3,
                  end=end3, course=random.choice(COURSES)))
    shifts.append(Shift(day=random.choice(days), start=start4,
                  end=end4, course=random.choice(COURSES)))
    shifts.append(Shift(day=random.choice(days), start=start5,
                  end=end5, course=random.choice(COURSES)))
    shifts.append(Shift(day=random.choice(days), start=start6,
                  end=end6, course=random.choice(COURSES)))

    for shift in shifts:
        db.session.add(shift)

    db.session.commit()

    print(f"Added {len(Shift.query.all())} shifts.")

# --------------------------------------------------------------------

# create associations


def user_requests():
    """
    Posted requests and accepted requests.
    """
    users = User.query.all()
    requests = Request.query.all()
    for request in requests:
        duo = random.sample(users, 2)
        request.posted_by.append(duo[0])
        if request.accepted:
            request.accepted_by.append(duo[1])

    db.session.commit()
    print("Created User-Request relationships")


def user_shifts():
    """
    3. Shifts - User staffed filter_by
    """
    users = User.query.all()
    shifts = Shift.query.all()
    cos126 = Shift.query.filter_by(course="COS126").all()
    cos226 = Shift.query.filter_by(course="COS2xx").all()

    for i, user in enumerate(users):
        if i <= 1:
            user.schedule.extend(cos126[:2])
            user.schedule.extend(cos226[:2])

        elif i > 3:
            x = random.sample(shifts, 2)
            user.schedule.append(x[0])
            user.schedule.append(x[1])
        else:
            user.schedule.append(random.choice(shifts))
    print("Created User-Shift relationships")
    db.session.commit()

# 4. Requests - shifts


def request_shifts():
    requests = Request.query.all()
    for request in requests:
        request.shift.append(random.choice(request.posted().schedule))
        request.base_price = calc_base_price(
            request.shift[0].id, startdate=request.date_requested, ignore=True)

    db.session.commit()
    print("Created Request-Shift relationships")
