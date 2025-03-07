"""
Module for testing utils
"""
import datetime
import pytest
from werkzeug.exceptions import BadRequest
from ranking_api.resources import utils


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
