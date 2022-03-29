import re
from subapp import db
from subapp.models import User, Shift, Request
from datetime import time, timedelta, datetime, date
import random
#--------------------------------------------------------------------
# reset database
db.drop_all()
db.create_all()
#--------------------------------------------------------------------

# create dummy users 
users = []
users.append(User(netid='mmir', balance=1000))
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

def dummy_enddate(created_date):
    dt = datetime.combine(date.today(), created_date) + timedelta(hours=3)
    return dt.time()

courses = ['COS217', 'COS226', 'COS126']
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
subs = User.query.all()[3:]
print(subs)
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
for request in requests:
    request.shift.append(random.choice(request.posted_by[0].schedule))

db.session.commit()
print("Created Request-Shift relationships")



#--------------------------------------------------------------------
# testing associations
def test_user_requests():
    all_requests = Request.query.all()
    for request in all_requests:
        accepted_by = next(iter(request.accepted_by), None)       
        print(f"Posted by: {request.posted_by[0].netid}, Accepted by: {accepted_by}")

def test_user_shifts():
    shifts = Shift.query.all()
    users = User.query.all()
    for shift in shifts:
        for user in users:
            if user in shift.staff:
                if shift not in user.schedule:
                    print(f"Error: {user} in {shift} but shift not in user schedule.")

            if shift in user.schedule:
                if user not in shift.staff:
                    print(f"Error: {shift} in {user} schedule but user not in shift staff.")
    print("User-Shift associations are correct.")

def test_request_shifts():
    requests = Request.query.all()
    for request in requests:
        if request.shift[0] not in request.posted_by[0].schedule:
            print(f"Error: {request} associated with {request.shift[0]} but shift not in user schedule.")
    print("Request-Shift associations are correct.")

def print_request_data():
    requests = Request.query.all()
    for request in requests:
        print("Shift: ", request.shift[0])
        print("Posted by: ", request.posted_by[0])
        print("Accepted by: ", next(iter(request.accepted_by), None))
        print("Shift in poster schedule: ", request.shift[0] in request.posted_by[0].schedule)
        print("---------------------------------")