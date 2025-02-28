"""
App factory module for creating the application.
"""
from typing import Union

from flask import Flask

from .authentication import Keyring
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


def create_app(config_obj: Union[object, str] = "config.Config") -> Flask:
    """
    Create and initialize a new Ranking API application via factory methods.

    :param config_obj: A configuration object import name of a configuration object.
                       This object is not instantiated, so if that is needed it must be
                       done before passing the object.
    :return: The Flask application with extensions and interfaces registered for use.
    """

    app = Flask(__name__.split(".", maxsplit=1)[0])
    app.config.from_object(config_obj)

    register_converters(app)
    register_resources()
    register_extensions(app)

    # Initialize keyring and create database tables if they do not exist yet
    with app.app_context():
        db.create_all()
        app.config["KEYRING"] = Keyring()

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

    api.add_resource(PlayerCollection, "/api/players/")
    api.add_resource(PlayerItem, "/api/players/<player:player>/")

    api.add_resource(MatchCollection, "/api/matches/")
    api.add_resource(MatchItem, "/api/matches/<match:match>/")


def register_extensions(app: Flask):
    """
    Initialize extensions utilized by the main Flask application.

    :param app: The main Flask application
    """

    db.init_app(app)
    api.init_app(app)
