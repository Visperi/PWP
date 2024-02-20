from flask import (
    request,
    Response
)
from flask_restful import Resource
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import (
    NotFound,
    BadRequest,
    UnsupportedMediaType
)
from jsonschema import validate, ValidationError

from ranking_api.extensions import api, db
from ranking_api.models import Player


class PlayerItem(Resource):

    @staticmethod
    def get() -> Player:
        pass


class PlayerCollection(Resource):

    @staticmethod
    def get():
        pass

    @staticmethod
    def post():
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Player.validate_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

        data = dict(num_of_matches=request.json["num_of_matches"],
                    rating=request.json["rating"])
        player = Player()
        player.deserialize(data)

        db.session.add(player)
        db.session.commit()

        # TODO: Update this when the resource urls are designed
        resource_url = api.url_for(PlayerItem,
                                   player=player)

        return Response(status=201, headers=dict(Location=resource_url))


class PlayerConverter(BaseConverter):

    def to_python(self, value: str) -> Player:
        player = Player.query(username=value).first()
        if player is None:
            raise NotFound
        return player

    def to_url(self, value: Player) -> str:
        return value.username