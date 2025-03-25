from flask import request, current_app, Response
from flask_restful import Resource

from werkzeug.routing import BaseConverter
from werkzeug.exceptions import Conflict, BadRequest, NotFound

from ranking_api.authentication import auth
from ranking_api.secret_models import ApiToken
from ranking_api.extensions import db

# TODO: Add roles

class ApiTokenItem(Resource):

    @staticmethod
    @auth.login_required
    def get(api_token: ApiToken):
        return api_token.serialize()

    @staticmethod
    @auth.login_required
    def delete(api_token: ApiToken):
        db.session.delete(api_token)
        db.session.commit()
        return Response(status=204)

    @staticmethod
    @auth.login_required
    def patch(api_token: ApiToken):
        keyring = current_app.config["KEYRING"]
        api_token = keyring.update_token(api_token.user)
        return api_token.serialize(), 200


class ApiTokenCollection(Resource):

    @staticmethod
    @auth.login_required
    def get():
        api_tokens = ApiToken.query.all()
        return [api_token.serialize() for api_token in api_tokens]

    @staticmethod
    @auth.login_required
    def post():
        try:
            user = request.args["user"]
        except KeyError:
            raise BadRequest(description="Query parameter user is required to create an API token.")

        keyring = current_app.config["KEYRING"]
        try:
            with current_app.app_context():
                api_token = keyring.create_token(user)
        except ValueError as e:
            raise Conflict(description=f"Token for user {user} already exists.") from e

        return api_token.serialize(), 201


class ApiTokenConverter(BaseConverter):

    def to_python(self, value: str) -> ApiToken:
        api_token = ApiToken.query.filter_by(user=value).first()
        if api_token is None:
            raise NotFound(description=f"No such API token with user {value}")
        return api_token

    def to_url(self, value: ApiToken) -> str:
        return value.user
