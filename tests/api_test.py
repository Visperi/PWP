"""
Module for testing application api endpoints
"""
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
        player, _ = self.__create_player(test_client, auth_header)
        player.num_of_matches = 1337

        # TODO change this after put is implemented
        with pytest.raises(NotImplementedError):
            test_client.post(f"{self.RESOURCE_URL}{player.username}/",
                             json=player.serialize(),
                             headers=auth_header)


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
        new_match, _ = self.__create_match(test_client, auth_header)
        new_match.location = new_match.location[:-1]
        with pytest.raises(NotImplementedError):
            test_client.post(f"{self.RESOURCE_URL}1/",
                             json=new_match.serialize(),
                             headers=auth_header)

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
        pass
