import enum

import pytest

from utils import validation


class TrafficLights(enum.Enum):
    RED_LIGHT = 'red'
    GREEN_LIGHT = 'green'
    YELLOW_LIGHT = 'yellow'


class TestConvertToEnumMembers:

    def test_happy_path(self):
        lights = ['red', 'green']

        result = validation.convert_to_enum_members(
            TrafficLights,
            lights
        )

        assert len(result) == 2
        assert result[0] == TrafficLights.RED_LIGHT
        assert result[1] == TrafficLights.GREEN_LIGHT

    def test_error_input(self):
        with pytest.raises(validation.EnumValidationError):
            validation.convert_to_enum_members(
                TrafficLights,
                ['red', 'blue']
            )


class TestPreprocessGetFilters:

    def test_none_filter(self):
        result = validation.preprocess_get_filters(None, TrafficLights)
        assert result is None

    def test_empty_filter(self):
        result = validation.preprocess_get_filters('', TrafficLights)
        assert result == []

    def test_single_value(self):
        result = validation.preprocess_get_filters('red', TrafficLights)
        assert result == [TrafficLights.RED_LIGHT]

    def test_multiple_values(self):
        result = validation.preprocess_get_filters('red,green', TrafficLights)
        assert result == [TrafficLights.RED_LIGHT, TrafficLights.GREEN_LIGHT]
