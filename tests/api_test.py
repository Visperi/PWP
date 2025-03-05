from datetime import datetime, timezone
from ranking_api.models import Player, Match, MatchPlayerRelation
import populate_database
import json
from sqlalchemy.orm import class_mapper

def create_player(name, num_of_matches, rating):
    player = {
        "username": name,
        "num_of_matches": num_of_matches,
        "rating": rating
    }
    return player
    
def create_match(loc, time, desc, status=0, shift=0, team1=0, team2=0):
    match = {
            "location": loc,
            "time": time,
            "description": desc,
            "status": status,
            "rating_shift": shift,
            "team1_score": team1,
            "team2_score": team2
        }
    return match

class TestPlayerModel(object):

    RESOURCE_URL = "/api/players/"

    def test_create_player(self, test_client):
        """Test creating a new player."""
        new_player = create_player("alpha", 0, 1000)
        response = test_client.post(self.RESOURCE_URL, json=new_player)
        assert response.status_code == 201
        resp_pname = response.headers["Location"].split("/")[-2]
        assert resp_pname == "alpha"

    def test_get_players(self, test_client):
        """Test retrieving all players."""
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        assert isinstance(response.json, list)

    def test_NOK_create_player_with_existing_name(self, test_client):
        """Test to add existing player"""
        response = test_client.get(self.RESOURCE_URL)
        players = response.get_json()
        player1 = players[0]
        resp = test_client.post(self.RESOURCE_URL, json=player1)
        assert resp.status_code == 409

    def test_NOK_create_player_with_bad_num_of_matches(self, test_client):
        """Test to add player with falsy input on num_of_matches"""
        new_player = create_player("beta", "two", 0)
        response = test_client.post(self.RESOURCE_URL, json=new_player)
        assert response.status_code == 400

    def test_NOK_create_player_with_too_long_name(self, test_client):
        """Test to add player with too long name"""
        new_player = create_player("thisnamehastoomuchlettersthisnamehastoomuchletters", 0, 0)
        response = test_client.post(self.RESOURCE_URL, json=new_player)
        assert response.status_code == 400

    def test_delete_player(self, test_client):
        """delete player"""
        resp = test_client.delete(self.RESOURCE_URL + "alpha/")
        assert resp.status_code == 204

    def test_NOK_delete_player(self, test_client):
        """try deleting player which doesn't exist"""
        new_player_name = "thisdoesntexist"
        resp = test_client.delete(self.RESOURCE_URL + new_player_name + "/")
        assert resp.status_code == 404

class TestMatchModel(object):

    RESOURCE_URL = "/api/matches/"

    def test_create_match(self, test_client):
        """Test creating a new match."""
        match = create_match("kenttä", datetime.now(timezone.utc), "first_match")
        response = test_client.post(self.RESOURCE_URL, json=match)
        print(response.json)
        assert response.status_code == 201
        assert response.json["location"] == "kenttä"

    #TODO more passing match scenarios

    def test_get_matches(self, test_client):
        """Test retrieving all matches."""
        response = test_client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        assert isinstance(response.json, list)

    def test_NOK_create_match_invalid_location(self, test_client):
        """NOK test to validate match location"""
        #too short
        match = create_match("", datetime.now(timezone.utc), "first_match")
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400
        
        #not a string
        match = create_match(1, datetime.now(timezone.utc), "first_match")
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400
        
        #too long
        match = create_match("thisistoolongthisistoolongthisistoolongthisistoolongthisistoolong", datetime.now(timezone.utc), "first_match")
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400

    def test_NOK_create_match_invalid_time(self, test_client):
        """NOK test to validate match time"""
        match = create_match("kenttä", "today", "first_match")
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400

        match = create_match("kenttä", 1.1990, "first_match")
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400

    def test_NOK_create_match_invalid_description(self, test_client):
        """NOK test to validate match description"""
        #not a string
        match = create_match("kenttä", datetime.now(timezone.utc), 1)
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400
        
        #too long
        match = create_match("kenttä", datetime.now(timezone.utc), "thisdescriptioniswaytoolongthisdescriptioniswaytoolongthisdescriptioniswaytoolongthisdescriptioniswaytoolong")
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400

    def test_NOK_create_match_invalid_status(self, test_client):
        """NOK test to validate match status"""
        #not an integer
        match = create_match("kenttä", datetime.now(timezone.utc), "first", "not_an_integer")
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400
        
        match = create_match("kenttä", datetime.now(timezone.utc), "first", 0.5)
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400
        
        #not 0, 1 or 2
        match = create_match("kenttä", datetime.now(timezone.utc), "first", 3)
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400

    def test_NOK_create_match_invalid_shift(self, test_client):
        """NOK test to validate match shift"""

        match = create_match("kenttä", datetime.now(timezone.utc), "first", 0, 0.5)
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400

        match = create_match("kenttä", datetime.now(timezone.utc), "first", 0, "not_an_integer")
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400

    def test_NOK_create_match_invalid_team_status(self, test_client):
        """NOK test to validate match team status"""
        
        match = create_match("kenttä", datetime.now(timezone.utc), "first", 0, 0, 0.5)
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400

        match = create_match("kenttä", datetime.now(timezone.utc), "first", 0, 0, "not_an_integer")
        response = test_client.post(self.RESOURCE_URL, json=match)
        assert response.status_code == 400
    

class TestMatchPlayerRelation(object):

    PLAYER_URL = "/api/players/"
    MATCH_URL = "/api/matches/"

    def test_join_match(self, test_client):
        """Test associating a player with a match."""
        # Get first player
        new_player = create_player("beta", 0, 0)
        player_response = test_client.post(self.PLAYER_URL, json=new_player)
        assert player_response.status_code == 201

        # Create match
        match = create_match("university", datetime.now(timezone.utc), "second_match" )
        response = test_client.post(self.MATCH_URL, json=match)
        assert response.status_code == 201
        assert response.json["location"] == "university"

        # Join match
        match_id = test_client.get(self.MATCH_URL)
        print(match_id)
        join_resp = test_client.post(f"/matches/{match_id}/join", json=new_player.serialize())
        assert join_resp.status_code == 200
        assert join_resp.json["message"] == "Player added to match"
