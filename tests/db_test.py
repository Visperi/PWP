"""
Module for testing database models
"""
import datetime
import uuid
from contextlib import nullcontext as does_not_raise

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from ranking_api.models import Player, Match, MatchPlayerRelation
from ranking_api.secret_models import ApiToken

EXAMPLE_DATETIME = datetime.datetime(2001, 9, 11, 15, 46, 0)

def get_time(timedelta_hours = 0):
    """
    Get a datetime object with current time and timedelta in hours applied to it.

    :param timedelta_hours: Timedelta in hours to current time.
                            Defaults to 0 and gives the current time.
    :return: Datetime object with timedelta applied.
    """
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=timedelta_hours)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record): # pylint: disable=W0613
    """
    Ensure foreign keys are supported
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.mark.parametrize(
    'inputs, expected, expectation',
    [
        # (username, num_of_matches, rating),
        # (exp_username, exp_num_of_matches, exp_rating),
        # Expected exception,
        (("uname", None, None),
         ("uname", 0, 1000),
         does_not_raise()), # test default value setting works
        (("uname", 73, 1337),
         ("uname", 73, 1337),
         does_not_raise()), # test custom value setting works
        ((None, None, None),
         None,
         pytest.raises(ValueError)), # test correct error is raised if no username is supplied
        (("", 73, 1337),
         None,
         pytest.raises(ValueError)), # test correct error is raised if username is too short
        (("a"*35, None, None),
         None,
         pytest.raises(ValueError)), # test correct error is raised if username is too long
        (("uname", -1, None),
         None,
         pytest.raises(ValueError)), # test correct error is raised if num of matches is negative
        (("uname", None, -1),
         None,
         pytest.raises(ValueError)), # test correct error is raised if rating is negative
        (("uname", None, "ggg"),
         None,
         pytest.raises(ValueError)), # test correct error is raised if rating is not int
        (("uname", "ggg", None),
         None,
         pytest.raises(ValueError)), # test correct error is raised if rating is not int
        ((555, None, None),
         None,
         pytest.raises(ValueError)), # test correct error is raised if username is not str
    ],
)
def test_create_player(db_session, inputs, expected, expectation):
    """
    Test create single player works
    """
    username, num_of_matches, rating = inputs
    with expectation:
        player = Player(username=username)
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
    'inputs, expectation',
    [
        #[(username, num_of_matches, rating)], Expected exception,
        (
            [("uname", None, None), ("uname", None, None)],
            pytest.raises(IntegrityError)
        ), # try to create players with same names
        (
            [("uname1", None, None), ("uname2", None, None), ("uname3", None, None)],
            does_not_raise()
        ) # create multiple valid players
    ],
)
def test_create_players(db_session, inputs, expectation):
    """
    Test create multiple players works
    """
    for username, num_of_matches, rating in inputs:
        player = Player(
            username=username
        )
        if num_of_matches:
            player.num_of_matches = num_of_matches
        if rating:
            player.rating = rating
        db_session.add(player)

    with expectation:
        db_session.commit()
        assert Player.query.count() == len(inputs)

@pytest.mark.parametrize(
    "inputs, expected",
    [
        (("uname2", None, None), ("uname2", 0, 1000)),
        (("uname2", 73, 1337), ("uname2", 73, 1337)),
    ]
)
def test_player_deserialize(inputs, expected):
    """
    Test player.deserialize works
    """
    player = Player(
        username="uname"
    )
    username, num_of_matches, rating = inputs
    data = {
        "username": username
    }
    if num_of_matches:
        data["num_of_matches"] = num_of_matches
    if rating:
        data["rating"] = rating
    player.deserialize(data)
    exp_username, exp_num_of_matches, exp_rating = expected
    assert player.username == exp_username
    assert player.num_of_matches == exp_num_of_matches
    assert player.rating == exp_rating

def test_get_player_json_schema():
    """
    Test Player.json_schema() returns correct schema
    """
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
    "inputs, expected, expectation",
    [
        # (location, time, description, status, season_id, rating_shift, team1_score, team2_score)
        (
            ("place", EXAMPLE_DATETIME, None, None, 1, None, None, None),
            ("place", EXAMPLE_DATETIME, None, 0, 1, None, 0, 0),
            does_not_raise()
        ), # test match with default values
        (
            ("place", EXAMPLE_DATETIME, "good game", 0, 1, 0, 0, 0),
            ("place", EXAMPLE_DATETIME, "good game", 0, 1, 0, 0, 0),
            does_not_raise()
        ), # test match with custom values
        (
            ("", EXAMPLE_DATETIME, "good game", 0, 1, 0, 0, 0),
            None,
            pytest.raises(ValueError)
        ), # test 0 length location
        (
            (None, EXAMPLE_DATETIME, "good game", 0, 1, 0, 0, 0),
            None,
            pytest.raises(ValueError)
        ), # test no location supplied
        (
            (555, EXAMPLE_DATETIME, "good game", 0, 1, 0, 0, 0),
            None,
            pytest.raises(ValueError)
        ), # test location is not string
        (
            ("a"*51, EXAMPLE_DATETIME, "good game", 0, 1, 0, 0, 0),
            None,
            pytest.raises(ValueError)
        ), # test location is over 50 chars
        (
            ("place", None, "good game", 0, 1, 0, 0, 0),
            None,
            pytest.raises(ValueError)
        ), # test no time supplied
        (
            ("place", "yee", "good game", 0, 1, 0, 0, 0),
            None,
            pytest.raises(ValueError)
        ), # test time not datetime
        (
            ("place", EXAMPLE_DATETIME, 555, 0, 1, 0, 0, 0),
            None,
            pytest.raises(ValueError)
        ), # test description not string
        (
            ("place", EXAMPLE_DATETIME, "a"*101, 0, 1, 0, 0, 0),
            None,
            pytest.raises(ValueError)
        ), # test description over 100 chars
        (
            ("place", EXAMPLE_DATETIME, "good game", "ggg", 1, 0, 0, 0),
            None,
            pytest.raises(ValueError)
        ), # test game_status not integer
        (
            ("place", EXAMPLE_DATETIME, "good game", -1, 1, 0, 0, 0),
            None,
            pytest.raises(ValueError)
        ), # test game_status under 0
        (
            ("place", EXAMPLE_DATETIME, "good game", 3, 1, 0, 0, 0),
            None,
            pytest.raises(ValueError)
        ), # test game_status over 2
        (
            ("place", EXAMPLE_DATETIME, "good game", 0, 1, "ggg", 0, 0),
            None,
            pytest.raises(ValueError)
        ), # test rating_shift not int or null
        (
            ("place", EXAMPLE_DATETIME, "good game", 0, 1, 0, -1, 0),
            None,
            pytest.raises(ValueError)
        ), # test team1_score negative
        (
            ("place", EXAMPLE_DATETIME, "good game", 0, 1, 0, "ggg", 0),
            None,
            pytest.raises(ValueError)
        ), # test team1_score not int
        (
            ("place", EXAMPLE_DATETIME, "good game", 0, 1, 0, 0, -1),
            None,
            pytest.raises(ValueError)
        ), # test team2_score negative
        (
            ("place", EXAMPLE_DATETIME, "good game", 0, 1, 0, 0, "ggg"),
            None,
            pytest.raises(ValueError)
        ), # test team2_score not int
    ]
)
def test_create_match(db_session, inputs, expected, expectation): # pylint: disable=R0914
    """
    Test single match creation
    """
    location, time, description, status, season_id, rating_shift, team1_score, team2_score = inputs
    with expectation:
        new_match = Match(location=location, time=time)
        if rating_shift is not None:
            new_match.rating_shift = rating_shift
        if description:
            new_match.description = description
        if status:
            new_match.status = status
        if team1_score:
            new_match.team1_score = team1_score
        if team2_score:
            new_match.team2_score = team2_score
        if season_id:
            new_match.season_id = season_id

        db_session.add(new_match)
        db_session.commit()
        assert Match.query.count() == 1

        (
            exp_location,
            exp_time,
            exp_description,
            exp_status,
            exp_season_id,
            exp_rating_shift,
            exp_team1_score,
            exp_team2_score
        ) = expected

        db_match = Match.query.first()
        assert db_match.id == 1
        assert db_match.location == exp_location
        assert db_match.time == exp_time
        assert db_match.description == exp_description
        assert db_match.status == exp_status
        assert db_match.season_id == exp_season_id
        assert db_match.rating_shift == exp_rating_shift
        assert db_match.team1_score == exp_team1_score
        assert db_match.team2_score == exp_team2_score

@pytest.mark.parametrize(
    "inputs",
    [
        (
            [
                ("place", EXAMPLE_DATETIME, "good game", 0, 1, 0, 0, 0),
                ("place", EXAMPLE_DATETIME, "good game", 0, 1, 0, 0, 0),
            ]
        ), # test create 2 games
    ]
)
def test_create_multiple_matches(db_session, inputs):
    """
    Test multiple matches creation works properly
    """
    for location, time, description, status, season_id, rating_shift, team1_score, team2_score in inputs:
        new_match = Match(
                location=location,
                time=time
            )
        new_match.rating_shift = rating_shift if rating_shift is not None else None
        if description:
            new_match.description = description
        if status:
            new_match.status = status
        if team1_score:
            new_match.team1_score = team1_score
        if team2_score:
            new_match.team2_score = team2_score
        if season_id:
            new_match.season_id = season_id
        db_session.add(new_match)
    db_session.commit()

    assert Match.query.count() == len(inputs)
    matches = Match.query.all()
    assert matches[0].id == 1
    assert matches[1].id == 2

def test_get_match_json_schema():
    """
    Test match.json_schema returns correct schema
    """
    schema = Match.json_schema()
    schema_properties = schema["properties"]
    expected_properties = ("location",
                           "time",
                           "description",
                           "status",
                           "season_id",
                           "rating_shift",
                           "team1_score",
                           "team2_score")

    for prop in expected_properties:
        assert prop in schema_properties

    assert schema["required"] == ["location", "time"]

    assert schema_properties["location"]["type"] == "string"
    assert schema_properties["location"]["minLength"] == 1
    assert schema_properties["location"]["maxLength"] == 50

    assert schema_properties["time"]["type"] == "string"
    assert schema_properties["time"]["format"] == "date-time"

    assert schema_properties["description"]["anyOf"] == [{"type": "string", "maxLength": 100},
                                                         {"type": "null"}]
    
    assert schema_properties["season_id"]["type"] == "integer"

    assert schema_properties["rating_shift"]["anyOf"] == [{"type": "null"}, {"type": "integer"}]

    for key in ("team1_score", "team2_score", "status"):
        prop = schema_properties[key]
        assert prop["type"] == "integer"
        assert prop["minimum"] == 0
        if key == "status":
            assert prop["maximum"] == 2

@pytest.mark.parametrize(
    "inputs, expected",
    [
        (("place", EXAMPLE_DATETIME, None, 0, 1, None, 0, 0),
         ("place", EXAMPLE_DATETIME, None, 0, 1, None, 0, 0)),
        (("place", EXAMPLE_DATETIME, "good game", 0, 1, 0, 0, 0),
         ("place", EXAMPLE_DATETIME, "good game", 0, 1, 0, 0, 0)),
    ]
)
def test_match_deserialize(inputs, expected): # pylint: disable=R0914
    """
    Test match deserialization
    """
    new_match = Match(
        location="weird place",
        time=datetime.datetime.now()
    )
    location, time, description, status, season_id, rating_shift, team1_score, team2_score = inputs
    data = {
        "location": location,
        "time": str(time),
        "status": status,
        "team1_score": team1_score,
        "team2_score": team2_score,
        "season_id": season_id
    }

    if description:
        data["description"] = description
    data["rating_shift"] = rating_shift if rating_shift is not None else None
    new_match.deserialize(data)
    (
        exp_location,
        exp_time,
        exp_description,
        exp_status,
        exp_season_id,
        exp_rating_shift,
        exp_team1_score,
        exp_team2_score
      ) = expected
    assert new_match.location == exp_location
    assert new_match.time == exp_time
    assert new_match.description == exp_description
    assert new_match.status == exp_status
    assert new_match.season_id == exp_season_id
    assert new_match.rating_shift == exp_rating_shift
    assert new_match.team1_score == exp_team1_score
    assert new_match.team2_score == exp_team2_score

def test_match_player_relation(db_session):
    """
    Test MatchPlayerRelation behavior in the database
    """
    new_match = Match(
        location="place",
        time=EXAMPLE_DATETIME,
        season_id=1
    )
    db_session.add(new_match)
    db_session.commit()

    match_id = Match.query.first().id

    player = Player(
        username="uname"
    )
    mp_relation = MatchPlayerRelation(
        username=player.username,
        match_id=match_id,
        team=1
    )

    db_session.add(player)
    db_session.add(mp_relation)
    db_session.commit()

    assert MatchPlayerRelation.query.count() == 1
    mp_relation = MatchPlayerRelation.query.first()
    assert mp_relation.username == player.username
    assert mp_relation.match_id == match_id
    assert Player.query.first().matches[0] == mp_relation
    assert Match.query.first().players[0] == mp_relation

def test_match_player_relation_serialize_match(db_session):
    """
    Test MatchPlayerRelation.serialize_match method
    """
    new_match = Match(
        location="place",
        time=EXAMPLE_DATETIME,
        season_id=1
    )
    db_session.add(new_match)
    db_session.commit()

    match_id = Match.query.first().id

    player = Player(
        username="uname"
    )
    mp_relation = MatchPlayerRelation(
        username=player.username,
        match_id=match_id,
        team=1
    )

    db_session.add(player)
    db_session.add(mp_relation)
    db_session.commit()

    match_data = mp_relation.serialize_match()
    assert match_data["location"] == "place"

def test_match_player_relation_serialize_player(db_session):
    """
    Test MatchPlayerRelation.serialize_player method
    """
    new_match = Match(
        location="place",
        time=EXAMPLE_DATETIME,
        season_id=1
    )
    db_session.add(new_match)
    db_session.commit()

    match_id = Match.query.first().id

    player = Player(
        username="uname"
    )
    mp_relation = MatchPlayerRelation(
        username=player.username,
        match_id=match_id,
        team=1
    )

    db_session.add(player)
    db_session.add(mp_relation)
    db_session.commit()

    player_data = mp_relation.serialize_player()
    assert player_data["username"] == "uname"

def test_player_serialize_include_matches(db_session):
    """
    Test Player.serialize method with include matches as True
    """
    new_match = Match(
        location="place",
        time=EXAMPLE_DATETIME,
        season_id=1
    )
    db_session.add(new_match)
    db_session.commit()

    match_id = Match.query.first().id

    player = Player(
        username="uname"
    )
    mp_relation = MatchPlayerRelation(
        username=player.username,
        match_id=match_id,
        team=1
    )

    db_session.add(player)
    db_session.add(mp_relation)
    db_session.commit()

    player_data = player.serialize(include_matches=True)
    expected = [
        {'id': 1,
         'location': 'place',
         'time': '2001-09-11 15:46:00',
         'description': None,
         'status': 0,
         'season_id': 1,
         'rating_shift': None,
         'team1_score': 0,
         'team2_score': 0,
         'team': 1
         }
        ]
    assert player_data["username"] == "uname"
    assert player_data["matches"] == expected

def test_match_serialize_include_players(db_session):
    """
    Test Match.serialize method with include players as True
    """
    new_match = Match(
        location="place",
        time=EXAMPLE_DATETIME,
        season_id=1
    )
    db_session.add(new_match)
    db_session.commit()

    match_id = Match.query.first().id

    player = Player(
        username="uname"
    )
    mp_relation = MatchPlayerRelation(
        username=player.username,
        match_id=match_id,
        team=1
    )

    db_session.add(player)
    db_session.add(mp_relation)
    db_session.commit()

    match_data = new_match.serialize(include_players=True)
    expected = [
        {'username': 'uname', 'num_of_matches': 0, 'rating': 1000, 'team': 1}
        ]
    assert match_data["location"] == "place"
    assert match_data["players"] == expected


@pytest.mark.parametrize("token, user, expires_in, created_at, expectation", (
        ("token", "testing", get_time(), get_time(), does_not_raise()),
        ("token", "testing", None, get_time(), does_not_raise()),
        (uuid.uuid4(), "testing", None, get_time(), pytest.raises(ValueError)),
        (None, "testing", None, get_time(), pytest.raises(ValueError)),
        (" ", "testing", None, get_time(), pytest.raises(ValueError)),
        ("token", None, None, get_time(), pytest.raises(ValueError)),
        ("token", "testing", "gsdjf", get_time(), pytest.raises(ValueError)),
        ("token", "testing", get_time(), None, pytest.raises(ValueError))
))
def test_create_api_token(db_session, token, user, expires_in, created_at, expectation):  # pylint: disable=R0913,R0917
    """
    Test creating an ApiToken works and raises ValueError with invalid values.
    """
    with expectation:
        token = ApiToken(token=token,
                         user=user,
                         expires_in=expires_in,
                         created_at=created_at)
        db_session.add(token)
        db_session.commit()

def test_api_token_duplicate_user_raises(db_session):
    """
    Test that creating ApiToken with non-unique user raises an error.
    """
    token = ApiToken(token="token",
                     user="testing",
                     expires_in=get_time(),
                     created_at=get_time())
    token2 = ApiToken(token="token2",
                      user=token.user,
                      expires_in=get_time(),
                      created_at=get_time())

    db_session.add(token)
    db_session.add(token2)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_api_token_is_expired(db_session):
    """
    Test that ApiToken.is_expired works as a hybrid property.
    """
    infinitely_valid_token = ApiToken(token=str(uuid.uuid4()),
                                      user="user1",
                                      expires_in=None,
                                      created_at=get_time())
    valid_token = ApiToken(token=str(uuid.uuid4()),
                           user="user2",
                           expires_in=get_time(1),
                           created_at=get_time())
    expired_token = ApiToken(token=str(uuid.uuid4()),
                             user="user3",
                             expires_in=get_time(-1),
                             created_at=get_time())

    db_session.add(infinitely_valid_token)
    db_session.add(valid_token)
    db_session.add(expired_token)
    db_session.commit()

    infinitely_valid_token = ApiToken.query.filter_by(token=infinitely_valid_token.token).first()
    valid_token = ApiToken.query.filter_by(token=valid_token.token).first()
    expired_token = ApiToken.query.filter_by(token=expired_token.token).first()

    assert ApiToken.query.count() == 3
    assert infinitely_valid_token.is_expired is False
    assert valid_token.is_expired is False
    assert expired_token.is_expired is True
