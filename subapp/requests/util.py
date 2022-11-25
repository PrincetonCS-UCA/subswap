from subapp.models import Shift
from datetime import time, timedelta, datetime, date
from flask import jsonify
from flask_login import current_user
import math

# def validate_request(request, swap):
#     # can current user create this request?
#     # is it a duplicate?
#     if request.posted().is_duplicate(requst):
#         return False
#     # is it not a valid date?
#     # if swap is true, can the user swap this shift?

#     pass


def calc_base_price(shiftid, startdate):
    request_date = startdate
    if (type(startdate) == str):
        request_date = datetime.strptime(
            startdate, '%Y-%m-%d')
    num_days = request_date - \
        datetime.combine(date.today(), datetime.min.time())
    price = int(50/math.log(num_days.days, 2)) if num_days.days > 1 else 60

    return {'status': "True" if price < current_user.balance else "False", 'price': price}


def get_swap_options(request_date):
    """
    Genereates possible swap shifts for the current user around startdate.
    Looks for possible shifts in a 10 day window around startdate.

    Returns a list in this format: [[1, "Monday, 03:00PM - 06:00PM, 11-07-2022"], ...]
    """
    # request_date = datetime.strptime(
    #     startdate, '%Y-%m-%d')
    num_days = request_date - \
        datetime.combine(date.today(), datetime.min.time())
    dates = [request_date - timedelta(days=x)
             for x in range(1, num_days.days)]
    dates += [request_date + timedelta(days=x)
              for x in range(10 - num_days.days)]
    dates.sort()

    # we have a list of dates
    day_shifts = {}

    for shift in current_user.schedule:
        if shift.day not in day_shifts:
            day_shifts[shift.day] = [shift]
        else:
            day_shifts[shift.day].append(shift)

    swap_shift_list = []

    # add shifts to each day
    for x in dates:
        # get shifts for that day
        if x.strftime('%A') in day_shifts:
            for shift in day_shifts[x.strftime('%A')]:
                swap_shift_list.append(
                    [shift.id, shift.formatted() + ", " + x.strftime("%m-%d-%Y")])

    return swap_shift_list


def process_shift_str(shift_data):
    """
    Input format: "1, Monday, 03:00PM - 06:00PM, 11-07-2022"
    Output format: (1, 11-07-2022)
    """
    # [1, Monday, 03:00PM - 06:00PM, 11-07-2022]
    # first index is id and last index is date
    shift_data = shift_data.split(',')
    id = int(shift_data[0])
    date = datetime.strptime(shift_data[-1].strip(), "%m-%d-%Y")

    return (id, date)
