import pytest

from mayak_inspector.common.models import metrics_event


@pytest.mark.config(
    MAYAK_INSPECTOR_TARIFF_GROUP_SETTINGS={
        'tariff_mapping': {
            '__default__': 'econom',
            'uberx': 'econom',
            'econom': 'econom',
            'comfortplus': 'comfortplus',
        },
        'tariff_groups_order': ['econom', 'comfortplus'],
    },
)
@pytest.mark.parametrize(
    'tariffs, expected',
    [
        pytest.param(
            ['uberx', 'econom', 'comfortplus'], 'comfortplus', id='default',
        ),
        pytest.param(['new'], 'econom', id='missing_config'),
        pytest.param(['uberx', 'econom'], 'econom', id='not_max'),
    ],
)
def test_tariff_mapping(tariffs, expected, stq3_context):
    config = stq3_context.config.MAYAK_INSPECTOR_TARIFF_GROUP_SETTINGS
    result = metrics_event.get_tariff_group(tariffs, config)
    assert result == expected
