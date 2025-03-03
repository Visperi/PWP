"""
Module for creating all the fixtures used in the tests

All of the fixtures created here can be used inside all test files (check db_test.py for example)
"""
import pytest
from ranking_api.app import create_app
from ranking_api.extensions import db

@pytest.fixture(scope="session") # create app only once per testing session to avoid error
def test_app():
    app = create_app(testing=True)
    return app

@pytest.fixture(scope="function") # new session created for each test
def db_session(test_app):
    with test_app.app_context():
        db.create_all()
        yield db.session
        db.session.rollback()
        db.drop_all()
        db.session.remove()

@pytest.fixture(scope="function") # new client created for each test
def test_client(test_app):
    """Setup a Flask test client."""
    return test_app.test_client()
