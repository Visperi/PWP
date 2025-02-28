"""
Definitions for models stored in separate secret database.
"""
from ranking_api.extensions import db


class ApiToken(db.Model):
    """
    A model for API tokens.
    """
    __tablename__ = "api_tokens"
    __bind_key__ = "secrets"

    token = db.Column(db.String(36), primary_key=True)
    user = db.Column(db.String(32), nullable=False)
    expires_in = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)