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
    UnsupportedMediaType,
    Conflict
)
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError

from ranking_api.extensions import api, db
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
    def delete(player: Player):
        """
        Player DELETE method handling 
        """
        db.session.delete(player)
        db.session.commit()
        return Response(status=204)

    @staticmethod
    def post(player: Player):
        """
        Player POST method handling 
        """
        # TODO: Implement to support updating player data
        raise NotImplementedError


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
    def post():
        """
        Handle POST method for players
        """
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Player.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        data = {
            "username": request.json["username"],
            "num_of_matches": request.json.get("num_of_matches"),
            "rating": request.json.get("rating")
        }

        player = Player()
        player.deserialize(data)

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
