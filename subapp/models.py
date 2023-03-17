from datetime import datetime
from flask_login import UserMixin
from config import ROLES, PERMISSIONS
from subapp import db
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Association tables
# ----------------------------------------------------------------------

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
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Database models
# ----------------------------------------------------------------------


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    netid = db.Column(db.String(120), unique=True, nullable=False)
    balance = db.Column(db.Integer, default=0)
    sub = db.Column(db.Boolean, default=False, nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    posted_requests = db.relationship(
        "Request", secondary=a_posted_requests, back_populates='posted_by')

    accepted_requests = db.relationship(
        "Request", secondary=a_accepted_requests, back_populates='accepted_by')

    schedule = db.relationship(
        "Shift", secondary=a_assigned_shifts, back_populates='staff')

    def __repr__(self):
        return f"User('{self.netid}')"

    def active_requests(self):
        """
        Request has not been accepted AND it is in the future.
        """
        return [request for request in self.posted_requests if not request.accepted and request.date_time()[0] > datetime.now()]

    def inactive_requests(self):
        """
        Request has been accepted OR it is in the past.
        """
        return [request for request in self.posted_requests if request.accepted or request.date_time()[1] < datetime.now()]

    def requested_shifts(self):
        """
        Shifts for which the user has an active request.
        """
        return [request.shift for request in self.active_requests()]

    def is_request_duplicate(self, request):
        """
        @param request should be a dictionary with at least three fields:
        1. posted_by: User object of the poster
        2. shift: Shift object of the related shift
        3. date_request: Of type datetime

        It should NOT be a Request object.
        """
        for req in self.active_requests():
            if ((request["posted_by"] == req.posted_by[0]) &
                    (request["shift"] == req.shift[0]) &
                    (request["date_requested"] == req.date_requested)):
                return True

        return False

    def accepted_reqs(self):
        """
        Returns a list of requests accepted by the user that are in the future.
        """
        future = sorted([request for request in self.accepted_requests if request.date_requested >
                        datetime.now()], key=lambda x: x.date_requested)
        past = sorted([
            request for request in self.accepted_requests if request.date_requested <= datetime.now()], key=lambda x: x.date_requested)
        return (future, past)

    def can(self, perm):
        """
        Checks if the user has the given permission.
        """
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(PERMISSIONS['Admin'])
# ----------------------------------------------------------------------


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_price = db.Column(db.Integer, nullable=False)
    accepted = db.Column(db.Boolean, default=False, nullable=False)
    subsidy = db.Column(db.Integer)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    date_requested = db.Column(db.DateTime, nullable=False)
    date_accepted = db.Column(db.DateTime)

    # associated users and shifts
    posted_by = db.relationship(
        "User", secondary=a_posted_requests, back_populates='posted_requests')

    accepted_by = db.relationship(
        "User", secondary=a_accepted_requests, back_populates='accepted_requests')

    # has to be a shift that is associated with the user requesting it
    shift = db.relationship(
        "Shift", secondary=a_requested_shifts, back_populates="requests")

    def __repr__(self):
        return f"Request('{self.id}')"

    def posted(self):
        return self.posted_by[0]

    def get_price(self):
        return self.base_price

    def get_course(self):
        return self.shift[0].course

    def date_time(self):
        start = datetime.combine(self.date_requested, self.shift[0].start)
        end = datetime.combine(self.date_requested, self.shift[0].end)
        return [start, end]
# ----------------------------------------------------------------------


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
# ----------------------------------------------------------------------


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        for r in ROLES:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in ROLES[r]:
                role.add_permission(perm)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name
# ----------------------------------------------------------------------
