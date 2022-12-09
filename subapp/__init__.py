import logging
import os
from logging.handlers import RotatingFileHandler

import sqlalchemy as sa
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask.logging import default_handler
from click import echo
from config import config

# ==============================================================================
# Configuration
# ==============================================================================

db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()

# ==============================================================================
# Application Factory Function
# ==============================================================================


def create_app():
    # create the flask application
    app = Flask(__name__)

    # configure the flask app
    config_type = os.getenv('CONFIG_TYPE', default='development')
    app.config.from_object(config[config_type])

    initialize_extensions(app)
    register_blueprints(app)
    configure_logging(app)
    register_cli_commands(app)

    # check if the database needs to be initialized
    engine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    inspector = sa.inspect(engine)
    if not inspector.has_table("user"):
        with app.app_context():
            from subapp import dbscript
            dbscript.create_dummy_data(all=True)

            app.logger.info('Initialized the database!')
    else:
        app.logger.info('Database already contains the user table.')

    return app

# ==============================================================================
# Helper functions
# ==============================================================================


def initialize_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    from subapp.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def register_blueprints(app):
    from subapp.main.routes import main
    from subapp.users.routes import users
    from subapp.requests.routes import requests
    from subapp.admin.routes import admin

    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(requests)
    app.register_blueprint(admin)


def register_cli_commands(app):
    @app.cli.command('init_db')
    def initialize_database():
        from subapp import dbscript
        dbscript.create_dummy_data(all=True)
        echo("Initialized the database!")


def configure_logging(app):
    if app.config['LOG_WITH_GUNICORN'] == "True":
        gunicorn_error_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers.extend(gunicorn_error_logger.handlers)
        app.logger.setLevel(logging.DEBUG)
    else:
        file_handler = RotatingFileHandler('instance/subswap.log',
                                           maxBytes=16384,
                                           backupCount=20)
        file_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(threadName)s-%(thread)d: %(message)s [in %(filename)s:%(lineno)d]')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.removeHandler(default_handler)
    app.logger.info('Starting the SubSwap app.')
