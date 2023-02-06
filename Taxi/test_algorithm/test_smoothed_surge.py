import pytest

from .. import common

SURGE_MAP_VALUES = [
    {'x': 0, 'y': 0, 'surge': 1.3851438760757446, 'weight': 1.0},
]

POINT_IN_SURGE = [37.752806233, 55.9]


@pytest.mark.parametrize(
    'surcharge_enabled,partial_request,expected_result',
    [
        pytest.param(
            False,
            {'point_a': POINT_IN_SURGE, 'point_b': POINT_IN_SURGE},
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 1.3,
                        'value_raw': 1.2,
                        'value_smooth': 1.3851438760757446,
                        'value_smooth_is_default': False,
                        'value_smooth_b': 1.3851438760757446,
                        'value_smooth_b_is_default': False,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'SmoothedSurgeTestId',
            },
            id='basic',
        ),
        pytest.param(
            False,  # surcharge_enabled
            {'point_a': POINT_IN_SURGE, 'point_b': [0.0, 0.0]},
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 1.3,  # smooth - max_jump_down (0.1)
                        'value_raw': 1.2,
                        'value_smooth': 1.3851438760757446,
                        'value_smooth_is_default': False,
                        'value_smooth_b': 0.9,
                        'value_smooth_b_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'SmoothedSurgeTestId',
            },
            id='no actual point B surge',
        ),
        pytest.param(
            True,  # surcharge_enabled
            {'point_a': POINT_IN_SURGE, 'point_b': [0.0, 0.0]},
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 1.3,  # smooth - max_jump_down (0.1)
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value_raw': 1.2,
                        'value_smooth': 1.3851438760757446,
                        'value_smooth_is_default': False,
                        'value_smooth_b': 0.9,
                        'value_smooth_b_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'SmoothedSurgeTestId',
            },
            id='no actual point B surge, surcharge enabled',
        ),
    ],
)
@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    SURGE_ENABLE_ANTISURGE=True,
    SURGE_ENABLE_SURCHARGE=True,
)
@pytest.mark.surge_heatmap(
    cell_size_meter=500.123,
    envelope={
        'br': [POINT_IN_SURGE[0] - 0.00001, POINT_IN_SURGE[1] - 0.00001],
        'tl': [POINT_IN_SURGE[0] + 0.1, POINT_IN_SURGE[1] + 0.1],
    },
    values=SURGE_MAP_VALUES,
)
async def test(
        taxi_surge_calculator,
        admin_surger,
        heatmap_storage_fixture,
        surcharge_enabled,
        partial_request,
        expected_result,
):
    expected_result = common.convert_response(
        expected_result,
        base={'experiment_id': 'da522a9106f3450d8e80c4aa8da915ad'},
        class_info_base={},
    )

    if not surcharge_enabled:
        zone = admin_surger.zones['SmoothedSurgeTestId']
        for exp in zone['forced']:
            if exp['experiment_name'] == 'default':
                exp['surcharge_enabled'] = False

    await taxi_surge_calculator.invalidate_caches()

    surger_request = {
        'user_id': 'a29e6a811131450f9a28337906594208',
        'client': {'name': 'iphone', 'version': [3, 82, 6434]},
    }
    surger_request.update(partial_request)

    response = await taxi_surge_calculator.post(
        'v1/calc-surge', json=surger_request,
    )
    assert response.status == 200, response.text
    actual_result = response.json()
    common.sort_data(actual_result)
    assert len(actual_result.pop('calculation_id', '')) == 32
    assert actual_result == expected_result


@pytest.mark.parametrize(
    'surcharge_enabled,partial_request,expected_result,use_default_surge',
    [
        (
            False,  # surcharge_enabled
            {'point_a': [31, 51], 'point_b': [32, 52]},
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 0.6,  # raw + max_jump_up (0.2)
                        'value_raw': 1.2,
                        'value_smooth': 0.4,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 0.9,
                        'value_smooth_b_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'SmoothedSurgeTestId',
            },
            {},
        ),
        (
            False,  # surcharge_enabled
            {'point_a': [31, 51], 'point_b': [32, 52]},
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 0.6,  # raw + max_jump_up (0.2)
                        'value_raw': 1.2,
                        'value_smooth': 0.4,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 0.9,
                        'value_smooth_b_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'SmoothedSurgeTestId',
            },
            {'__default__': False, 'SmoothedSurgeTest': True},
        ),
    ],
)
@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    SURGE_ENABLE_ANTISURGE=True,
    SURGE_ENABLE_SURCHARGE=True,
)
async def test_defaults(
        taxi_surge_calculator,
        admin_surger,
        surcharge_enabled,
        partial_request,
        expected_result,
        taxi_config,
        use_default_surge,
):
    expected_result = common.convert_response(
        expected_result,
        base={'experiment_id': 'da522a9106f3450d8e80c4aa8da915ad'},
        class_info_base={},
    )

    if not surcharge_enabled:
        zone = admin_surger.zones['SmoothedSurgeTestId']
        for exp in zone['forced']:
            if exp['experiment_name'] == 'default':
                exp['surcharge_enabled'] = False

    if use_default_surge:
        taxi_config.set_values(
            dict(SURGE_USE_DEFAULT_SURGE_IF_NO_SMOOTHING=use_default_surge),
        )
        await taxi_surge_calculator.invalidate_caches()

    surger_request = {
        'user_id': 'a29e6a811131450f9a28337906594208',
        'client': {'name': 'iphone', 'version': [3, 82, 6434]},
    }
    surger_request.update(partial_request)

    response = await taxi_surge_calculator.post(
        'v1/calc-surge', json=surger_request,
    )
    assert response.status == 200, response.text
    actual_result = response.json()
    common.sort_data(actual_result)
    assert len(actual_result.pop('calculation_id', '')) == 32
    assert actual_result == expected_result
