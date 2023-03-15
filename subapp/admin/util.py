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
    return permission_required(PERMISSIONS['Admin'])(f)


def save_files(files):
    for name, file in files.items():
        path = os.path.join(current_app.root_path, f'admin/static/files/{name}.csv')
        file.save(path)
    return True
