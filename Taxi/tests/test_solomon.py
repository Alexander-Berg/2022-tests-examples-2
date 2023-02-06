import pytest

from core.solomon import SensorValue, sensor_value_to_dict


@pytest.mark.parametrize("test_input,expected", [
    (
        SensorValue('test', 11, 12),
        {'labels': {'sensor': 'test'}, 'ts': 11, 'value': 12}
    )
])
def test_sensor_value_to_dict(test_input, expected):
    assert expected == sensor_value_to_dict(test_input)
