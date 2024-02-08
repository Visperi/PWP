"""
Flask extensions utilized by the main Flask object to prevent circular imports and have one common
place for all needed modules. Objects instantiated here must call init_app method before using
them.
"""
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
