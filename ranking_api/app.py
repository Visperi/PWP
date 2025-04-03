"""
App factory module for creating the application.
"""
from typing import Union, Tuple

from flask import Flask
from werkzeug.exceptions import HTTPException

from .authentication import Keyring
from .extensions import (
    db,
    api,
    auth
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
from .resources.api_token import (
    ApiTokenConverter,
    ApiTokenCollection,
    ApiTokenItem
)

from .resources.season import (
    SeasonConverter,
    SeasonCollection,
    SeasonItem
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
    register_error_handlers(app)

    # Initialize keyring and create database tables if they do not exist yet
    with app.app_context():
        db.create_all()
        initialize_keyring(app)


    return app


def initialize_keyring(app: Flask):
    """
    Initialize a keyring object handling API tokens.

    :param app: The Flask app to initialize the keyring to.
    """
    keyring = Keyring()
    app.config["KEYRING"] = keyring
    if app.debug:
        app.logger.info(f"Your development API token is: {keyring.debug_token}")

def register_converters(app: Flask):
    """
    Register converters for resources.

    :param app: The main Flask application
    """
    app.url_map.converters["player"] = PlayerConverter
    app.url_map.converters["match"] = MatchConverter
    app.url_map.converters["season"] = SeasonConverter
    app.url_map.converters["api_token"] = ApiTokenConverter


def register_resources():
    """
    Register resources and their routing for the Flask API.
    """

    api.add_resource(PlayerCollection, "/players/")
    api.add_resource(PlayerItem, "/players/<player:player>/")

    api.add_resource(MatchCollection, "/matches/")
    api.add_resource(MatchItem, "/matches/<match:match>/")

    api.add_resource(SeasonCollection, "/seasons/")
    api.add_resource(SeasonItem, "/seasons/<season:season>/")

    api.add_resource(ApiTokenCollection, "/tokens/")
    api.add_resource(ApiTokenItem, "/tokens/<api_token:api_token>/")


def register_extensions(app: Flask):
    """
    Initialize extensions utilized by the main Flask application.

    :param app: The main Flask application
    """

    db.init_app(app)
    api.init_app(app)


def register_error_handlers(app: Flask):
    """
    Register error handlers that return JSON responses for errors instead of the default plain text.

    :param app: Flask app to register the error handlers for.
    """

    def build_response(error_code: int, message: str) -> Tuple[dict, int]:
        """
        Build JSON response for an error.

        :param error_code: HTTP error code of the error.
        :param message: The error message.
        :return: Tuple containing the JSON response and HTTP status code.
        """
        return {"message": message}, error_code

    @auth.error_handler
    def handle_auth_error(error_code: int) -> Tuple[dict, int]:
        """
        Handle authentication errors, meaning HTTP401 for invalid API token and HTTP403 if the
        token is valid but is not authorized to complete a request.

        :param error_code: Error code of the error.
        :return: Tuple containing a JSON response and the HTTP status code.
        """
        if error_code == 401:
            message = "Invalid API token."
        else:
            message = "Insufficient credentials for the request."

        return build_response(error_code, message)

    @app.errorhandler(HTTPException)
    def handle_generic_error(error: HTTPException) -> Tuple[dict, int]:
        """
        Handle all generic HTTP errors.

        :param error: The HTTP error.
        :return: Tuple containing a JSON response and the HTTP status code.
        """
        return build_response(error.code, error.description)
