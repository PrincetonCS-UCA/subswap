from flask import current_app
from functools import wraps
from flask_login import current_user
from config import PERMISSIONS
import os

# wrapper function for admin


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                return current_app.login_manager.unauthorized()
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(PERMISSIONS['ADMIN'])(f)


def save_files(cos226, cos126):
    cos226_path = os.path.join(
        current_app.root_path, 'admin/static/files/cos226.csv')
    cos126_path = os.path.join(
        current_app.root_path, 'admin/static/files/cos126.csv')
    cos226.save(cos226_path)
    cos126.save(cos126_path)
    return True
