"""
Configuration module for the main Flask application.
"""


class Config:

    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_BINDS = {"secrets": "sqlite:///secret.db"}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
