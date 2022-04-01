from subapp import db
from subapp.models import User, Shift, Request
from datetime import time, timedelta, datetime, date
import random
#--------------------------------------------------------------------
def create_dummy_data(all=False, reset=False, users=False, requests=False, shifts=False, ushifts=False, rshifts=False, urequests=False):
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
    print("Dummy data created.")

#--------------------------------------------------------------------
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

    for i, user in enumerate(users):
        db.session.add(user)

    db.session.commit()

    print(f"Added {len(User.query.all())} users")
#--------------------------------------------------------------------

# create dummy requests
def create_requests():
    date1 = datetime(2022, 2, 1, 0, 0, 0)
    date2 = datetime(2022, 2, 5, 0, 0, 0)
    date3 = datetime(2022, 2, 2, 0, 0, 0)
    date4 = datetime(2022, 2, 3, 0, 0, 0)
    date5 = datetime(2022, 2, 4, 0, 0, 0)
    date6 = datetime(2022, 2, 6, 0, 0, 0)
    requests = []
    requests.append(Request(swap=False, date_requested=date1, base_price=10, accepted=True, bonus=5))
    requests.append(Request(swap=True, date_requested=date2, base_price=5, accepted=True, bonus=0))
    requests.append(Request(swap=False, date_requested=date3, base_price=15, accepted=True, bonus=10))
    requests.append(Request(swap=False, date_requested=date4, base_price=50, accepted=False, bonus=5))
    requests.append(Request(swap=True, date_requested=date5, base_price=25, accepted=False, bonus=0))
    requests.append(Request(swap=True, date_requested=date6, base_price=15, accepted=False, bonus=10))

    for request in requests:
        db.session.add(request)

    db.session.commit()
    print(f"Added {len(Request.query.all())} requests")

#--------------------------------------------------------------------

# create dummy shifts
def create_shifts():
    def dummy_enddate(created_date):
        dt = datetime.combine(date.today(), created_date) + timedelta(hours=3)
        return dt.time()

    courses = ['COS226/217', 'COS126']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

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
    shifts.append(Shift(day=random.choice(days), start=start1, end=end1, course=random.choice(courses)))
    shifts.append(Shift(day=random.choice(days), start=start2, end=end2, course=random.choice(courses)))
    shifts.append(Shift(day=random.choice(days), start=start3, end=end3, course=random.choice(courses)))
    shifts.append(Shift(day=random.choice(days), start=start4, end=end4, course=random.choice(courses)))
    shifts.append(Shift(day=random.choice(days), start=start5, end=end5, course=random.choice(courses)))

    for shift in shifts:
        db.session.add(shift)

    db.session.commit()

    print(f"Added {len(Shift.query.all())} shifts.")

#--------------------------------------------------------------------

# create associations

# 1. Users - posted requests and accepted requests
def user_requests():
    subs = User.query.all()[3:]
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

# 3. Shifts - User staffed by
def user_shifts():
    users = User.query.all()
    shifts = Shift.query.all()
    
    for i, user in enumerate(users):
        if i == 0:
            user.schedule.extend(shifts)
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
        request.shift.append(random.choice(request.posted_by[0].schedule))

    db.session.commit()
    print("Created Request-Shift relationships")
