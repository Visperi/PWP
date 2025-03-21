"""
Utility module for API resource HTTP methods.
"""

from datetime import datetime

from werkzeug.exceptions import BadRequest
from jsonschema import ValidationError


def str_to_bool(value: str) -> bool:
    """
    Convert a query parameter to boolean variable and raise an exception if it is not boolean type.

    :param value: The query parameter value
    :return: True if the parameter lowered is 'true' or False if it is 'false'
    :raises BadRequest if parameter value is invalid, i.e. not strictly boolean in string format.
    """
    lower = value.lower()

    if lower == "true":
        return True
    if lower == "false":
        return False
    raise BadRequest(description="Bad query parameter")


def ts_to_datetime(timestamp: str) -> datetime:
    """
    Convert an ISO8601 timestamp to datetime object or raise an exception,
    if it is not in correct format.

    :param timestamp: The timestamp string to convert.
    :return: The timestamp converted to datetime object.
    :raises BadRequest: If the timestamp is not in ISO8601 format.
    """
    try:
        return datetime.fromisoformat(timestamp)
    except ValueError as exc:
        raise BadRequest("Bad datetime format") from exc


def fetch_validation_error(error: ValidationError):
    """
    Fetch a short and useful validation error message from a ValidationError.
    There is no need to send the full message with all field rules to the client.

    :param error: The triggered ValidationError.
    :return: An error message in format 'field_name: error_cause'
    """
    if error.validator == "required":
        variable_name = error.validator_value[0]
    else:
        variable_name = error.relative_path[0]
    return f"Error on value {variable_name}: {error.message}"
