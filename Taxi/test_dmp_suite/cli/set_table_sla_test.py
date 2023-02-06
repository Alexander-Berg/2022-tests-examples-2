import pytest

from dmp_suite.datetime_utils import parse_timedelta_string


@pytest.mark.parametrize(
    'sla_input, expected_result',
    [(25200, 25200), ("25200", 25200), ("7h", 25200), ('7H', 25200), ('6h59m60s', 25200), ('6h59m60', 25200), (0, 0),
     ("0", 0), ("0d", 0)]
)
def test_parse_sla_string(sla_input, expected_result):
    assert parse_timedelta_string(sla_input) == expected_result


@pytest.mark.parametrize(
    'sla_input',
    [25200.0, object(), '2h3s4h'],
)
def test_parse_sla_string_raises(sla_input):
    with pytest.raises(ValueError):
        parse_timedelta_string(sla_input)
