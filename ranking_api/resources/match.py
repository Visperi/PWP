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
    def post(match: Match):
        """
        Match POST method handling 
        """
        # TODO: Implement to support updating match data
        raise NotImplementedError


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
            msg = f"{e.schema['description']}: {e.message}"
            raise BadRequest(description=msg) from e

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
