import pytest

from .. import common

SURGE_MAP_VALUES = [
    {'x': 0, 'y': 0, 'surge': 1.3851438760757446, 'weight': 1.0},
]

POINT_IN_SURGE = [37.752806233, 55.9]


@pytest.mark.parametrize('enable_native_fallback', [False, True])
@pytest.mark.parametrize(
    'no_explicit_antisurge_threshold,'
    'surcharge_enabled,partial_request,expected',
    [
        pytest.param(
            False,  # no_explicit_antisurge_threshold
            False,  # surcharge_enabled
            {'point_a': [37.0, 55.9], 'point_b': POINT_IN_SURGE},
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'business',
                        'reason': 'rain',
                        'value': 0.6,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.0,
                        'value_smooth_b_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 0.7,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.3851438760757446,
                        'value_smooth_b_is_default': False,
                        'explicit_antisurge': {'value': 0.6},
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Yandex HQ2',
            },
            id='implicit fixed price for both classes',
        ),
        pytest.param(
            False,  # no_explicit_antisurge_threshold
            False,  # surcharge_enabled
            {
                'point_a': [37.0, 55.9],
                'point_b': POINT_IN_SURGE,
                'fixed_price_classes': ['business', 'econom'],
            },
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'business',
                        'reason': 'rain',
                        'value': 0.6,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.0,
                        'value_smooth_b_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 0.7,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.3851438760757446,
                        'value_smooth_b_is_default': False,
                        'explicit_antisurge': {'value': 0.6},
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Yandex HQ2',
            },
            id='fixed price for both classes',
        ),
        pytest.param(
            False,  # no_explicit_antisurge_threshold
            True,  # surcharge_enabled
            {
                'point_a': [37.0, 55.9],
                'point_b': POINT_IN_SURGE,
                'fixed_price_classes': ['business', 'econom'],
            },
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'business',
                        'reason': 'rain',
                        'value': 0.6,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.0,
                        'value_smooth_b_is_default': True,
                        'surcharge_alpha': 1.0,
                        'surcharge_beta': 0.0,
                        'surcharge': 0.0,
                    },
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 0.7,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.3851438760757446,
                        'value_smooth_b_is_default': False,
                        'surcharge_alpha': 1.0,
                        'surcharge_beta': 0.0,
                        'surcharge': 0.0,
                        'explicit_antisurge': {
                            'value': 0.6,
                            'surcharge_alpha': 1.0,
                            'surcharge_beta': 0.0,
                            'surcharge': 0.0,
                        },
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Yandex HQ2',
            },
            id='fixed price for both classes with surcharge',
        ),
        pytest.param(
            False,  # no_explicit_antisurge_threshold
            False,  # surcharge_enabled
            {
                'point_a': [37.0, 55.73425398624534],
                'fixed_price_classes': ['business', 'econom'],
            },
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'business',
                        'reason': 'rain',
                        'value': 0.6,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 0.7,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Yandex HQ2',
            },
            id='fixed price for both classes, no point B',
        ),
        pytest.param(
            False,  # no_explicit_antisurge_threshold
            False,  # surcharge_enabled
            {
                'point_a': [37.0, 55.73425398624534],
                'point_b': [0.0, 0.0],
                'fixed_price_classes': ['business', 'econom'],
            },
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'business',
                        'reason': 'rain',
                        'value': 0.6,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.0,
                        'value_smooth_b_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 0.7,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.0,
                        'value_smooth_b_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Yandex HQ2',
            },
            id='fixed price for both classes, no point B surge',
        ),
        pytest.param(
            False,  # no_explicit_antisurge_threshold
            False,  # surcharge_enabled
            {
                'point_a': [37.0, 55.73425398624534],
                'point_b': [0.0, 0.0],
                'fixed_price_classes': ['business'],
            },
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'business',
                        'reason': 'rain',
                        'value': 0.6,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.0,
                        'value_smooth_b_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 1.0,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.0,
                        'value_smooth_b_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Yandex HQ2',
            },
            id='business - fixed, econom - not fixed, no actual point B surge',
        ),
        pytest.param(
            False,  # no_explicit_antisurge_threshold
            False,  # surcharge_enabled
            {
                'point_a': [37.0, 55.73425398624534],
                'point_b': [0.0, 0.0],
                'fixed_price_classes': ['econom'],
            },
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'business',
                        'reason': 'rain',
                        'value': 1.0,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.0,
                        'value_smooth_b_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 0.7,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.0,
                        'value_smooth_b_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Yandex HQ2',
            },
            id='business - not fixed, econom - fixed, no actual point B surge',
        ),
        pytest.param(
            False,  # no_explicit_antisurge_threshold
            False,  # surcharge_enabled
            {
                'point_a': [37.0, 55.73425398624534],
                'point_b': POINT_IN_SURGE,
                'fixed_price_classes': [],
            },
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'business',
                        'reason': 'rain',
                        'value': 1.0,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.0,
                        'value_smooth_b_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 1.0,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.3851438760757446,
                        'value_smooth_b_is_default': False,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Yandex HQ2',
            },
            id='explicitly not fixed price',
        ),
        pytest.param(
            True,  # no_explicit_antisurge_threshold
            False,  # surcharge_enabled
            {
                'point_a': [37.0, 55.73425398624534],
                'point_b': POINT_IN_SURGE,
                'fixed_price_classes': ['business', 'econom'],
            },
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'business',
                        'reason': 'rain',
                        'value': 0.6,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.0,
                        'value_smooth_b_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'value': 0.6,
                        'value_raw': 0.6,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                        'value_smooth_b': 1.3851438760757446,
                        'value_smooth_b_is_default': False,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Yandex HQ2',
            },
            id='fixed price for both classes, no explicit antisurge threshold',
        ),
    ],
)
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business'],
    SURGE_ENABLE_ANTISURGE=True,
    SURGE_ENABLE_EXPLICIT_ANTISURGE=True,
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
        taxi_config,
        enable_native_fallback,
        no_explicit_antisurge_threshold,
        surcharge_enabled,
        partial_request,
        expected,
):
    if enable_native_fallback:
        for class_info in expected['classes']:
            # fallback uses value_raw as default smooth surge by default
            if class_info['value_smooth_is_default']:
                class_info['value_smooth'] = class_info['value_raw']
    expected = common.convert_response(
        expected,
        base={'experiment_id': 'da522a9106f3450d8e80c4aa8da915ad'},
        class_info_base={},
    )

    if enable_native_fallback:
        expected['calculation_type'] = 'default'
        expected['fallback_type'] = 'native_algorithm'

    zone = admin_surger.zones['MSK-Yandex HQ2']
    for exp in zone['forced']:
        if exp['experiment_name'] == 'default':
            if not surcharge_enabled:
                exp['surcharge_enabled'] = False

            if no_explicit_antisurge_threshold:
                del exp['explicit_antisurge_threshold']

    taxi_config.set_values(
        {'SURGE_NATIVE_FALLBACK_FORCE': enable_native_fallback},
    )

    await taxi_surge_calculator.invalidate_caches()

    surger_request = {
        'user_id': 'a29e6a811131450f9a28337906594208',
        'client': {'name': 'iphone', 'version': [3, 82, 6434]},
    }
    surger_request.update(partial_request)

    response = await taxi_surge_calculator.post(
        '/v1/calc-surge', json=surger_request,
    )

    assert response.status == 200, response.text
    actual_result = response.json()
    common.sort_data(actual_result)
    assert len(actual_result.pop('calculation_id', '')) == 32
    assert actual_result == expected
