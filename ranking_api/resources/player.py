"""
API representation of player resources.
"""
from flask import (
    request,
    Response
)
from flask_restful import Resource
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import (
    NotFound,
    BadRequest,
    Conflict
)
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError

from ranking_api.extensions import api, db
from ranking_api.authentication import auth
from ranking_api.models import Player
from .utils import str_to_bool, validate_put_request_properties, fetch_validation_error_message


class PlayerItem(Resource):
    """
    Represents a single Player resource and its HTTP methods in the API.
    PlayerConverter is used to pair a username to an actual Player object during requests.
    HTTP404 is raised if a Player with username does not exist.
    """
    @staticmethod
    def get(player: Player) -> dict:
        """
        GET method handler to fetch a serialized Player object from the database.

        :param player: The Player object.
        :return: HTTP200 response with The Player object as a serialized JSON in the response body.
        """
        return player.serialize()

    @staticmethod
    @auth.login_required
    def delete(player: Player):
        """
        DELETE method handler to delete a Player object from the database.

        :param player: The Player object to delete.
        :return: HTTP204 response.
        """
        db.session.delete(player)
        db.session.commit()
        return Response(status=204)

    @staticmethod
    @auth.login_required
    def put(player: Player):
        """
        PUT method handler to modify an existing Player object in the database.

        :param player: The Player object to modify.
        :return: HTTP200 response with the modified Player object path in Location header.
        :raises BadRequest: HTTP400 error if the object fields are invalid.
        """
        validate_put_request_properties(Player.json_schema(), request.json)
        player.deserialize(request.json)
        db.session.commit()
        return Response(status=200, headers={"Location": api.url_for(PlayerItem, player=player)})


class PlayerCollection(Resource):
    """
    Represents a collection of players and HTTP methods for collection requests.
    """

    @staticmethod
    def get():
        """
        GET method handler to fetch collection of Player objects from the database.
        Supports a query parameter include_matches (default: True) for fetching also
        the players matches with the data.

        :return: HTTP200 response with a list of Player objects as serialized JSONs in the body.
        """
        # Parse possible query parameter for including or excluding matches for players
        include_matches = request.args.get("include_matches", default=True, type=str_to_bool)

        players = Player.query.all()
        return [player.serialize(include_matches=include_matches) for player in players]

    @staticmethod
    @auth.login_required
    def post():
        """
        POST method handler to create a new Player object into the database.

        :return: HTTP201 response with the created object path in Location header.
        :raises BadRequest: HTTP400 error if the provided data is not valid.
        """
        try:
            validate(request.json, Player.json_schema())
        except ValidationError as e:
            raise BadRequest(description=fetch_validation_error_message(e)) from e

        player = Player()
        player.deserialize(request.json)

        try:
            db.session.add(player)
            db.session.commit()
        except IntegrityError as exc:
            raise Conflict(
                description=f"Player with username {player.username} already exists"
            ) from exc

        resource_url = api.url_for(PlayerItem, player=player)
        return Response(status=201, headers={"Location": resource_url})


class PlayerConverter(BaseConverter):
    """
    A converter class responsible for Player object conversions for PlayerItem methods.
    Converts usernames from requests to Player objects, or vice versa Player objects to usernames.
    """
    def to_python(self, value: str) -> Player:
        """
        Convert a username to a Player object.

        :param value: The players' username.
        :return: The Player object corresponding to the username.
        :raises: NotFound HTTP404 error if a Player object with the username is not in database.
        """
        player = Player.query.filter_by(username=value).first()
        if player is None:
            raise NotFound(description=f"No such player with username {value}")
        return player

    def to_url(self, value: Player) -> str:
        """
        Convert a Player object to string containing its username.

        :param value: The Player object.
        :return: The player username.
        """
        return value.username
