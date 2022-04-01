import pandas as pd
from subapp.models import Shift, User
from subapp import db
from flask import current_app, session
from functools import wraps
from flask_login import current_user
import os

# wrapper function for admin
def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
               return current_app.login_manager.unauthorized()
            urole = current_user.role
            if ((urole != role) and (role != "ANY")):
                return current_app.login_manager.unauthorized()      
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


def save_files(cos226, cos126):
    cos226_path = os.path.join(current_app.root_path, 'admin/static/files/cos226.csv')
    cos126_path = os.path.join(current_app.root_path, 'admin/static/files/cos126.csv')
    cos226.save(cos226_path)
    cos126.save(cos126_path)
    return True