"""
A module responsible for token authentication handling. Import this module where authentication is needed.
"""

from typing import Any

from ranking_api.extensions import auth


class Keyring:

    def __init__(self):
        self._tokens = {}
        self.__read_existing_tokens()

    def get(self, value: str, default: Any = None):
        return self._tokens.get(value, default)

    def add_token(self, token: str, user: str):
        # TODO: Save the token to a persistent storage
        self._tokens[token] = user

    def delete_token(self, token):
        # TODO: Delete the token from the persistent storage
        self._tokens.pop(token)

    def __read_existing_tokens(self):
        self._tokens = {"asd": "admin"}


@auth.verify_token
def verify_token(token: str):
    return keyring.get(token)


keyring = Keyring()
