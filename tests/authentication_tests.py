"""
Module containing tests for API authentication and the related backend functionality.
"""
import uuid
from datetime import datetime, timezone, timedelta

import pytest

from ranking_api.extensions import db
from ranking_api.authentication import Keyring, UserCollisionError
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

    def test_get_debug_token(self, keyring):
        """
        Test the debug token is None in production.
        """
        assert keyring.debug_token is None

    def test_create_token(self, keyring):
        """
        Test the Keyring.create_token functionality.
        """
        user = "testing"
        token = keyring.create_token(user)
        uuid.UUID(str(token))  # Validate the generated token

        assert keyring.get(str(token)) is not None
        assert token.expires_in is None
        assert token.created_at < datetime.now(timezone.utc).replace(tzinfo=None)
        assert token.user == user
        assert token.is_expired is False

    @pytest.mark.parametrize("username", ("", " ", 1, None))
    def test_invalid_username_fails_token_creation(self, keyring, username):
        """
        Test that creating a token with non-string, empty string, or white space only string fails.
        """
        with pytest.raises(ValueError):
            keyring.create_token(username)

    def test_creating_second_token_raises(self, keyring):
        """
        Test that attempting to add a second token for user raises an exception.
        """
        user = "testing"
        keyring.create_token(user)

        with pytest.raises(UserCollisionError):
            keyring.create_token(user)

    def test_update_token(self, keyring):
        """
        Test the Keyring.update_token functionality.
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
        Test the Keyring.delete_token functionality.
        """
        user = "testing"
        token = keyring.create_token(user)
        keyring.delete_token(user)

        assert keyring.get(str(token)) is None
        # Attempt to delete now nonexistent token
        with pytest.raises(ValueError):
            keyring.delete_token(token.user)

    def test_keyring_persistence(self, keyring):
        """
        Test that the keyring data is persistent between sessions, i.e. tokens are correctly
        saved in database.
        """
        user = "testing"
        token = keyring.create_token(user)
        keyring = Keyring()  # Reset keyring
        assert keyring.get(str(token)) is not None

        keyring.delete_token(user)
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

    def test_serialize(self):
        """
        Test the ApiToken serialization functionality.
        """

        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        api_token = ApiToken(token="some token",
                             user="testing",
                             role="my role",
                             expires_in=current_time,
                             created_at=current_time)

        assert api_token.serialize() == {"token": "some token",
                                         "user": "testing",
                                         "role": "my role",
                                         "expires_in": str(current_time),
                                         "created_at": str(current_time)}

    def test_is_expired(self):
        """
        Test the ApiToken.is_expired functionality.
        """
        api_token = ApiToken(expires_in=None)
        assert api_token.is_expired is False

        expires_in = datetime.now(timezone.utc) - timedelta(seconds=1)
        api_token = ApiToken(expires_in=expires_in.replace(tzinfo=None))
        assert api_token.is_expired is True

        expires_in = datetime.now(timezone.utc) + timedelta(seconds=1)
        api_token = ApiToken(expires_in=expires_in.replace(tzinfo=None))
        assert api_token.is_expired is False

class TestApiAuthentication:
    """
    Tests for testing authentication against the actual API.
    """

    PLAYERS_URL = "/api/players/"
    MATCHES_URL = "/api/matches/"

    @pytest.fixture(scope="function")
    def match_id(self, test_app):
        """
        Create a match and get its ID as string.
        """
        match = generate_match()
        with test_app.app_context():
            db.session.add(match)
            db.session.commit()
            return str(match.id)

    @pytest.fixture(scope="function")
    def player_username(self, test_app):
        """
        Create a player and get its username.
        """
        player = generate_player()
        with test_app.app_context():
            db.session.add(player)
            db.session.commit()
            return player.username

    @pytest.mark.parametrize("url,fixture", (
            (PLAYERS_URL, None),
            (MATCHES_URL, None),
            (PLAYERS_URL, "player_username"),
            (MATCHES_URL, "match_id")
    ))
    def test_gets_pass_without_auth(self, test_client, request, url, fixture):
        """
        Test that GET requests to all resources except api_token are successful
        without providing API token.
        """
        request_url = url
        if fixture:
            request_url += request.getfixturevalue(fixture)

        assert test_client.get(request_url, follow_redirects=True).status_code == 200

    @pytest.mark.parametrize("url", (PLAYERS_URL, MATCHES_URL))
    def test_posts_fail_without_auth(self, test_client, url):
        """
        Test that all POST requests fail without providing API token.
        """
        request_url = url

        assert test_client.post(request_url, follow_redirects=True).status_code == 401

    @pytest.mark.parametrize("url,fixture", (
            (PLAYERS_URL, "player_username"),
            (MATCHES_URL, "match_id")
    ))
    def test_deletes_fail_without_auth(self, test_client, request, url, fixture):
        """
        Test that all DELETE requests fail without providing API token.
        """
        request_url = url
        if fixture:
            request_url += request.getfixturevalue(fixture)

        assert test_client.delete(request_url, follow_redirects=True).status_code == 401

    @pytest.mark.parametrize("url", (PLAYERS_URL, MATCHES_URL))
    def test_posts_success_with_auth(self, test_client, auth_header, url):
        """
        Test that all POST requests are processed when API token is provided.
        """

        assert test_client.post(url,
                                headers=auth_header,
                                follow_redirects=True).status_code != 401

    @pytest.mark.parametrize("url,fixture", (
            (PLAYERS_URL, "player_username"),
            (MATCHES_URL, "match_id")
    ))
    def test_deletes_success_with_auth(self, test_client, auth_header, request, url, fixture):  # pylint: disable=R0913,R0917
        """
        Test that all DELETE requests are processed when API token is provided.
        """
        request_url = url
        if fixture:
            request_url += request.getfixturevalue(fixture)

        assert test_client.delete(request_url,
                                  headers=auth_header,
                                  follow_redirects=True).status_code == 204

    @pytest.mark.parametrize("url,fixture", (
            (PLAYERS_URL, "player_username"),
            (MATCHES_URL, "match_id")
    ))
    def test_put_fails_without_auth(self, test_client, request, url, fixture):
        """
        Test that PUT requests fail without proper Authorization header.
        """
        request_url = url + request.getfixturevalue(fixture)
        assert test_client.put(request_url, follow_redirects=True).status_code == 401

    @pytest.mark.parametrize("url,fixture", (
            (PLAYERS_URL, "player_username"),
            (MATCHES_URL, "match_id")
    ))
    def test_puts_success_with_auth(self,
                                    test_client,
                                    auth_header,
                                    request,
                                    url,
                                    fixture):
        """
        Test PUT requests are processed with proper Authorization header.
        """
        # pylint: disable=R0913,R0917

        request_url = url + request.getfixturevalue(fixture)
        assert test_client.put(request_url,
                               headers=auth_header,
                               follow_redirects=True).status_code != 401


class TestApiTokenApiAuthentication:
    """
    Test that api_token resource HTTP methods are
    correctly processed or not processed with different authorization headers.
    """

    TOKENS_URL = "/api/tokens/"

    @pytest.fixture(scope="function")
    def token_user(self, test_app):
        """
        Create a token to the test app keyring and get the token user.
        """
        keyring = test_app.config["KEYRING"]
        with test_app.app_context():
            api_token = keyring.create_token("testing")
            return api_token.user

    @pytest.mark.parametrize("url, fixture", (
            (TOKENS_URL, None),
            (TOKENS_URL, "token_user")
    ))
    def test_get_tokens_fail_with_invalid_auth(self,
                                               test_client,
                                               auth_header,
                                               url,
                                               request,
                                               fixture):
        """
        Test that GET requests to get API tokens are not processed
        without token or with token without super admin rights.
        """
        # pylint: disable=R0917,R0913
        request_url = url
        if fixture:
            request_url += request.getfixturevalue(fixture)

        assert test_client.get(request_url,
                               follow_redirects=True).status_code == 401
        assert test_client.get(request_url,
                               headers=auth_header,
                               follow_redirects=True).status_code == 403

    def test_create_token_fails_with_invalid_auth(self, test_client, auth_header, token_user):
        """
        Test that POST requests to create new APi tokens are not processed without
        token or with token with no super admin rights.
        """
        request_url = self.TOKENS_URL + f"?user{token_user}"

        assert test_client.post(request_url).status_code == 401
        assert test_client.post(request_url, headers=auth_header).status_code == 403

    def test_delete_token_fails_with_invalid_auth(self, test_client, auth_header, token_user):
        """
        Test that DELETE requests to delete API tokens are not processed
        without token or with token without super admin rights.
        """
        request_url = self.TOKENS_URL + token_user

        assert test_client.delete(request_url,
                                  follow_redirects=True).status_code == 401
        assert test_client.delete(request_url,
                                  headers=auth_header,
                                  follow_redirects=True).status_code == 403

    def test_patch_token_fails_with_invalid_auth(self, test_client, auth_header, token_user):
        """
        Test that PATCH requests to update API tokens are not processed without
        token or with token without super admin rights.
        """
        request_url = self.TOKENS_URL + token_user

        assert test_client.patch(request_url,
                                 follow_redirects=True).status_code == 401
        assert test_client.patch(request_url,
                                 headers=auth_header,
                                 follow_redirects=True).status_code == 403

    @pytest.mark.parametrize("fixture", (None, "token_user"))
    def test_get_tokens_success_with_auth(self,
                                          test_client,
                                          auth_header_superadmin,
                                          request,
                                          fixture):
        """
        Test that GET requests to get API tokens are processed with super admin token.
        """
        request_url = self.TOKENS_URL
        if fixture:
            request_url += request.getfixturevalue(fixture)

        resp = test_client.get(request_url, headers=auth_header_superadmin, follow_redirects=True)
        assert resp.status_code not in [401, 403]

    def test_create_token_success_with_auth(self, test_client, auth_header_superadmin):
        """
        Test that POST requests to create new API tokens are processed with super admin token.
        """
        resp = test_client.post(self.TOKENS_URL,
                                headers=auth_header_superadmin,
                                follow_redirects=True)

        assert resp.status_code not in [401, 403]

    def test_delete_token_success_with_auth(self, test_client, auth_header_superadmin, token_user):
        """
        Test that DELETE requests to delete API tokens are processed with super admin token.
        """
        resp = test_client.delete(self.TOKENS_URL + token_user,
                                  headers=auth_header_superadmin,
                                  follow_redirects=True)

        assert resp.status_code not in [401, 403]

    def test_patch_token_success_with_auth(self, test_client, token_user, auth_header_superadmin):
        """
        Test that PATCH requests to update API token are processed with super admin token.
        """
        resp = test_client.patch(self.TOKENS_URL + token_user,
                                 headers=auth_header_superadmin,
                                 follow_redirects=True)

        assert resp.status_code not in [401, 403]
