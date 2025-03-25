"""
Definitions for models stored in separate secret database.
"""
from datetime import datetime, timezone

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

from ranking_api.extensions import db


class ApiToken(db.Model):
    """
    A model for API tokens.
    """
    __tablename__ = "api_tokens"
    __bind_key__ = "secrets"

    token = db.Column(db.String(36), primary_key=True)
    user = db.Column(db.String(32), nullable=False, unique=True)
    expires_in = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def __str__(self):
        return self.token

    @validates("token", "user")
    def validate_string_fields(self, key, value):
        """
        Validate assigned string properties.

        :param key: Name of the property.
        :param value: Value assigned to the property.
        :return: Value of the property if valid.
        :raises ValueError: If the value is not a string or contains no textual data.
        """
        if not isinstance(value, str):
            raise ValueError(f"{key} must be a string.")
        if not value.strip():
            raise ValueError(f"{key} must have non-empty content.")
        return value

    @validates("expires_in", "created_at")
    def validate_datetime_fields(self, key, value):
        """
        Validate assigned datetime properties. Accepts null values for nullable properties.

        :param key: Name of the property.
        :param value: Value assigned to the property.
        :return: The value if valid.
        :raises ValueError: If the value is not datetime object.
        """
        if isinstance(value, datetime) or (key == "expires_in" and value is None):
            return value

        raise ValueError(f"{key} must be a datetime object.")

    @hybrid_property
    def is_expired(self):
        """
        True if the token is expired, False otherwise. Always False for
        nullified expires_in values.
        """
        if self.expires_in is None:
            return False

        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        return self.expires_in < current_time
