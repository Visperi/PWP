"""
Module for testing application api endpoints
"""
from datetime import datetime, timezone, timedelta

import pytest

import populate_database


class TestPlayerModel:
    """
    Test behavior for player api resources
    """

    RESOURCE_URL = "/api/players/"

    def __create_player(self, test_client, auth_header):
        new_player = populate_database.generate_player()
        response = test_client.post(self.RESOURCE_URL,
                                    json=new_player.serialize(),
                                    headers=auth_header)
        return new_player, response

    def test_create_player(self, test_client, auth_header):
        """Test creating a new player"""
        new_player, response = self.__create_player(test_client, auth_header)
        assert response.status_code == 201
        resp_pname = response.headers["Location"].split("/")[-2]
        assert resp_pname == new_player.username

    def test_create_player_invalid_datatype(self, test_client, auth_header):
        """Test insert invalid datatype"""
        new_player = populate_database.generate_player()
        response = test_client.post(
            self.RESOURCE_URL,
            json=new_player.username,
            mimetype="text/plain",
            headers=auth_header
            )
        assert response.status_code == 415

    def test_create_player_invalid_json(self, test_client, auth_header):
        """Test insert invalid json"""
        new_player = populate_database.generate_player().serialize()
        del new_player["username"]
        response = test_client.post(self.RESOURCE_URL, json=new_player, headers=auth_header)
        assert response.status_code == 400

    def test_nok_create_player(self, test_client, auth_header):
        """Test to add existing player"""
        player, _ = self.__create_player(test_client, auth_header)
        response = test_client.post(self.RESOURCE_URL, json=player.serialize(), headers=auth_header)
        assert response.status_code == 409

    def test_get_player(self, test_client, auth_header):
        """Test retrieving a single player"""
        player, _ = self.__create_player(test_client, auth_header)
        response = test_client.get(f"{self.RESOURCE_URL}{player.username}/")
        assert player.serialize() == response.json

    def test_get_players(self, test_client, auth_header):
        """Test retrieving all players"""
        # create 2 players
        self.__create_player(test_client, auth_header)
        self.__create_player(test_client, auth_header)

        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 2

    def test_delete_player(self, test_client, auth_header):
        """Delete player"""
        player, _ = self.__create_player(test_client, auth_header)
        response = test_client.delete(f"{self.RESOURCE_URL}{player.username}/", headers=auth_header)
        assert response.status_code == 204

    def test_nok_delete_player(self, test_client, auth_header):
        """Try deleting player that doesn't exist"""
        name = "xyz"
        response = test_client.delete(f"{self.RESOURCE_URL}{name}/", headers=auth_header)
        assert response.status_code == 404

    def test_update_player(self, test_client, auth_header):
        """Try updating existing player"""
        new_attrs = {"username": "test",
                     "num_of_matches": 1337,
                     "rating": 12345}

        player, _ = self.__create_player(test_client, auth_header)
        original_name = player.username
        for attr_name, attr_value in new_attrs.items():
            setattr(player, attr_name, attr_value)

        response = test_client.put(f"{self.RESOURCE_URL}{original_name}/",
                                   json=player.serialize(),
                                   headers=auth_header)
        assert response.status_code == 200

        updated_player = test_client.get(response.headers["Location"]).json
        for attr_name, attr_value in updated_player.items():
            assert updated_player[attr_name] == attr_value

    def test_missing_put_fields_raises(self, test_client, auth_header):
        """
        Test that not giving all object fields on PUT requests returns Bad Request error.
        """
        _, resp = self.__create_player(test_client, auth_header)
        response = test_client.put(resp.headers["Location"],
                                   json={"username": "testing"},
                                   headers=auth_header)
        assert response.status_code == 400

    def test_put_validation(self, test_client, auth_header):
        """
        Test the field validation on PUT requests.
        """
        data = {"username": 564323,
                "num_of_matches": 0,
                "rating": 0}

        _, resp = self.__create_player(test_client, auth_header)
        response = test_client.put(resp.headers["Location"],
                                   json=data,
                                   headers=auth_header)
        assert response.status_code == 400

class TestMatchModel:
    """
    Test match api endpoint behavior
    """
    RESOURCE_URL = "/api/matches/"

    def __create_match(self, test_client, auth_header):
        new_match = populate_database.generate_match()
        response = test_client.post(self.RESOURCE_URL,
                                    json=new_match.serialize(),
                                    headers=auth_header)
        return new_match, response

    def test_create_match(self, test_client, auth_header):
        """Test creating a new match."""
        _, response = self.__create_match(test_client, auth_header)
        assert response.status_code == 201

    def test_create_match_invalid_json(self, test_client, auth_header):
        """Test create match with invalid json in request"""
        new_match, _ = self.__create_match(test_client, auth_header)
        new_match = new_match.serialize()
        del new_match["location"]
        response = test_client.post(self.RESOURCE_URL, json=new_match, headers=auth_header)
        assert response.status_code == 400

    def test_get_match(self, test_client, auth_header):
        """Test get single match"""

        new_match, _ = self.__create_match(test_client, auth_header)
        response = test_client.get(f"{self.RESOURCE_URL}1/", headers=auth_header)
        assert response.status_code == 200
        assert response.json["location"] == new_match.location

    def test_get_matches(self, test_client, auth_header):
        """Test retrieving all matches."""
        self.__create_match(test_client, auth_header)
        self.__create_match(test_client, auth_header)

        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 2

    def test_delete_match(self, test_client, auth_header):
        """Test deleting a match"""
        self.__create_match(test_client, auth_header)
        response = test_client.delete(f"{self.RESOURCE_URL}1/", headers=auth_header)
        assert response.status_code == 204

    def test_update_match(self, test_client, auth_header):
        """Test updating existing match"""
        new_attrs = {"location": "test area",
                     "time": datetime.now(timezone.utc) + timedelta(hours=1),
                     "description": "testing testing",
                     "status": 2,
                     "rating_shift": 50,
                     "team1_score": 1,
                     "team2_score": 2}

        new_match, resp = self.__create_match(test_client, auth_header)
        for attr_name, attr_value in new_attrs.items():
            setattr(new_match, attr_name, attr_value)

        response = test_client.put(resp.headers["Location"],
                                   json=new_match.serialize(),
                                   headers=auth_header)
        assert response.status_code == 200

        updated_match = test_client.get(resp.headers["Location"]).json
        for attr_name, attr_value in new_attrs.items():
            if attr_name == "time":
                assert updated_match[attr_name] == str(attr_value.replace(tzinfo=None))
            else:
                assert updated_match[attr_name] == attr_value

    def test_missing_put_field_raises(self, test_client, auth_header):
        """
        Test that not giving all object fields on PUT requests returns Bad Request error.
        """
        _, resp = self.__create_match(test_client, auth_header)
        response = test_client.put(resp.headers["Location"],
                                   json={"location": "testing"},
                                   headers=auth_header)
        assert response.status_code == 400

    def test_put_validation(self, test_client, auth_header):
        """
        Test the field validation on PUT requests.
        """
        data = {"location": "test area",
                "time": 12345,  # The invalid field
                "description": "testing testing",
                "status": 2,
                "rating_shift": 50,
                "team1_score": 1,
                "team2_score": 2}

        _, resp = self.__create_match(test_client, auth_header)
        response = test_client.put(resp.headers["Location"],
                                   json=data,
                                   headers=auth_header)
        assert response.status_code == 400

    def test_match_conversion(self, test_client):
        """
        Test match conversion raises notfound error
        """
        response = test_client.get(f"{self.RESOURCE_URL}400/")
        assert response.status_code == 404

class TestMatchPlayerRelation:
    """
    Test matchplayer relation behavior in the api
    """

    PLAYER_URL = "/api/players/"
    MATCH_URL = "/api/matches/"

    # Match joining is NOT implemented yet TODO
    def test_join_match(self, test_client, auth_header):
        """Test associating a player with a match."""
        # Get first player
        new_player = populate_database.generate_player()
        player_response = test_client.post(self.PLAYER_URL,
                                           json=new_player.serialize(),
                                           headers=auth_header)
        assert player_response.status_code == 201

        # Create match
        match = populate_database.generate_match()
        response = test_client.post(self.MATCH_URL, json=match.serialize(), headers=auth_header)
        assert response.status_code == 201

        # Join match
    def test_leave_match(self, test_client):
        """Test player leaving match"""
        # leave

class TestSeasonModel:
    """
    Test season api endpoint behavior
    """

    RESOURCE_URL = "/api/seasons/"

    def __create_season(self, test_client, auth_header):
        new_season = populate_database.generate_season()
        response = test_client.post(self.RESOURCE_URL,
                                    json=new_season.serialize(),
                                    headers=auth_header)
        return new_season, response

    def test_create_season(self, test_client, auth_header):
        """Test creating a new season"""
        _, resp = self.__create_season(test_client, auth_header)
        assert resp.status_code == 201

    def test_create_season_invalid_json(self, test_client, auth_header):
        """Test create new season with invalid json in request"""
        new_season, _ = self.__create_season(test_client, auth_header)
        new_season = new_season.serialize()
        del new_season["starting_date"]
        response = test_client.post(
            self.RESOURCE_URL,
            json=new_season,
            headers=auth_header
            )
        assert response.status_code == 400

    def test_get_season(self, test_client, auth_header):
        """Test get single season"""
        new_season, _ = self.__create_season(test_client, auth_header)
        response = test_client.get(f"{self.RESOURCE_URL}2/", headers=auth_header)
        assert response.status_code == 200
        assert response.json["end_date"] == str(new_season.end_date)

    def test_get_seasons(self, test_client, auth_header):
        """Test get all seasons"""
        self.__create_season(test_client, auth_header)

        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 2

    def test_delete_season(self, test_client, auth_header):
        """Test delete a season (drunk admin favorite)"""
        response = test_client.delete(f"{self.RESOURCE_URL}1/", headers=auth_header)
        assert response.status_code == 204
        resp = test_client.get(self.RESOURCE_URL)
        assert len(resp.json) == 0

    def test_update_season(self, test_client, auth_header):
        """Test updating existing season"""
        new_attrs = {
            "starting_date": datetime.now(timezone.utc) + timedelta(hours=1),
            "end_date": datetime.now(timezone.utc) + timedelta(hours=2)
        }

        new_season, resp = self.__create_season(test_client, auth_header)
        for attr_name, attr_value in new_attrs.items():
            setattr(new_season, attr_name, attr_value)

        response = test_client.put(resp.headers["Location"],
                                   json=new_season.serialize(),
                                   headers=auth_header)
        assert response.status_code == 200

        updated_season = test_client.get(resp.headers["Location"]).json
        for attr_name, attr_value in new_attrs.items():
            if attr_name in ("end_date", "starting_date"):
                assert updated_season[attr_name] == str(attr_value.replace(tzinfo=None))
            else:
                assert updated_season[attr_name] == attr_value

    def test_get_season_invalid_id(self, test_client):
        """Test get season with an id that doesn't exist"""
        response = test_client.get(f"{self.RESOURCE_URL}1337/")
        assert response.status_code == 404

class TestApiTokenModel:
    """
    Test api_token resource methods.
    """

    TOKEN_URL = "/api/tokens/"

    @pytest.mark.parametrize("user, status_code", (
            (None, 400),  # No user query string
            ("", 400),
            (" ", 400)
    ))
    def test_create_token_invalid_user_param(self,
                                             test_client,
                                             auth_header_superadmin,
                                             user,
                                             status_code):
        """
        Test that creating a new API token with invalid user raises an error.
        """
        if user is None:
            url = self.TOKEN_URL
            expected_error = "Query parameter user is required to create an API token."
        else:
            url = self.TOKEN_URL + f"?user={user}"
            expected_error = "User must be a non-empty string."

        resp = test_client.post(url, headers=auth_header_superadmin)
        assert resp.status_code == status_code
        assert resp.json["message"] == expected_error

    def test_fetching_nonexistent_token_raises(self, test_client, auth_header_superadmin):
        """
        Test that GET request with nonexistent token user raises an error.
        """
        assert test_client.get(self.TOKEN_URL + "nonexistent",
                               headers=auth_header_superadmin,
                               follow_redirects=True).status_code == 404

    def test_create_token(self, test_client, auth_header_superadmin):
        """
        Test that sending POST request api_token resource correctly creates a new token.
        """
        assert test_client.post(self.TOKEN_URL + "?user=testing",
                                headers=auth_header_superadmin).status_code == 201

    def test_create_token_duplicate_user(self, test_client, auth_header_superadmin):
        """
        Test that sending a POST request with existing token user raises an error.
        """
        user = "testing"
        test_client.post(self.TOKEN_URL + f"?user={user}",
                         headers=auth_header_superadmin)
        assert test_client.post(self.TOKEN_URL + f"?user={user}",
                                headers=auth_header_superadmin).status_code == 409

    def test_get_tokens(self, test_client, auth_header_superadmin):
        """
        Test that GET requests to api_token resource returns list of
        serialized API tokens or a single serialized API token.
        """
        test_client.post(self.TOKEN_URL + "?user=testing",
                         headers=auth_header_superadmin)
        resp = test_client.get(self.TOKEN_URL + "testing",
                               headers=auth_header_superadmin,
                               follow_redirects=True)
        all_tokens = test_client.get(self.TOKEN_URL,
                                     headers=auth_header_superadmin,
                                     follow_redirects=True)

        assert resp.status_code == 200
        assert all_tokens.status_code == 200
        assert list(resp.json.keys()) == ["token", "user", "role", "expires_in", "created_at"]
        assert len(all_tokens.json) == 2  # auth_header fixtures also create tokens

    def test_delete_token(self, test_client, auth_header_superadmin):
        """
        Test that DELETE request to api_token resource correctly deletes an API token.
        """
        user = "testing"
        test_client.post(self.TOKEN_URL + f"?user={user}",
                         headers=auth_header_superadmin)
        resp = test_client.delete(self.TOKEN_URL + user,
                                  headers=auth_header_superadmin,
                                  follow_redirects=True)
        remaining_tokens = test_client.get(self.TOKEN_URL,
                                           headers=auth_header_superadmin)

        assert resp.status_code == 204
        assert len(remaining_tokens.json) == 1

    def test_patch_token(self, test_client, auth_header_superadmin):
        """
        Test that PATCH request to api_token resource correctly updates an API token.
        """
        user = "testing"
        first_token = test_client.post(self.TOKEN_URL + f"?user={user}",
                                       headers=auth_header_superadmin).json
        resp = test_client.patch(self.TOKEN_URL + user,
                                 headers=auth_header_superadmin,
                                 follow_redirects=True)
        updated_token = resp.json

        assert resp.status_code == 200
        assert first_token["token"] != updated_token["token"]
        assert first_token["created_at"] != updated_token["created_at"]
        assert first_token["user"] == updated_token["user"]
