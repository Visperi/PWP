"""
Generate a key for user without the API interface.
Use this module to generate the first API key.
"""
from ranking_api.app import create_app
from ranking_api.authentication import Keyring


if __name__ == "__main__":
    USER = "admin"

    app = create_app()
    with app.app_context():
        keyring: Keyring = app.config["KEYRING"]
        try:
            token = keyring.create_token(USER)
            print(f"Generated a new token for user {USER}. The key is: {token}")
        except ValueError:
            token = keyring.update_token(USER)
            print(f"Updated an existing token for {USER}. The new token is: {token}")
        print("This key is valid only in production!")
