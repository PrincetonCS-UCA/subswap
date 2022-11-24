class Config:
    SECRET_KEY = "wubalubadubdub"
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


PRICING_ALG = "default"
COURSES = ["COS126", "COS2xx"]
