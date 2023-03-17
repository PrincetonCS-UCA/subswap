import os
from functools import wraps
from flask import current_app
from flask_login import current_user
from config import PERMISSIONS
# ----------------------------------------------------------------------


def permission_required(permission):
    """
    Creates a decorater for implementing permissions for routes.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                return current_app.login_manager.unauthorized()
            return f(*args, **kwargs)
        return decorated_function
    return decorator
# ----------------------------------------------------------------------


def admin_required(f):
    """
    Function decorater for requiring the admin permission.
    """
    return permission_required(PERMISSIONS['Admin'])(f)
# ----------------------------------------------------------------------


def save_files(files):
    """
    Saves the permanent schedule files to static.
    """
    for name, file in files.items():
        path = os.path.join(current_app.root_path,
                            f'admin/static/files/{name}.csv')
        file.save(path)
    return True
# ----------------------------------------------------------------------
