""" Models for Flask Feedback app """

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """ Connects to database """

    db.app = app
    db.init_app(app)