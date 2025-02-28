"""
A module responsible for token authentication handling.
Import this module where authentication is needed.
"""

import uuid
from typing import Any, Dict, Union, Optional
from datetime import datetime, timezone

from flask import current_app

from ranking_api.extensions import auth, db
from ranking_api.secret_models import ApiToken


class Keyring:
    """
    A keyring object that handles API tokens for the application.
    """

    def __init__(self):
        """
        A keyring object that handles API tokens for the application.
        """
        self._tokens: Dict[str, ApiToken] = {}
        if not current_app.debug:
            self.__read_persistent_tokens()
        else:
            dev_token = self.create_token("development_admin")
            self._tokens[str(dev_token)] = dev_token
            print(f"Your development API token is: {dev_token.token}")

    @staticmethod
    def __generate_token():
        return uuid.uuid4()

    def __read_persistent_tokens(self):
        """
        Read existing API tokens from database into the keyring.
        """
        for api_token in ApiToken.query.all():
            self._tokens[api_token.token] = api_token

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
        :raises ValueError: If a token for the user already exists.
        """
        if ApiToken.query.filter_by(user=user).first():
            raise ValueError(f"API token for user {user} already exists. Use update_token to "
                             f"generate a new token for existing ApiToken.")

        api_token = ApiToken(token=str(self.__generate_token()),
                             user=user,
                             expires_in=None,
                             created_at=datetime.now(timezone.utc))

        if not current_app.debug:
            db.session.add(api_token)
            db.session.commit()

        self._tokens[api_token.token] = api_token
        return api_token

    def update_token(self, user: str) -> ApiToken:
        """
        Update an API token for user. If current_app is in debug mode,
        the token is not saved into database.

        :param user: User to update the API token for.
        :return: The updated ApiToken object.
        :raises ValueError: If a token for the user does not exist.
        """
        if not current_app.debug:
            existing_token = ApiToken.query.filter_by(user=user).first()
        else:
            existing_token = None
            for token in self._tokens.values():
                if token.user == user:
                    existing_token = token
                    break

        if not existing_token:
            raise ValueError(f"No API token for user {user} exists. Use create_token "
                             f"to create a new ApiToken.")

        existing_token.token = str(self.__generate_token())
        existing_token.created_at = datetime.now(timezone.utc)

        if not current_app.debug:
            db.session.commit()

        return existing_token

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
def verify_token(token: str) -> Optional[ApiToken]:
    """
    Verify a token against approved tokens stored in the keyring.

    :param token: A token provided by user in a request.
    :return: ApiToken object corresponding the object if the token is valid, None otherwise.
    """
    keyring = current_app.config["KEYRING"]
    return keyring.get(token)
