"""
App factory module for creating the application.
"""

from flask import Flask

from .extensions import (
    db,
    api
)
from .resources.player import (
    PlayerConverter,
    PlayerCollection,
    PlayerItem
)

from .resources.match import (
    MatchConverter,
    MatchCollection,
    MatchItem
)


def create_app() -> Flask:
    """
    Create and initialize a new Ranking API application via factory methods.

    :return: The Flask application with extensions and interfaces registered for use.
    """

    app = Flask(__name__.split(".")[0])
    app.config.from_object("config.Config")

    register_converters(app)
    register_resources()
    register_extensions(app)

    # Create tables if they do not exist yet
    with app.app_context():
        db.create_all()

    return app


def register_converters(app: Flask):
    """
    Register converters for resources.

    :param app: The main Flask application
    """
    app.url_map.converters["player"] = PlayerConverter
    app.url_map.converters["match"] = MatchConverter


def register_resources():
    """
    Register resources and their routing for the Flask API.
    """

    # TODO: Implement the resource urls
    api.add_resource(PlayerCollection, "/api/")
    api.add_resource(PlayerItem, "/api/")
    
    api.add_resource(MatchCollection, "/api/")
    api.add_resource(MatchItem, "/api/")


def register_extensions(app: Flask):
    """
    Initialize extensions utilized by the main Flask application.

    :param app: The main Flask application
    """

    db.init_app(app)
    api.init_app(app)
