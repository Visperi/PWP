"""
App factory module for creating the application.
"""

from flask import Flask

from .extensions import db


def create_app() -> Flask:
    """
    Create and initialize a new Ranking API application via factory methods.

    :return: The Flask application with extensions and interfaces registered for use.
    """

    app = Flask(__name__.split(".")[0])
    app.config.from_object("config.Config")

    register_extensions(app)

    # Create tables if they do not exist yet
    with app.app_context():
        db.create_all()

    return app


def register_extensions(app: Flask):
    """
    Initialize extensions utilized by the main Flask application.

    :param app: The main Flask application
    """

    db.init_app(app)
