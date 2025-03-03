import datetime
import pytest
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from ranking_api.models import Player, Match


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.mark.parametrize(
    'inputs, expected, exception',
    [
        #(username, num_of_matches, rating), (exp_username, exp_num_of_matches, exp_rating), Expected exception,
        (("uname", None, None), ("uname", 0, 1000), None), # test default value setting works
        (("uname", 73, 1337), ("uname", 73, 1337), None), # test custom value setting works
        ((None, None, None), None, ValueError), # test correct error is raised if no username is supplied
        (("a"*35, None, None), None, ValueError), # test correct error is raised if username is too long
        (("uname", -1, None), None, ValueError), # test correct error is raised if num of matches is negative
        (("uname", None, -1), None, ValueError), # test correct error is raised if rating is negative
        ((555, None, None), None, ValueError), # test correct error is raised if username is not str
    ],
)
def test_create_player(db_session, inputs, expected, exception):
    username, num_of_matches, rating = inputs
    if exception:
        with pytest.raises(exception):
            player = Player(
                username=username,
            )
            if num_of_matches:
                player.num_of_matches = num_of_matches
            if rating:
                player.rating = rating
            db_session.add(player)
            db_session.commit()
    else:
        player = Player(
                username=username,
            )
        if num_of_matches:
            player.num_of_matches = num_of_matches
        if rating:
            player.rating = rating
        db_session.add(player)
        db_session.commit()

        assert Player.query.count() == 1

        exp_username, exp_num_of_matches, exp_rating = expected
        db_player = Player.query.first()
        assert db_player.username == exp_username
        assert db_player.rating == exp_rating
        assert db_player.num_of_matches == exp_num_of_matches

@pytest.mark.parametrize(
    'inputs, exception',
    [
        #[(username, num_of_matches, rating)], Expected exception,
        (
            [("uname", None, None), ("uname", None, None)],
            IntegrityError
        ), # try to create players with same names
        (
            [("uname1", None, None), ("uname2", None, None), ("uname3", None, None)],
            None
        ) # create multiple valid players
    ],
)
def test_create_players(db_session, inputs, exception):
    for username, num_of_matches, rating in inputs:
        player = Player(
            username=username
        )
        if num_of_matches:
            player.num_of_matches = num_of_matches
        if rating:
            player.rating = rating
        db_session.add(player)
        
    if exception:
        with pytest.raises(exception):
            db_session.commit()
    else:
        db_session.commit()
        assert Player.query.count() == len(inputs)

def test_get_player_json_schema():
    schema = Player.json_schema()
    expected = {
        'type': 'object',
        'required': ['username'],
        'properties': {
            'username': {
                'description': "The users' name",
                'type': 'string',
                'minLength': 1,
                'maxLength': 32
                },
            'num_of_matches': {
                'description': 'Number of played matches',
                'type': 'integer',
                'minimum': 0
                },
            'rating': {
                'description': 'Current rating of the player',
                'type': 'integer',
                'minimum': 0
                }
            }
        }
    assert schema == expected

@pytest.mark.parametrize(
    "inputs, expected, exception",
    [
        # (location, time, description, status, rating_shift, team1_score, team2_score)
        (("Turku", datetime.datetime.now(), None, None, None, None, None), ("Turku", datetime.datetime.now(), None, None, None, None, None), None),
    ]
)
def test_create_match(db_session, inputs, expected, exception):
    location, time, description, status, rating_shift, team1_score, team2_score = inputs
    new_match = Match(
        location=location,
        time=time
    )
    db_session.add(new_match)
    db_session.commit()
    assert Match.query.count() == 1
    assert Match.query.first().location == location
    assert Match.query.first().time == time
