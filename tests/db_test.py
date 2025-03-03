import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event

from ranking_api.models import Player, Match


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def test_create_default_player(db_session):
    player = Player(
        username="Jonne"
    )

    db_session.add(player)
    db_session.commit()

    assert Player.query.count() == 1
    db_player = Player.query.first()
    assert db_player.username == "Jonne"
    assert db_player.rating == 1000
    assert db_player.num_of_matches == 0

def test_create_custom_player(db_session):
    player = Player(
        username="Jonne",
        rating=1337,
        num_of_matches=73
    )

    db_session.add(player)
    db_session.commit()

    assert Player.query.count() == 1
    db_player = Player.query.first()
    assert db_player.username == "Jonne"
    assert db_player.rating == 1337
    assert db_player.num_of_matches == 73
