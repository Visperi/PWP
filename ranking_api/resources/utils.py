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
    :raises BadRequest: if parameter value is invalid, i.e. not strictly boolean in string format.
    :raises AttributeError: If the input is not string type.
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


def fetch_validation_error_message(error: ValidationError):
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


def validate_put_request_properties(schema: dict, data: dict):
    """
    Validate received object properties for PUT requests. Raise an exception if validation fails.
    This function temporarily makes all schema properties required, so use only when
    that is needed.

    :param schema: The object schema to validate against.
    :param data: The received request data.
    :return: None if the data is valid, else raise a BadRequest error.
    :raises: BadRequest HTTP400 error if object field validation fails.
    """
    # Update the schema to require all properties
    schema["required"] = list(schema["properties"].keys())

    try:
        validate(data, schema)
    except ValidationError as e:
        if list(data.keys()) != schema["required"]:
            msg = "All object fields are required in PUT requests."
        else:
            msg = fetch_validation_error_message(e)
        raise BadRequest(description=msg) from e
