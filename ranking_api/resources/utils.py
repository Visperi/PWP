"""
Utility module for processing HTTP methods for resources.
"""

from datetime import datetime

from werkzeug.exceptions import BadRequest


def str_to_bool(value: str) -> bool:
    """
    Convert a query parameter to boolean variable and raise an exception if it is not boolean type.

    :param value: The query parameter value
    :return: True if the parameter lowered is 'true' or False if it is 'false'
    :raises BadRequest: If the parameter value is invalid, i.e. is not strictly a boolean in string format.
    """
    lower = value.lower()

    if lower == "true":
        return True
    elif lower == "false":
        return False
    else:
        raise BadRequest(description="Bad query parameter")


def ts_to_datetime(timestamp: str) -> datetime:
    """
    Convert an ISO8601 timestamp to datetime object or raise an exception if it is not in correct format.
    The timestamp must not have any timezone information.

    :param timestamp: The timestamp
    :return: The timestamp converted to datetime object
    :raises BadRequest: If the timestamp is in incorrect format.
    """
    try:
        return datetime.fromisoformat(timestamp)
    except ValueError:
        raise BadRequest("Bad datetime format")
