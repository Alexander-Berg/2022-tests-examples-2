import pytest

from taxi_config_schemas import config_models
from test_taxi_config_schemas.configs import common

SCHEMA = {
    'additionalProperties': {'$ref': '#/definitions/zone_pin_settings'},
    'properties': {'__default__': {'$ref': '#/definitions/zone_pin_settings'}},
    'required': ['__default__'],
    'type': 'object',
    'definitions': {
        'gain_ratio_range': {'maximum': 1, 'minimum': 0, 'type': 'number'},
        'zone_pin_settings': {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'price_gain_absolute': {'minimum': 0, 'type': 'integer'},
                'price_gain_absolute_minorder': {
                    'minimum': 0,
                    'type': 'number',
                },
                'price_gain_ratio': {'$ref': '#/definitions/gain_ratio_range'},
                'route_gain_ratio': {'$ref': '#/definitions/gain_ratio_range'},
                'time_gain_ratio': {'$ref': '#/definitions/gain_ratio_range'},
            },
        },
    },
}

DEFAULT_VALUE = {
    '__default__': {
        'price_gain_absolute': 30,
        'price_gain_absolute_minorder': 1,
        'price_gain_ratio': 0.1,
        'route_gain_ratio': 0.1,
        'time_gain_ratio': 0.2,
    },
}


@pytest.mark.parametrize(
    'new_value,is_valid',
    [
        (
            {
                '__default__': {
                    'price_gain_absolute': 30,
                    'price_gain_absolute_minorder': 1,
                    'price_gain_ratio': 0.1,
                    'route_gain_ratio': 0.1,
                    'time_gain_ratio': 0.2,
                },
                'moscow': {
                    'price_gain_absolute': 50,
                    'price_gain_absolute_minorder': 5,
                    'price_gain_ratio': 0.1,
                    'route_gain_ratio': 0.1,
                    'time_gain_ratio': 0.2,
                },
            },
            True,
        ),
        (
            {
                '__default__': {
                    'price_gain_absolute': 30,
                    'price_gain_absolute_minorder': 1,
                    'price_gain_ratio': 0.1,
                    'route_gain_ratio': 0.1,
                    'time_gain_ratio': 0.2,
                },
                'moscow': {
                    'price_gain_absolute': True,
                    'price_gain_absolute_minorder': 5,
                    'price_gain_ratio': 0.1,
                    'route_gain_ratio': 0.1,
                    'time_gain_ratio': 0.2,
                },
            },
            False,
        ),
        (
            {
                '__default__': {
                    'price_gain_absolute': 30,
                    'price_gain_absolute_minorder': 1,
                    'price_gain_ratio': 0.1,
                    'route_gain_ratio': 0.1,
                    'time_gain_ratio': 0.2,
                },
                'moscow': {
                    'price_gain_absolute': 2,
                    'price_gain_absolute_minorder': 5,
                    'price_gain_ratio': 2,
                    'route_gain_ratio': 0.1,
                    'time_gain_ratio': 0.2,
                },
            },
            False,
        ),
    ],
)
async def test_validation(web_context, new_value, is_valid):
    config_with_value = common.get_config_with_value(DEFAULT_VALUE, SCHEMA)
    if is_valid:
        await config_with_value.validate(new_value, {}, web_context)
    else:
        with pytest.raises(config_models.ValidationError):
            await config_with_value.validate(new_value, {}, web_context)
