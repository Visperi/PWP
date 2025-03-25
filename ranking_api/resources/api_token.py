"""
API representation of API token resources.
"""
from flask import request, current_app, Response
from flask_restful import Resource

from werkzeug.routing import BaseConverter
from werkzeug.exceptions import Conflict, BadRequest, NotFound

from ranking_api.authentication import auth
from ranking_api.secret_models import ApiToken
from ranking_api.extensions import db

# TODO: Add roles

class ApiTokenItem(Resource):
    """
    Represents a singe ApiToken resource and its HTTP methods in the API.
    ApiTokenConverter is used to pair a user to an actual ApiToken object during requests.
    HTTP404 is raised if an ApiToken with user does not exist.
    """

    @staticmethod
    @auth.login_required
    def get(api_token: ApiToken):
        """
        GET method handler to fetch a serialized ApiToken object from the database.

        :param api_token: The ApiToken object.
        :return: HTTP200 response with The ApiToken object as a serialized JSON in
                 the response body.
        """
        return api_token.serialize()

    @staticmethod
    @auth.login_required
    def delete(api_token: ApiToken):
        """
        DELETE method handler to delete an ApiToken object from the database.

        :param api_token: The ApiToken object to delete.
        :return: HTTP204 response.
        """
        db.session.delete(api_token)
        db.session.commit()
        return Response(status=204)

    @staticmethod
    @auth.login_required
    def patch(api_token: ApiToken):
        """
        PATCH method handler to update a token for existing ApiToken object in the database.

        :param api_token: The ApiToken object to update token for.
        :return: HTTP200 response with the updated ApiToken object in response body.
        """
        keyring = current_app.config["KEYRING"]
        api_token = keyring.update_token(api_token.user)
        return api_token.serialize(), 200


class ApiTokenCollection(Resource):
    """
    Represents a collection of API tokens and HTTP methods for collection requests.
    """

    @staticmethod
    @auth.login_required
    def get():
        """
        GET method handler to fetch collection of ApiToken objects from the database.

        :return: HTTP200 response with a list of ApiToken objects as serialized JSONs in the body.
        """
        api_tokens = ApiToken.query.all()
        return [api_token.serialize() for api_token in api_tokens]

    @staticmethod
    @auth.login_required
    def post():
        """
        POST method handler to create a new ApiToken object for a user into the database.

        :return: HTTP201 response with the created ApiToken object serialized in the response body.
                 HTTP400 response if query parameter user is missing.
                 HTTP409 response if a token for the user already exists.
        """
        try:
            user = request.args["user"]
        except KeyError as e:
            msg = "Query parameter user is required to create an API token."
            raise BadRequest(description=msg) from e

        keyring = current_app.config["KEYRING"]
        try:
            with current_app.app_context():
                api_token = keyring.create_token(user)
        except ValueError as e:
            raise Conflict(description=f"Token for user {user} already exists.") from e

        return api_token.serialize(), 201


class ApiTokenConverter(BaseConverter):
    """
    A converter class responsible for ApiToken object conversions for ApiTokenItem methods.
    Converts users from requests to ApiToken objects, or vice versa ApiToken objects to users.
    """

    def to_python(self, value: str) -> ApiToken:
        """
        Convert a user to an ApiToken object.

        :param value: The ApiToken user.
        :return: The ApiToken object corresponding to the user.
        :raises NotFound: HTTP404 error if an ApiToken object with the user is not in database.
        """
        api_token = ApiToken.query.filter_by(user=value).first()
        if api_token is None:
            raise NotFound(description=f"No such API token with user {value}")
        return api_token

    def to_url(self, value: ApiToken) -> str:
        """
        Convert an ApiToken object to string containing its user.

        :param value: The ApiToken object.
        :return: The ApiToken user.
        """
        return value.user
