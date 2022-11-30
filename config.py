import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ENV = 'development'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL').replace("://", "ql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


PRICING_ALG = "default"
COURSES = ["COS126", "COS2xx"]
