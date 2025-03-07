"""
Module for testing application api endpoints
"""
from datetime import datetime
from ranking_api.models import Player, Match, MatchPlayerRelation
import populate_database
import json
from sqlalchemy.orm import class_mapper
import pytest


class TestPlayerCollection(object):
    """
    Test class for player resources
    """

    RESOURCE_URL = "/api/players/"

    def __create_player(self, test_client):
        new_player = populate_database.generate_player()
        response = test_client.post(self.RESOURCE_URL, json=new_player.serialize())
        return new_player, response

    def test_create_player(self, test_client):
        """Test creating a new player"""
        new_player, response = self.__create_player(test_client)
        assert response.status_code == 201
        resp_pname = response.headers["Location"].split("/")[-2]
        assert resp_pname == new_player.username

    def test_create_player_invalid_datatype(self, test_client):
        """Test insert invalid json"""
        new_player = populate_database.generate_player()
        response = test_client.post(self.RESOURCE_URL, json=new_player.username, mimetype="text/plain")
        print(response.data)
        print(response.status_code)
        assert response.status_code == 415

    def test_create_player_invalid_json(self, test_client):
        """Test insert invalid json"""
        new_player = populate_database.generate_player().serialize()
        del new_player["username"]
        response = test_client.post(self.RESOURCE_URL, json=new_player)
        assert response.status_code == 400

    def test_nok_create_player(self, test_client):
        """Test to add existing player"""
        player, _ = self.__create_player(test_client)
        response = test_client.post(self.RESOURCE_URL, json=player.serialize())
        assert response.status_code == 409

    def test_get_player(self, test_client):
        """Test retrieving a single player"""
        player, _ = self.__create_player(test_client)
        response = test_client.get(f"{self.RESOURCE_URL}{player.username}/")
        assert player.serialize() == response.json

    def test_get_players(self, test_client):
        """Test retrieving all players"""
        # create 2 players
        self.__create_player(test_client)
        self.__create_player(test_client)

        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 2

    def test_delete_player(self, test_client):
        """Delete player"""
        player, _ = self.__create_player(test_client)
        response = test_client.delete(f"{self.RESOURCE_URL}{player.username}/")
        assert response.status_code == 204

    def test_nok_delete_player(self, test_client):
        """Try deleting player that doesn't exist"""
        name = "xyz"
        response = test_client.delete(f"{self.RESOURCE_URL}{name}/")
        assert response.status_code == 404

    def test_update_player(self, test_client):
        """Try updating existing player"""
        player, _ = self.__create_player(test_client)
        player.num_of_matches = 1337

        # TODO change this after put is implemented
        with pytest.raises(NotImplementedError):
            response = test_client.post(f"{self.RESOURCE_URL}{player.username}/", json=player.serialize())
 

class TestMatchModel(object):

    RESOURCE_URL = "/api/matches/"

    def test_create_match(self, test_client):
        """Test creating a new match."""
        match = populate_database.generate_match()
        match_location = match.location
        response = test_client.post(self.RESOURCE_URL, json=match.serialize())
        assert response.status_code == 201
        assert response.json["location"] == match_location

    def test_get_matches(self, test_client):
        """Test retrieving all matches."""
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        assert isinstance(response.json, list)

class TestMatchPlayerRelation(object):

    PLAYER_URL = "/api/players/"
    MATCH_URL = "/api/matches/"

    def test_join_match(self, test_client):
        """Test associating a player with a match."""
        # Get first player
        new_player = populate_database.generate_player()
        player_response = test_client.post(self.PLAYER_URL, json=new_player.serialize())
        assert player_response.status_code == 201

        # Create match
        match = populate_database.generate_match()
        match_location = match.location
        response = test_client.post(self.MATCH_URL, json=match.serialize())
        assert response.status_code == 201
        assert response.json["location"] == match_location

        # Join match
        match_id = match.id
        join_resp = test_client.post(f"/matches/{match_id}/join", json={new_player})
        assert join_resp.status_code == 200
        assert join_resp.json["message"] == "Player added to match"
