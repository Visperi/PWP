"""
Configuration module for the main Flask application.
"""


class Config:

    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig:
    
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:" # use sqlite in-memory database for testing
    TESTING = True
