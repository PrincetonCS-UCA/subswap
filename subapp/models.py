from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from config import ROLES, PERMISSIONS

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
        return [request for request in self.posted_requests if not request.accepted]

    def inactive_requests(self):
        return [request for request in self.posted_requests if request.accepted]

    # shifts for which the user has submitted a request
    def requested_shifts(self):
        return [request.shift for request in self.active_requests()]

    # shifts for which the user's request was accepted. idk why this is useful
    def fulfilled_shifts(self):
        return [request.shift for request in self.inactive_requests()]

    def is_request_duplicate(self, request):
        for req in self.active_requests():
            if req.is_duplicate(request):
                return True

        return False

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(PERMISSIONS['ADMIN'])


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_price = db.Column(db.Integer, nullable=False)
    accepted = db.Column(db.Boolean, default=False, nullable=False)
    bonus = db.Column(db.Integer, nullable=False, default=0)
    subsidy = db.Column(db.Integer, default=0)
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

    def is_duplicate(self, request):
        if ((request.posted_by == self.posted_by) &
                (request.shift == self.shift) &
                (request.date_requested == self.date_requested)):
            return True
        else:
            return False

    def get_price(self):
        return self.base_price + self.bonus

    def get_course(self):
        return self.shift[0].course


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
