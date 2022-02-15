from app import db, login_manager
from datetime import datetime, timedelta
from flask_login import UserMixin
#----------------------------------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#----------------------------------------------------------------------
# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # name, netid, assigned_shifts, posted_requests, accepted_requests
    # type: admin, user

# Request model. Can be a sub or a swap
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # shift, posted_by, accepted_by, swap?

# Model for storing shift times
class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # datetime, users, requests