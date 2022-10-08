from subapp.models import Request, Shift, User


def validate_request(Request: request, Bool: swap):
    # can current user create this request?
    # is it a duplicate?
    if request.posted().is_duplicate(requst):
        return False
    # is it not a valid date?
    # if swap is true, can the user swap this shift?

    pass
