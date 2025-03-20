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
    BadRequest
)
from jsonschema import (
    validate,
    ValidationError,
    Draft7Validator as D7Validator
)

from ranking_api.extensions import api, db
from ranking_api.authentication import auth
from ranking_api.models import Match
from .utils import fetch_validation_error


class MatchItem(Resource):
    """
    Match api resources
    """
    @staticmethod
    def get(match: Match) -> dict:
        """
        Match GET method handling 
        """
        return match.serialize()

    @staticmethod
    @auth.login_required
    def delete(match: Match):
        """
        Match DELETE method handling 
        """
        db.session.delete(match)
        db.session.commit()
        return Response(status=204)

    @staticmethod
    @auth.login_required
    def put(match: Match):
        """
        Handle PUT method and update given fields on a Match object.
        """
        try:
            new_data = {
                "location": request.json["location"],
                "time": request.json["time"],
                "description": request.json["description"],
                "status": request.json["status"],
                "rating_shift": request.json["rating_shift"],
                "team1_score": request.json["team1_score"],
                "team2_score": request.json["team2_score"]
            }
        except KeyError as e:
            msg = "All Match object fields are required on PUT requests."
            raise BadRequest(description=msg) from e

        try:
            validate(new_data, Match.json_schema())
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

        match.deserialize(new_data)
        db.session.commit()
        return Response(status=200, headers={"Location": api.url_for(MatchItem, match=match)})


class MatchCollection(Resource):
    """
    Matches api resources
    """
    @staticmethod
    def get():
        """
        Handle GET method for all matches
        """
        matches = Match.query.all()
        return [match.serialize() for match in matches]

    @staticmethod
    @auth.login_required
    def post():
        """
        Handle POST method for matches
        """
        try:
            validate(request.json, Match.json_schema(), format_checker=D7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=fetch_validation_error(e)) from e

        match = Match()
        match.deserialize(request.json)

        # Match primary key is auto-incrementing ID and other data can be identical
        # -> No need for Integrity check here
        db.session.add(match)
        db.session.commit()

        resource_url = api.url_for(MatchItem, match=match)
        return Response(status=201, headers={"Location": resource_url})


class MatchConverter(BaseConverter):
    """
    Converter class for matches (str - python)
    """
    def to_python(self, value: str) -> Match:
        match = Match.query.filter_by(id=value).first()
        if match is None:
            raise NotFound(description=f"No such match with ID {value}")
        return match

    def to_url(self, value: Match) -> str:
        return str(value.id)
