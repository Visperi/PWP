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
from ranking_api.models import Match

class MatchItem(Resource):

    @staticmethod
    def get() -> Match:
        pass

class MatchCollection(Resource):
    @staticmethod
    def get():
        pass

    def post():
        if not request.json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Match.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e))

        data = dict(
            location=request.json["location"],
            time=request.json["time"],
            description=request.json["description"],
            status=request.json["status"],
            rating_shift=request.json["rating_shift"],
            team1_score=request.json["team1_score"],
            team2_score=request.json["team2_score"],
            players=request.json["players"]
        )
        match = Match()
        match.deserialize(data)

        db.session.add(match)
        db.session.commit()

        # TODO: Update this when the resource urls are designed
        resource_url = api.url_for(MatchItem,
                                   match=match)

        return Response(status=201, headers=dict(Location=resource_url))

class MatchConverter(BaseConverter):
    def to_python(self, value: str) -> Match:
        match = Match.query(id=value).first()
        if match is None:
            raise NotFound
        return match

    def to_url(self, value: Match) -> str:
        return str(value.id)