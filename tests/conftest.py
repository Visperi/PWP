"""
Module for creating all the fixtures used in the tests

All of the fixtures created here can be used inside all test files (check db_test.py for example)
"""
import pytest
import populate_database
from ranking_api.app import create_app
from ranking_api.extensions import db

@pytest.fixture(scope="session")
def test_app():
    """
    Create test app a single time for a single testing session and cleanup db after
    """
    app = create_app("config.TestConfig")
    return app


@pytest.fixture(scope="function") # clean db state after each test
def db_session(test_app): # pylint: disable=W0621
    """
    Create testing db session
    """
    with test_app.app_context():
        db.create_all()
        new_season = populate_database.generate_season() # insert a single season into database to make season dependent tests work
        db.session.add(new_season)
        yield db.session
        db.session.rollback()
        db.drop_all()

@pytest.fixture(scope="function") # new client created for each test
def test_client(test_app, db_session): # pylint: disable=W0621,W0613
    """
    Setup a Flask test client.
    """
    return test_app.test_client()

@pytest.fixture(scope="function")
def auth_header(test_app):  # pylint: disable=W0621
    """
    Get Authorization header with a Bearer token for requests requiring authentication.
    """
    with test_app.app_context():
        api_token = test_app.config["KEYRING"].create_token("tests")
        return {"Authorization": f"Bearer {api_token}"}
