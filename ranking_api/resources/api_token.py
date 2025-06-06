"""
API representation of API token resources.
"""
from flask import request, current_app, Response
from flask_restful import Resource

from werkzeug.routing import BaseConverter
from werkzeug.exceptions import Conflict, BadRequest, NotFound

from ranking_api.authentication import auth, UserCollisionError
from ranking_api.secret_models import ApiToken
from ranking_api.extensions import db


class ApiTokenItem(Resource):
    """
    Represents a singe ApiToken resource and its HTTP methods in the API.
    ApiTokenConverter is used to pair a user to an actual ApiToken object during requests.
    HTTP404 is raised if an ApiToken with user does not exist.
    """

    @staticmethod
    @auth.login_required(role="super admin")
    def get(api_token: ApiToken):
        """
        GET method handler to fetch a serialized ApiToken object from the database.

        :param api_token: The ApiToken object.
        :return: HTTP200 response with The ApiToken object as a serialized JSON in
                 the response body.
        """
        return api_token.serialize()

    @staticmethod
    @auth.login_required(role="super admin")
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
    @auth.login_required(role="super admin")
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
    @auth.login_required(role="super admin")
    def get():
        """
        GET method handler to fetch collection of ApiToken objects from the database.

        :return: HTTP200 response with a list of ApiToken objects as serialized JSONs in the body.
        """
        api_tokens = ApiToken.query.all()
        return [api_token.serialize() for api_token in api_tokens]

    @staticmethod
    @auth.login_required(role="super admin")
    def post():
        """
        POST method handler to create a new ApiToken object for a user into the database.
        User for the token must be specified in query parameter 'user'. Query parameter
        'role' can optionally be given to give the token a specific role. Default value creates a
        regular admin token.

        :return: HTTP201 response with the created ApiToken object serialized in the response body.
        :raises BadRequest: HTTP400 error if user query parameter is missing or is invalid.
        :raises Conflict: HTTP409 error if a token for the user already exists.
        """
        try:
            user = request.args["user"]
            role = request.args.get("role")
        except KeyError as e:
            msg = "Query parameter user is required to create an API token."
            raise BadRequest(description=msg) from e

        keyring = current_app.config["KEYRING"]
        try:
            with current_app.app_context():
                api_token = keyring.create_token(user, role)
        except UserCollisionError as e:
            raise Conflict(description=f"Token for user {user} already exists.") from e
        except ValueError as e:
            raise BadRequest(str(e)) from e

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
