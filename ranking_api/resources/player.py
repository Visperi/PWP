"""
API representation of match resources
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
from .utils import str_to_bool


class PlayerItem(Resource):
    """
    Player api resources
    """
    @staticmethod
    def get(player: Player) -> dict:
        """
        Player GET method handling 
        """
        return player.serialize()

    @staticmethod
    @auth.login_required
    def delete(player: Player):
        """
        Player DELETE method handling 
        """
        db.session.delete(player)
        db.session.commit()
        return Response(status=204)

    @staticmethod
    @auth.login_required
    def put(player: Player):
        """
        Handle PUT method and update given fields on a Player object.
        """
        try:
            new_data = {
                "username": request.json["username"],
                "num_of_matches": request.json["num_of_matches"],
                "rating": request.json["rating"]
            }
        except KeyError as e:
            msg = "All Player object fields are required on PUT requests."
            raise BadRequest(description=msg) from e

        try:
            validate(new_data, Player.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        player.deserialize(new_data)
        db.session.commit()
        return Response(status=200, headers={"Location": api.url_for(PlayerItem, player=player)})


class PlayerCollection(Resource):
    """
    Players api resources
    """
    @staticmethod
    def get():
        """
        Handle GET method for all players
        """
        # Parse possible query parameter for including or excluding matches for players
        include_matches = request.args.get("include_matches", default=True, type=str_to_bool)

        players = Player.query.all()
        return [player.serialize(include_matches=include_matches) for player in players]

    @staticmethod
    @auth.login_required
    def post():
        """
        Handle POST method for players
        """
        try:
            validate(request.json, Player.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

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
    Converter class for matches (str - python)
    """
    def to_python(self, value: str) -> Player:
        player = Player.query.filter_by(username=value).first()
        if player is None:
            raise NotFound
        return player

    def to_url(self, value: Player) -> str:
        return value.username
