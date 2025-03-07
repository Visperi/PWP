"""
Module containing tests for API authentication and the related backend functionality.
"""
import uuid
from datetime import datetime, timezone, timedelta

import pytest

from ranking_api.extensions import db
from ranking_api.authentication import Keyring
from ranking_api.secret_models import ApiToken
from populate_database import generate_match, generate_player


class TestKeyring:
    """
    Tests for the Keyring object handling API tokens.
    """

    @pytest.fixture(scope="function")
    def keyring(self, test_app):
        """
        Get a reference to the test applications Keyring.
        """
        yield test_app.config.get("KEYRING")
        db.drop_all()
        db.create_all()

    @pytest.fixture(scope="function", autouse=True)
    def _provide_app_context(self, test_app):
        """
        Get app context to prevent explicit with app_context call.
        """
        with test_app.app_context():
            yield

    def test_keyring_exists(self, keyring):
        """
        Test the keyring object actually exists within the Flask application.
        """
        assert keyring is not None

    def test_add_token(self, keyring):
        """
        Test the Keyring.add functionality.
        """
        user = "testing"
        token = keyring.create_token(user)
        uuid.UUID(str(token))  # Validate the generated token

        assert keyring.get(str(token)) is not None
        assert token.expires_in is None
        assert token.created_at < datetime.now(timezone.utc).replace(tzinfo=None)
        assert token.user == user
        assert token.is_expired is False

    def test_falsy_username_fails_token_creation(self, keyring):
        """
        Test that creating a token with non-string, empty string, or white space only string fails.
        """
        with pytest.raises(ValueError):
            keyring.create_token("")
            keyring.create_token(" ")
            keyring.create_token(1)
            keyring.create_token(None)

    def test_creating_second_token_raises(self, keyring):
        """
        Test that attempting to add a second token for user raises an exception.
        """
        user = "testing"
        keyring.create_token(user)

        with pytest.raises(ValueError):
            keyring.create_token(user)

    def test_update_token(self, keyring):
        """
        Test the Keyring.update functionality.
        """
        user = "testing"
        # Copy old token to prevent old and new tokens pointing to the same updated ApiToken object
        tmp = keyring.create_token(user)
        old_token = ApiToken(token=tmp.token,
                             user=tmp.user,
                             expires_in=tmp.expires_in,
                             created_at=tmp.created_at)
        new_token = keyring.update_token(user)

        assert keyring.get(str(old_token)) is None
        assert keyring.get(str(new_token)) is not None
        assert str(old_token) != str(new_token)
        assert old_token.created_at != new_token.created_at
        assert old_token.user == new_token.user

    def test_updating_nonexistent_raises(self, keyring):
        """
        Test that attempting to update token for nonexistent ApiToken raises an exception.
        """
        with pytest.raises(ValueError):
            keyring.update_token("Token for this user does not exist")

    def test_keyring_get(self, keyring):
        """
        Test the Keyring.get functionality.
        """
        token = keyring.create_token("testing")

        assert keyring.get("Nonexistent token") is None
        assert isinstance(keyring.get(str(token)), ApiToken)

    def test_delete_token(self, keyring):
        """
        Test the Keyring.delete functionality.
        """
        user = "testing"
        token = keyring.create_token(user)
        keyring.delete_token(user)

        assert keyring.get(str(token)) is None
        # Attempt to delete now nonexistent token
        with pytest.raises(ValueError):
            keyring.delete_token(str(token))

    def test_keyring_persistence(self, keyring):
        """
        Test that the keyring data is persistent between sessions, i.e. tokens are correctly
        saved in database.
        """
        user = "testing"
        token = keyring.create_token(user)
        keyring = Keyring()  # Reset keyring
        assert keyring.get(str(token)) is not None

        keyring.delete_token(str(user))
        keyring = Keyring()
        assert keyring.get(str(token)) is None

        tmp = keyring.create_token(user)
        old_token = ApiToken(token=tmp.token,
                             user=tmp.user,
                             expires_in=tmp.expires_in,
                             created_at=tmp.created_at)
        new_token = keyring.update_token(tmp.user)
        keyring = Keyring()
        assert keyring.get(str(old_token)) is None
        assert keyring.get(str(new_token)) is not None


class TestApiToken:
    """
    Tests for the actual ApiToken object used by Keyring.
    """

    def test_str(self):
        """
        Test str call to ApiToken returns the actual token.
        """
        token = "some token"
        api_token = ApiToken(token=token)

        assert str(api_token) == token

    def test_is_expired(self):
        """
        Test the ApiToken.is_expired functionality.
        """
        api_token = ApiToken(expires_in=None)
        assert api_token.is_expired is False

        expires_in = datetime.now(timezone.utc) - timedelta(seconds=1)
        api_token = ApiToken(expires_in=expires_in)
        assert api_token.is_expired is True

        expires_in = datetime.now(timezone.utc) + timedelta(seconds=1)
        api_token = ApiToken(expires_in=expires_in)
        assert api_token.is_expired is False

class TestApiAuthentication:
    """
    Tests for testing authentication against the actual API.
    """

    PLAYERS_URL = "/api/players/"
    MATCHES_URL = "/api/matches/"

    @pytest.fixture(scope="class")
    def match_id(self, test_app):
        """
        Create a match and get its ID as string.
        """
        match = generate_match()
        with test_app.app_context():
            db.session.add(match)
            db.session.commit()
            return str(match.id)

    @pytest.fixture(scope="class")
    def player_username(self, test_app):
        """
        Create a player and get its username.
        """
        player = generate_player()
        with test_app.app_context():
            db.session.add(player)
            db.session.commit()
            return player.username

    @pytest.fixture(scope="class")
    def auth_header(self, test_app):
        """
        Get authorization header for requests requiring authentication.
        """
        with test_app.app_context():
            api_token = test_app.config["KEYRING"].create_token("test_user")
            return {"Authorization": f"Bearer {api_token}"}

    def test_gets_pass_without_auth(self, test_client, player_username, match_id):
        """
        Test that GET requests to all resources are successful without providing API token.
        """
        assert test_client.get(self.PLAYERS_URL).status_code == 200
        assert test_client.get(self.MATCHES_URL).status_code == 200
        assert test_client.get(self.PLAYERS_URL + player_username,
                               follow_redirects=True).status_code == 200
        assert test_client.get(self.MATCHES_URL + match_id,
                               follow_redirects=True).status_code == 200

    def test_posts_fail_without_auth(self, test_client, player_username, match_id):
        """
        Test that all POST requests fail without providing API token.
        """
        assert test_client.post(self.PLAYERS_URL).status_code == 401
        assert test_client.post(self.MATCHES_URL).status_code == 401
        assert test_client.post(self.PLAYERS_URL + player_username,
                                follow_redirects=True).status_code == 401
        assert test_client.post(self.MATCHES_URL + match_id,
                                follow_redirects=True).status_code == 401

    def test_deletes_fail_without_auth(self, test_client, player_username, match_id):
        """
        Test that all DELETE requests fail without providing API token.
        """
        assert test_client.post(self.PLAYERS_URL + player_username,
                                follow_redirects=True).status_code == 401
        assert test_client.post(self.MATCHES_URL + match_id,
                                follow_redirects=True).status_code == 401

    def test_posts_success_with_auth(self, test_client, auth_header, player_username, match_id):
        """
        Test that all POST requests are processed when API token is provided.
        """
        assert test_client.post(self.PLAYERS_URL,
                                follow_redirects=True,
                                headers=auth_header).status_code != 401
        assert test_client.post(self.MATCHES_URL,
                                follow_redirects=True,
                                headers=auth_header).status_code != 401

        with pytest.raises(NotImplementedError):
            assert test_client.post(self.PLAYERS_URL + player_username,
                                    follow_redirects=True,
                                    headers=auth_header).status_code != 401
            assert test_client.post(self.MATCHES_URL + match_id,
                                    follow_redirects=True,
                                    headers=auth_header).status_code != 401

    def test_deletes_success_with_auth(self, test_client, auth_header, player_username, match_id):
        """
        Test that all DELETE requests are processed when API token is provided.
        """
        assert test_client.delete(self.PLAYERS_URL + player_username,
                                  follow_redirects=True,
                                  headers=auth_header).status_code == 204
        assert test_client.delete(self.MATCHES_URL + match_id,
                                  follow_redirects=True,
                                  headers=auth_header).status_code == 204
