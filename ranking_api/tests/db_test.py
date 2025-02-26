import os
import pytest
import tempfile
import time
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from app import create_app
from models import Player, Match, MatchPlayerRelation

if __name__ == "__main__":
    app = create_app()

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True
    
    ctx = app.app.app_context()
    ctx.push()
    app.db.create_all()
        
    yield app.db
    
    app.db.session.rollback()
    app.db.drop_all()
    app.db.session.remove()
    ctx.pop()
    os.close(db_fd)
    os.unlink(db_fname)

def _get_player(playername="alpha"):
    return Player(
        username=playername,
        num_of_matches=5,
        rating=1100
    )

def _get_match(loc="nurtsi", desc="eka peli"):
    return Match(
        location=loc,
        time=datetime.datetime.now(),
        description=desc
    )
    
def test_create_instances(db_handle):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that 
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    # Create everything
    player = _get_player()
    match = _get_match()
    db_handle.session.add(player)
    db_handle.session.add(match)
    db_handle.session.commit()
    
    # Check that everything exists
    assert Player.query.count() == 1
    assert Match.query.count() == 1
    db_player = Player.query.first()
    db_match = Match.query.first()
    
    # Check all relationships (both sides)
    assert db_match.players == db_player
    assert db_player.matches == db_match
    assert db_player in db_match.players
    assert db_match in db_player.matches
    
def test_player_uniqueness(db_handle):
    """
    Tests that there can't be two players with same name
    """
    
    player = _get_player()
    playername = player.username
    db_handle.session.add(playername)   
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

"""
def test_measurement_ondelete_sensor(db_handle):
    
    #Tests that measurement's sensor foreign key is set to null when the sensor
    #is deleted.

    
    measurement = _get_measurement()
    sensor = _get_sensor()
    measurement.sensor = sensor
    db_handle.session.add(measurement)
    db_handle.session.commit()
    db_handle.session.delete(sensor)
    db_handle.session.commit()
    assert measurement.sensor is None
        
def test_location_columns(db_handle):

    #Tests the types and restrictions of location columns. Checks that numerical
    #values only accepts numbers, and that all of the columns are optional. 

    
    location = _get_location()
    location.latitude = str(location.latitude) + "°"
    db_handle.session.add(location)
    with pytest.raises(StatementError):
        db_handle.session.commit()
        
    db_handle.session.rollback()
        
    location = _get_location()
    location.longitude = str(location.longitude) + "°"
    db_handle.session.add(location)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
    db_handle.session.rollback()

    location = _get_location()
    location.altitude = str(location.altitude) + "m"
    db_handle.session.add(location)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    location = Location(name="beta")
    db_handle.session.add(location)
    db_handle.session.commit()    
    
def test_sensor_columns(db_handle):
 
    #Tests sensor columns' restrictions. Name must be unique, and name and model
    #must be mandatory.


    sensor_1 = _get_sensor()
    sensor_2 = _get_sensor()
    db_handle.session.add(sensor_1)
    db_handle.session.add(sensor_2)    
    with pytest.raises(IntegrityError):
        db_handle.session.commit()

    db_handle.session.rollback()
    
    sensor = _get_sensor()
    sensor.name = None
    db_handle.session.add(sensor)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    sensor = _get_sensor()
    sensor.model = None
    db_handle.session.add(sensor)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()    
    
def test_measurement_columns(db_handle):

    #Tests that a measurement value only accepts floating point values and that
    #time only accepts datetime values.

    
    measurement = _get_measurement()
    measurement.value = str(measurement.value) + "kg"
    db_handle.session.add(measurement)
    with pytest.raises(StatementError):
        db_handle.session.commit()
        
    db_handle.session.rollback()
    
    measurement = _get_measurement()
    measurement.time = time.time()
    db_handle.session.add(measurement)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
def test_deployment_columns(db_handle):

    #Tests that all columns in the deployment table are mandatory. Also tests
    #that start and end only accept datetime values.

    
    # Tests for nullable
    deployment = _get_deployment()
    deployment.start = None
    db_handle.session.add(deployment)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()

    deployment = _get_deployment()
    deployment.end = None
    db_handle.session.add(deployment)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()

    deployment = _get_deployment()
    deployment.name = None
    db_handle.session.add(deployment)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
        
    # Tests for column type
    deployment = _get_deployment()
    deployment.start = time.time()
    db_handle.session.add(deployment)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    deployment = _get_deployment()
    deployment.end = time.time()
    db_handle.session.add(deployment)
    with pytest.raises(StatementError):
        db_handle.session.commit()
"""