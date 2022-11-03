from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


a_posted_requests = db.Table("posted_requests",
                             db.Column("user_id", db.Integer, db.ForeignKey(
                                 "user.id"), primary_key=True),
                             db.Column("request_id", db.Integer, db.ForeignKey("request.id"), primary_key=True))

a_accepted_requests = db.Table("accepted_requests",
                               db.Column("user_id", db.Integer, db.ForeignKey(
                                   "user.id"), primary_key=True),
                               db.Column("request_id", db.Integer, db.ForeignKey("request.id"), primary_key=True))

a_assigned_shifts = db.Table("assigned_shifts",
                             db.Column("user_id", db.Integer, db.ForeignKey(
                                 "user.id"), primary_key=True),
                             db.Column("shift_id", db.Integer, db.ForeignKey("shift.id"), primary_key=True))

a_requested_shifts = db.Table("requested_shifts",
                              db.Column("request_id", db.Integer, db.ForeignKey(
                                  "request.id"), primary_key=True),
                              db.Column("shift_id", db.Integer, db.ForeignKey("shift.id"), primary_key=True))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    netid = db.Column(db.String(120), unique=True, nullable=False)
    balance = db.Column(db.Integer, default=0)
    role = db.Column(db.String(120), default="user")
    sub = db.Column(db.Boolean, default=False, nullable=False)

    posted_requests = db.relationship(
        "Request", secondary=a_posted_requests, back_populates='posted_by')

    accepted_requests = db.relationship(
        "Request", secondary=a_accepted_requests, back_populates='accepted_by')

    schedule = db.relationship(
        "Shift", secondary=a_assigned_shifts, back_populates='staff')

    def __repr__(self):
        return f"User('{self.netid}')"

    def active_requests(self):
        return [request for request in self.posted_requests if not request.accepted]

    def inactive_requests(self):
        return [request for request in self.posted_requests if request.accepted]

    # shifts for which the user has submitted a request
    def requested_shifts(self):
        return [request.shift for request in self.active_requests()]

    # shifts for which the user's request was accepted. idk why this is useful
    def fulfilled_shifts(self):
        return [request.shift for request in self.inactive_requests()]

    def is_duplicate(self, request):
        for req in self.active_requests():
            if req.is_duplicate(request):
                return True

        return False


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    swap = db.Column(db.Boolean, default=False, nullable=False)
    base_price = db.Column(db.Integer, nullable=False)
    accepted = db.Column(db.Boolean, default=False, nullable=False)
    bonus = db.Column(db.Integer, nullable=False, default=0)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    date_requested = db.Column(db.DateTime, nullable=False)
    is_possible_swap = db.Column(db.Boolean, default=False, nullable=False)
    # associated users and shifts
    posted_by = db.relationship(
        "User", secondary=a_posted_requests, back_populates='posted_requests')

    accepted_by = db.relationship(
        "User", secondary=a_accepted_requests, back_populates='accepted_requests')

    # has to be a shift that is associated with the user requesting it
    shift = db.relationship(
        "Shift", secondary=a_requested_shifts, back_populates="requests")

    # has to be shifts that are not in the current users schedule and don't
    # conflict with them
    swap_requests_id = db.Column(db.Integer, db.ForeignKey('request.id'))
    swap_requests = db.relationship("Request")

    def __repr__(self):
        return f"Request('{self.id}')"

    def posted(self):
        return self.posted_by[0]

    def is_duplicate(self, request):
        if ((request.posted_by == self.posted_by) &
                (request.shift == self.shift) &
                (request.date_requested == self.date_requested)):
            return True
        else:
            return False


class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    start = db.Column(db.Time, nullable=False)
    end = db.Column(db.Time, nullable=False)

    course = db.Column(db.String(120), nullable=False)

    staff = db.relationship(
        "User", secondary=a_assigned_shifts, back_populates="schedule")

    requests = db.relationship(
        "Request", secondary=a_requested_shifts, back_populates="shift")

    def __repr__(self):
        return f"Shift('{self.id}')"

    def formatted(self):
        s = self.start.strftime("%I:%M%p")
        e = self.end.strftime("%I:%M%p")
        return f"{self.day}, {s} - {e}"

    def user_requests(self, user):
        return [request for request in self.requests if request.posted_by == user]
