from subapp import db
from subapp.models import User, Shift, Request
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
                      swaprequests=False):
    if all or reset:
        reset_db()
    if all or users:
        create_users()
    if all or requests:
        create_requests()
    if all or shifts:
        create_shifts()
    if all or ushifts:
        user_shifts()
    if all or urequests:
        user_requests()
    if all or rshifts:
        request_shifts()
    # if all or swaprequests:
    #     swap_requests()
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
    users.append(User(netid='mmir', balance=1000, role='Admin'))
    users.append(User(netid='tak', balance=50))
    users.append(User(netid='ffakhro', balance=150))
    users.append(User(netid='ali', balance=250))
    users.append(User(netid='rehma', balance=450))
    users.append(User(netid='vini', balance=500))
    users.append(User(netid='lumbroso', balance=1000, role='Admin'))

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

    finalDates = random.sample(sum(dates.values(), []), 10)

    requests = []
    for i in range(20):
        requests.append(Request(swap=random.choice([True, False]),
                                date_requested=finalDates[i],
                                base_price=random.randint(5, 30),
                                accepted=random.choice([True]*10 + [False]*5),
                                bonus=random.randint(0, 15)))

    for request in requests:
        db.session.add(request)

    db.session.commit()
    print(f"Added {len(Request.query.all())} requests")

# --------------------------------------------------------------------

# create dummy shifts


def create_shifts():
    def dummy_enddate(created_date):
        dt = datetime.combine(date.today(), created_date) + timedelta(hours=3)
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
    subs = User.query.all()
    nonsubs = User.query.all()[:3]
    requests = Request.query.all()
    for i, request in enumerate(requests):
        if i < 3:
            request.accepted_by.append(random.choice(subs))
        if i < 2:
            request.posted_by.append(nonsubs[0])
        else:
            user = random.choice(nonsubs[1:])
            user.posted_requests.append(request)

    db.session.commit()
    print("Created User-Request relationships")


def user_shifts():
    """
    3. Shifts - User staffed filter_by
    """
    users = User.query.all()
    shifts = Shift.query.all()
    cos126 = Shift.query.filter_by(course="COS126").all()

    for i, user in enumerate(users):
        if i == 0:
            user.schedule.extend(cos126[:2])
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
    # sort schedule based on days
    # sort requests based on days
    # combine together
    k = len(requests)
    for request in requests:
        request.shift.append(random.choice(request.posted_by[0].schedule))

    db.session.commit()
    print("Created Request-Shift relationships")

# 5. Swappable requests


def swap_requests():
    requests = Request.query.all()
    for i in range(0, len(requests), 2):
        # get shifts that this user hasn't requested something for
        requested_shifts = requests[i].posted_by[0].active_requests()
        temp = [(r.shift[0], r.date_posted) for r in requested_shifts]
        requested_shifts = {}
        for tup in temp:
            if tup[0] not in requested_shifts:
                requested_shifts[tup[0]] = [tup[1]]
            else:
                requested_shifts[tup[0]].append(tup[1])

        requests[i].swap_requests.append()
