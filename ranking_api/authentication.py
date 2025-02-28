"""
A module responsible for token authentication handling. Import this module where authentication is needed.
"""

import uuid
from typing import Any, Dict, Union
from datetime import datetime

from flask import current_app

from ranking_api.extensions import auth, db
from ranking_api.models import ApiToken


class Keyring:

    def __init__(self):
        """
        A keyring object that handles API tokens for the application.
        """
        self._tokens: Dict[str, ApiToken] = {}
        if not current_app.debug:
            self.__read_persistent_tokens()
        else:
            dev_token = self.create_token("development_admin")
            self._tokens[dev_token.token] = dev_token
            print(f"Your development API token is: {dev_token.token}")

    def __read_persistent_tokens(self):
        """
        Read existing API tokens from database into the keyring.
        """
        tokens = {}
        for api_token in ApiToken.query.all():
            tokens[api_token.token] = api_token

        self._tokens = tokens

    def get(self, token: str, default: Any = None) -> Union[ApiToken, Any]:
        """
        Get ApiToken object from the keyring. Return the default value if it does not exist.

        :param token: The token to search for in the keyring.
        :param default: Value to return if the token does not exist.
        :return: ApiToken corresponding the token or the default value.
        """
        return self._tokens.get(token, default)

    def create_token(self, user: str) -> ApiToken:
        """
        Create a new API token and add the token into the keyring.
        If current_app is in debug mode, the token is not saved into database.

        :param user: User to create the API token for.
        :return: The newly created ApiToken object.
        """
        token = uuid.uuid4()
        api_token = ApiToken(token=str(token),
                             user=user,
                             expires_in=None,
                             created_at=datetime.now())

        if not current_app.debug:
            db.session.add(api_token)
            db.session.commit()

        self._tokens[api_token.token] = api_token
        return api_token

    def delete_token(self, token: str):
        """
        Delete a token from the keyring and database.

        :param token: The token to remove.
        :raises KeyError: If the token is not in the keyring.
        """
        self._tokens.pop(token)

        if not current_app.debug:
            existing_token = ApiToken.query.filter_by(token=token).first()
            if not existing_token:
                return

            db.session.delete(existing_token)
            db.session.commit()


@auth.verify_token
def verify_token(token: str):
    keyring = current_app.config["KEYRING"]
    return keyring.get(token)
