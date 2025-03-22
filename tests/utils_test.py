"""
Module for testing utils
"""
import datetime
from contextlib import nullcontext as does_not_raise

import pytest
from werkzeug.exceptions import BadRequest

from ranking_api.resources import utils
from ranking_api.models import Player


@pytest.mark.parametrize(
        "inputs, expected, exception",
        [
            ("true", True, None),
            ("false", False, None),
            ("abc", None, BadRequest),
            (1, None, AttributeError)
        ]
)
def test_str_to_bool(inputs, expected, exception):
    """Test str_to_bool function from utils"""
    if exception:
        with pytest.raises(exception):
            utils.str_to_bool(inputs)
    else:
        assert utils.str_to_bool(inputs) == expected

@pytest.mark.parametrize(
        "inputs, expected, exception",
        [
            ("2001-09-11T08:46:00+00:00",
            datetime.datetime.fromisoformat("2001-09-11T08:46:00+00:00"),
            None
            ),
            ("200",
            None,
            BadRequest
            ),
        ]
)
def test_ts_to_datetime(inputs, expected, exception):
    """Test ts_to_datetime function from utils"""
    if exception:
        with pytest.raises(exception):
            utils.ts_to_datetime(inputs)
    else:
        assert utils.ts_to_datetime(inputs) == expected


@pytest.mark.parametrize("data, expectation", (
        ({"username": "testing", "num_of_matches": 0, "rating": 0}, does_not_raise()),
        ({"username": "testing", "num_of_matches": 0}, pytest.raises(BadRequest)),
        ({"username": "testing", "rating": 0}, pytest.raises(BadRequest)),
        ({"num_of_matches": 0, "rating": 0} ,pytest.raises(BadRequest)),
        ({"username": None, "num_of_matches": 0, "rating": 0}, pytest.raises(BadRequest))
))
def test_put_request_property_validation(data, expectation):
    """
    Test the PUT request property validation. Verify the function raises BadRequest error if any
     of the schema properties is missing or their data is invalid.
    """
    schema = Player.json_schema()
    with expectation:
        utils.validate_put_request_properties(schema, data)
