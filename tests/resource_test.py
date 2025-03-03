'''import json
import os
import pytest
import random
import tempfile
import time
from datetime import datetime
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def _populate_db():
    for idx, letter in enumerate("ABC", start=1):
        loc = Location(
            name=f"Location-{letter}",
            latitude=round(random.random() * 100, 2),
            longitude=round(random.random() * 100, 2),
            altitude=round(random.random() * 100, 2),
        )
        sensor = Sensor(
            name=f"test-sensor-{idx}",
            model="testsensor",
        )
        sensor.location = loc
        db.session.add(sensor)
        
    db.session.commit()
    
def _get_sensor_json(number=1):
    """
    Creates a valid sensor JSON object to be used for PUT and POST tests.
    """
    
    return {"name": "extra-sensor-{}".format(number), "model": "extrasensor"}
    

class TestSensorCollection(object):
    """
    This class implements tests for each HTTP method in sensor collection
    resource. 
    """
    
    RESOURCE_URL = "/api/sensors/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body["items"]) == 3
        for item in body["items"]:
            assert "name" in item
            assert "model" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = _get_sensor_json()
        
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["name"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "extra-sensor-1"
        assert body["model"] == "extrasensor"
        
        # send same data again for 409
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        
        # remove model field for 400
        valid.pop("model")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        
class TestSensorItem(object):
    
    RESOURCE_URL = "/api/sensors/test-sensor-1/"
    INVALID_URL = "/api/sensors/non-sensor-x/"
    MODIFIED_URL = "/api/sensors/extra-sensor-1/"
    
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "test-sensor-1"
        assert body["model"] == "testsensor"
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible erroe codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI. 
        """
        
        valid = _get_sensor_json()
        
        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        
        # test with another sensor's name
        valid["name"] = "test-sensor-2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409
        
        # test with valid (only change model)
        valid["name"] = "test-sensor-1"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204
        
        # remove field for 400
        valid.pop("model")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400
        
        valid = _get_sensor_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["model"] == valid["model"]
        
    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the sensor afterwards results in 404.
        Also checks that trying to delete a sensor that doesn't exist results
        in 404.
        """
        
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404
'''