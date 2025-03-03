from datetime import datetime
from ranking_api.models import Player, Match, MatchPlayerRelation
import populate_database


class TestPlayerModel(object):

    RESOURCE_URL = "/api/players/"

    def test_create_player(self, test_client):
        """Test creating a new player."""
        new_player = populate_database.generate_player()
        player_name = new_player.username
        response = test_client.post(self.RESOURCE_URL, json=new_player)
        assert response.status_code == 201
        assert response.json["username"] == player_name

    def test_get_players(self, test_client):
        """Test retrieving all players."""
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        assert isinstance(response.json, list)

class TestMatchModel(object):

    RESOURCE_URL = "/api/matches/"

    def test_create_match(self, test_client):
        """Test creating a new match."""
        match = populate_database.generate_match()
        match_location = match.location
        response = test_client.post(self.RESOURCE_URL, json=match)
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
        # Create player
        new_player = populate_database.generate_player()
        player_name = new_player.username
        player_response = test_client.post(self.RESOURCE_URL, json=new_player)
        assert player_response.status_code == 201
        assert player_response.json["username"] == player_name

        # Create match
        match = populate_database.generate_match()
        match_location = match.location
        response = test_client.post(self.MATCH_URL, json=match)
        assert response.status_code == 201
        assert response.json["location"] == match_location

        # Join match
        match_id = match.id
        join_resp = test_client.post(f"/matches/{match_id}/join", json={"player_username": player_name})
        assert join_resp.status_code == 200
        assert join_resp.json["message"] == "Player added to match"
