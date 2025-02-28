"""
Definitions for models stored in separate secret database.
"""
from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

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

    def __str__(self):
        return self.token

    @hybrid_property
    def is_expired(self):
        """
        True if the token is expired, False otherwise. Always False for
        nullified expires_in values.
        """
        return self.expires_in is not None and datetime.now() > self.expires_in
