import pytest

import operation_calculations.geosubventions.common as common


class TestConfig:
    ATLAS_GEOSUBVENTION_RESTRICTIONS = {
        '__default__': {'ok_key': 1},
        'moscow': {'ok_key': 2},
        'korolev': {'ok_key': 3},
    }
    ATLAS_GEOSUBVENTIONS_EXPERIMENTS = {
        '__default__': [{'shift_money': 1}],
        'moscow': [{'shift_money': 1}, {'shift_interval': 1}],
        'korolev': [{'shift_interval': 3}],
    }


@pytest.mark.parametrize(
    'tariff_zones, filter_param_name, expected',
    (
        pytest.param(['moscow'], 'ok_key', 2),
        pytest.param(['moscow', 'vidnoe'], 'ok_key', 2),
        pytest.param(['vidnoe'], 'ok_key', 1),
        pytest.param(
            ['moscow', 'korolev'],
            'ok_key',
            1,
            marks=pytest.mark.xfail(raises=common.GeosubventionsConfigError),
        ),
    ),
)
async def test_get_filter_conf(tariff_zones, filter_param_name, expected):
    config = TestConfig()
    val = common.get_filter_conf(config, filter_param_name, tariff_zones)
    assert val == expected


@pytest.mark.parametrize(
    'tariff_zones, expected',
    (
        pytest.param(['moscow'], [{'shift_money': 1}, {'shift_interval': 1}]),
        pytest.param(
            ['moscow', 'vidnoe'], [{'shift_money': 1}, {'shift_interval': 1}],
        ),
        pytest.param(['vidnoe'], [{'shift_money': 1}]),
        pytest.param(
            ['moscow', 'korolev'],
            None,
            marks=pytest.mark.xfail(raises=common.GeosubventionsConfigError),
        ),
    ),
)
async def test_get_experiment(tariff_zones, expected):
    config = TestConfig()
    val = common.get_conf_for_zones(
        config, 'ATLAS_GEOSUBVENTIONS_EXPERIMENTS', tariff_zones,
    )
    assert val == expected
