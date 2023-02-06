import pytest

CONFIG_DEFAULT_ENABLED_VALUE = {
    '__default__': {
        '__default__': {'enabled': True, 'fallback_to_mongo_enabled': False},
    },
}

PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS = pytest.mark.parametrize(
    'individual_tariffs_switch_on',
    [
        pytest.param(False, id='use_direct_mongo_tariffs'),
        pytest.param(
            True,
            id='use_individual_tariffs',
            marks=[
                pytest.mark.config(
                    INDIVIDUAL_TARIFFS_USING=CONFIG_DEFAULT_ENABLED_VALUE,
                ),
            ],
        ),
    ],
)
