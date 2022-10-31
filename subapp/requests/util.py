from subapp.models import Request, Shift, User


# def validate_request(request, swap):
#     # can current user create this request?
#     # is it a duplicate?
#     if request.posted().is_duplicate(requst):
#         return False
#     # is it not a valid date?
#     # if swap is true, can the user swap this shift?

#     pass


def get_swap_options(int: shiftid):
    """
    Genereates shif
    Args:
        int (shiftid): _description_
    """
    shift = Shift.query.filter_by(id=shiftid).first()
