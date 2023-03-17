from subapp.models import User, Request, Shift
# ----------------------------------------------------------------------


def test():
    test_user_requests()
    test_user_shifts()
    test_request_shifts()
# ----------------------------------------------------------------------


def test_user_requests():
    all_requests = Request.query.all()
    for request in all_requests:
        accepted_by = next(iter(request.accepted_by), None)
        print(
            f"Posted by: {request.posted_by[0].netid}, Accepted by: {accepted_by}")
# ----------------------------------------------------------------------


def test_user_shifts():
    shifts = Shift.query.all()
    users = User.query.all()
    for shift in shifts:
        for user in users:
            if user in shift.staff:
                if shift not in user.schedule:
                    print(
                        f"Error: {user} in {shift} but shift not in user schedule.")

            if shift in user.schedule:
                if user not in shift.staff:
                    print(
                        f"Error: {shift} in {user} schedule but user not in shift staff.")
    print("User-Shift associations are correct.")
# ----------------------------------------------------------------------


def test_request_shifts():
    requests = Request.query.all()
    for request in requests:
        if request.shift[0] not in request.posted_by[0].schedule:
            print(
                f"Error: {request} associated with {request.shift[0]} but shift not in user schedule.")
    print("Request-Shift associations are correct.")
# ----------------------------------------------------------------------


def print_request_data():
    requests = Request.query.all()
    for request in requests:
        print("Shift: ", request.shift[0])
        print("Posted by: ", request.posted_by[0])
        print("Accepted by: ", next(iter(request.accepted_by), None))
        print("Shift in poster schedule: ",
              request.shift[0] in request.posted_by[0].schedule)
        print("---------------------------------")
# ----------------------------------------------------------------------
