"""
Utility module for API resource HTTP methods.
"""

from datetime import datetime

from werkzeug.exceptions import BadRequest
from jsonschema import validate, ValidationError


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


def validate_put_request_properties(schema: dict, data: dict):
    """
    Validate received object properties for PUT requests. Raise an exception if validation fails.

    :param schema: The object schema to validate against.
    :param data: The received request data.
    :return: None if the data is valid, else raise a BadRequest error.
    """
    # Update the schema to require all properties
    schema["required"] = list(schema["properties"].keys())

    try:
        validate(data, schema)
    except ValidationError as e:
        if list(data.keys()) != schema["required"]:
            msg = "All object fields are required in PUT requests."
        else:
            msg = str(e)
        raise BadRequest(description=msg) from e
