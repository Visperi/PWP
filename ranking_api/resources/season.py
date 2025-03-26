"""
API representation of season resources.
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
from ranking_api.models import Season
from .utils import validate_put_request_properties, fetch_validation_error_message

class SeasonItem(Resource):
    """
    Represents a single Season resource and its HTTP methods in the API
    """

    @staticmethod
    def get(season: Season) -> dict:
        """
        GET method handler to fetch a serialized Season object from the database.
        
        :param season: The Season object
        :return: HTTP200 response with the Season object as a serialized JSON in the response body.
        """
        return season.serialize()

    @staticmethod
    @auth.login_required
    def delete(season: Season):
        """
        DELETE method handler to delete a Season object from the database.
        
        :param season: The Season object to delete.
        :return: HTTP204 response.
        """
        db.session.delete(season)
        db.session.commit()
        return Response(status=204)

    @staticmethod
    @auth.login_required
    def put(season: Season):
        """
        PUT method handler to modify an existing Season object in the database.

        :param season: The Season object to modify.
        :return: HTTP200 response with the modified Season object path in Location header.
        :raises BadRequest: HTTP400 error if the object fields are invalid.
        """
        validate_put_request_properties(Season.json_schema(), request.json)
        season.deserialize(request.json)
        db.session.commit()
        return Response(status=200, headers={"Location": api.url_for(SeasonItem, season=season)})

class SeasonCollection(Resource):
    """
    Represents a collection of seasons and HTTP method for collection requests.
    """

    @staticmethod
    def get():
        """
        GET method handler to fetch collection of Season objects from the database.

        :return: HTTP200 response with a list of Match objects as serialized JSONs in the body.
        """
        seasons = Season.query.all()
        return [season.serialize() for season in seasons]

    @staticmethod
    @auth.login_required
    def post():
        """
        POST method handler ot create a new Season object into the database.

        :return: HTTP201 response with the created object path in Location header.
        :raises BadRequest: HTTP400 error if the provided data is not valid.
        """
        try:
            validate(request.json, Season.json_schema(), format_checker=D7Validator.FORMAT_CHECKER)
        except ValidationError as e:
            raise BadRequest(description=fetch_validation_error_message(e)) from e

        season = Season()
        season.deserialize(request.json)

        db.session.add(season)
        db.session.commit()

        resource_url = api.url_for(SeasonItem, season=season)
        return Response(status=201, headers={"Location": resource_url})

class SeasonConverter(BaseConverter):
    """
    A converter class responsible for Season object conversions for SeasonItem methods.
    Converts IDs from requests to Season objects, or vice versa Season objects to IDs.
    """

    def to_python(self, value):
        """
        Convert and ID to a Season object.

        :param value: The Season ID.
        :return: The Season object corresponding to the ID.
        :raises NotFound: HTTP404 error if a Season object with the id is not in database.
        """
        season = Season.query.filter_by(id=value).first()
        if season is None:
            raise NotFound(description=f"No such season with ID {value}")
        return season

    def to_url(self, value):
        """
        Convert a Season object to string containing its ID.

        :param value: The Season object.
        :return: The seson ID as a string.
        """
        return str(value.id)
