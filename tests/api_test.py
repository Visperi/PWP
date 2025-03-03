from datetime import datetime
from ranking_api.models import Player, Match, MatchPlayerRelation
import populate_database
import json
from sqlalchemy.orm import class_mapper


class TestPlayerModel(object):

    RESOURCE_URL = "/api/players/"

    def test_create_player(self, test_client):
        """Test creating a new player."""
        new_player = populate_database.generate_player()
        player_name = new_player.username
        response = test_client.post(self.RESOURCE_URL, json=new_player.serialize())
        assert response.status_code == 201
        resp_pname = response.headers["Location"].split("/")[-2]
        assert resp_pname == player_name

    def test_get_players(self, test_client):
        """Test retrieving all players."""
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        assert isinstance(response.json, list)

    def test_NOK_create_player(self, test_client):
        """Test to add existing player"""
        response = test_client.get(self.RESOURCE_URL)
        players = response.get_json()
        player1 = players[0]
        resp = test_client.post(self.RESOURCE_URL, json=player1)
        assert resp.status_code == 409

    def test_delete_player(self, test_client):
        """delete player"""
        response = test_client.get(self.RESOURCE_URL)
        players = response.get_json()
        player1 = players[0]
        resp = test_client.delete("/api/player/", json=player1)
        assert resp.status_code == 204

    def test_NOK_delete_player(self, test_client):
        """try deleting player which doesn't exist"""
        new_player = populate_database.generate_player()
        new_player.username = "xyz"
        resp = test_client.delete("/api/player/", json=new_player.serialize())
        assert resp.status_code == 404

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
