"""
API representation of match resources.
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
from .utils import validate_put_request_properties


class MatchItem(Resource):
    """
    Represents a singe Match resource and its HTTP methods in the API.
    MatchConverter is used to pair an ID to an actual Match object during requests.
    HTTP404 is raised if a Match with ID does not exist.
    """

    @staticmethod
    def get(match: Match) -> dict:
        """
        GET method handler to fetch a serialized Match object from the database.

        :param match: The Match object.
        :return: HTTP200 response with The Match object as a serialized JSON in the response body.
        """
        return match.serialize()

    @staticmethod
    @auth.login_required
    def delete(match: Match):
        """
        DELETE method handler to delete a Match object from the database.

        :param match: The Match object to delete.
        :return: HTTP204 response.
        """
        db.session.delete(match)
        db.session.commit()
        return Response(status=204)

    @staticmethod
    @auth.login_required
    def put(match: Match):
        """
        PUT method handler to modify an existing Match object in the database.

        :param match: The Match object to modify.
        :return: HTTP200 response with the modified Match object path in Location header.
        :raises: BadRequest HTTP400 error if the object fields are invalid.
        """
        validate_put_request_properties(Match.json_schema(), request.json)
        match.deserialize(request.json)
        db.session.commit()
        return Response(status=200, headers={"Location": api.url_for(MatchItem, match=match)})


class MatchCollection(Resource):
    """
    Represents a collection of matches and HTTP methods for collection requests.
    """

    @staticmethod
    def get():
        """
        GET method handler to fetch collection of Match objects from the database.

        :return: HTTP200 response with a list of Match objects as serialized JSONs in the body.
        """
        matches = Match.query.all()
        return [match.serialize() for match in matches]

    @staticmethod
    @auth.login_required
    def post():
        """
        POST method handler to create a new Match object into the database.

        :return: HTTP201 response with the created object path in Location header.
                 HTTP400 response if the provided data is not valid.
        """
        try:
            validate(request.json, Match.json_schema(), format_checker=D7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=str(e)) from e

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
    A converter class responsible for Match object conversions for MatchItem methods.
    Converts IDs from requests to Match objects, or vice versa Match objects to IDs.
    """

    def to_python(self, value: str) -> Match:
        """
        Convert an ID to a Match object.

        :param value: The match ID.
        :return: The Match object corresponding to the ID.
        :raises: NotFound HTTP404 response if a Match object with the ID is not in database.
        """
        match = Match.query.filter_by(id=value).first()
        if match is None:
            raise NotFound
        return match

    def to_url(self, value: Match) -> str:
        """
        Convert a Match object to string containing its ID.

        :param value: The Match object.
        :return: The match ID as a string.
        """
        return str(value.id)
