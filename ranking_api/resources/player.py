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
    Conflict,
    NotImplemented
)
from jsonschema import validate, ValidationError
from sqlalchemy.exc import IntegrityError

from ranking_api.extensions import api, db
from ranking_api.models import Player
from .utils import str_to_bool


class PlayerItem(Resource):

    @staticmethod
    def get(player: Player) -> dict:
        return player.serialize()

    @staticmethod
    def delete(player: Player):
        # TODO: Implement this
        raise NotImplemented


class PlayerCollection(Resource):

    @staticmethod
    def get():
        # Parse possible query parameter for including or excluding matches for players
        include_matches = request.args.get("include_matches", default=True, type=str_to_bool)

        players = Player.query.all()
        return [player.serialize(include_matches=include_matches) for player in players]

    @staticmethod
    def post():
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Player.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

        data = dict(username=request.json["username"],
                    num_of_matches=request.json.get("num_of_matches"),
                    rating=request.json.get("rating"))
        player = Player()
        player.deserialize(data)

        try:
            db.session.add(player)
            db.session.commit()
        except IntegrityError:
            raise Conflict(description=f"Player with username {player.username} already exists")

        resource_url = api.url_for(PlayerItem, player=player)
        return Response(status=201, headers=dict(Location=resource_url))


class PlayerConverter(BaseConverter):

    def to_python(self, value: str) -> Player:
        player = Player.query.filter_by(username=value).first()
        if player is None:
            raise NotFound
        return player

    def to_url(self, value: Player) -> str:
        return value.username
