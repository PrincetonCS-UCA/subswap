import os

# Determine the folder of the top-level directory of this project
BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    FLASK_ENV = 'development'
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', default='wubalubadubub')
    # if database url is not given, an sqllite datebase is stored in the
    # instance folder
    CAS_SERVER_URL = os.environ.get(
        'CAS_SERVER_URL', default='https://fed.princeton.edu/cas/login')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_WITH_GUNICORN = os.environ.get('LOG_WITH_GUNICORN', default=False)


class ProductionConfig(Config):
    FLASK_ENV = 'production'
    CAS_SERVICE_URL = os.environ.get('CAS_SERVICE_URL')
    if os.getenv('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').replace(
            "postgres://", "postgresql://", 1)
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASEDIR, 'instance', 'data-dev.db')}"


class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    CAS_SERVICE_URL = 'http://localhost:5000/login?next=%2F'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f"sqlite:///{os.path.join(BASEDIR, 'instance', 'data-dev.db')}"


class TestingConfig(Config):
    TESTING = True
    CAS_SERVICE_URL = 'http://localhost:5000/login?next=%2F'
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI',
                                             default=f"sqlite:///{os.path.join(BASEDIR, 'instance', 'test.db')}")
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

PRICING_ALG = "default"
ICO = 400
COURSES = ["COS126", "COS2xx"]
PERMISSIONS = {"COS126": 1, "COS2xx": 2, "ADMIN": 4}
ROLES = {"COS126": [1], "COS2xx": [1, 2], "ADMIN": [1, 2, 4]}
ADMINS = ["mmir", "lumbroso"]
