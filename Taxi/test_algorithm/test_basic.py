# pylint: disable=W0621
import pytest

from .. import common

YT_LOGS = []
RESOURCE_REQUESTS = []


@pytest.fixture
def mocks_and_testpoint(testpoint, mockserver):
    @testpoint('yt_logger::messages::calculations')
    def _handler(data_json):
        YT_LOGS.append(data_json)

    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        request = request.json

        response = {'radius': 2785, 'generic': {}, 'reposition': {}}

        for category in request.get('allowed_classes', []):
            response['generic'][category] = {
                'free': 12,
                'on_order': 18,
                'free_chain': 3,
                'total': 30,
                'free_chain_groups': {'short': 3, 'medium': 3, 'long': 3},
            }

        request['__resource_name__'] = 'count_by_categories'
        RESOURCE_REQUESTS.append(request)
        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'}, json=response,
        )

    @mockserver.json_handler('/pin-storage/v1/get_stats/radius')
    def _get_stats_radius(request):
        request = dict(request.query)

        request['__resource_name__'] = 'get_stats/radius'
        RESOURCE_REQUESTS.append(request)

        high_surge_b = request.get('high_surge_b')
        if high_surge_b is not None:
            percentiles = [
                dict(percentile=int(el), value=i)
                for i, el in enumerate(high_surge_b.split(','))
            ]
        else:
            percentiles = None

        return {
            'stats': {
                'pins': 3,
                'pins_with_b': 0,
                'pins_with_order': 0,
                'pins_with_driver': 0,
                'prev_pins': 2.8800000000000003,
                'values_by_category': {
                    'business': {
                        'estimated_waiting': 0,
                        'surge': 0,
                        'surge_b': 0.1,
                        'pins_order_in_tariff': 0,
                        'pins_driver_in_tariff': 0,
                        'cost': 1.1,
                        'trip': {'distance': 11, 'time': 1},
                        'pins_surge_b_percentiles': percentiles,
                    },
                },
                'global_pins': 3,
                'global_pins_with_order': 0,
                'global_pins_with_driver': 0,
            },
        }


@pytest.mark.parametrize(
    'enable_native_fallback,expected_response_override,'
    'expected_full_calculation_meta_override',
    [
        (False, None, None),
        (
            True,
            {
                'calculation_type': 'default',
                'fallback_type': 'native_algorithm',
                'classes': [
                    {
                        # econom
                        'value_raw': 1.8,
                        'surge': {'value': 1.8},
                        'calculation_meta': {
                            'ps': 4.466666666666667,
                            'f_derivative': common.JsonOverrideDelete(),
                            'smooth': {'point_a': {'value': 1.8}},
                            'deviation_from_target_abs': (
                                common.JsonOverrideDelete()
                            ),
                            'ps_shift_past_raw': common.JsonOverrideDelete(),
                        },
                    },
                ],
            },
            {
                'econom': {
                    'deviation_from_target_abs': common.JsonOverrideDelete(),
                    'ps_shift_past_raw': common.JsonOverrideDelete(),
                    'ps': 4.466666666666667,
                    'f_derivative': common.JsonOverrideDelete(),
                    'smooth': {
                        'point_a': {'value': 1.8},
                        'point_b': common.JsonOverrideDelete(),
                    },
                },
            },
        ),
    ],
    ids=['pipeline_execution', 'native_fallback'],
)
@pytest.mark.now('2020-07-06T19:21:49+03:00')
async def test_algorithm_basic(
        taxi_surge_calculator,
        mocks_and_testpoint,
        load_json,
        taxi_config,
        enable_native_fallback,
        expected_response_override,
        expected_full_calculation_meta_override,
):
    YT_LOGS.clear()
    RESOURCE_REQUESTS.clear()

    taxi_config.set_values(
        {'SURGE_NATIVE_FALLBACK_FORCE': enable_native_fallback},
    )

    request = {
        'user_id': 'a29e6a811131450f9a28337906594208',
        'classes': ['econom'],
        'point_a': [13, 13],
    }
    expected_response = {
        'zone_id': 'Funtown',
        'user_layer': 'default',
        'experiment_id': 'e5d8a86361064b17833c3a42d7fd6b38',
        'experiment_name': 'default',
        'experiment_layer': 'default',
        'is_cached': False,
        'classes': [
            {
                'name': 'econom',
                'value_raw': 1.5,
                'surge': {'value': 1.5},
                'calculation_meta': {
                    'counts': {
                        'free': 12,
                        'free_chain': 3,
                        'pins': 3,
                        'radius': 2785,
                        'total': 30,
                    },
                    'smooth': {'point_a': {'value': 1.0, 'is_default': True}},
                    'f_derivative': -0.056999999999999995,
                    'pins_meta': {
                        'eta_in_tariff': 0.0,
                        'surge_in_tariff': 0.0,
                        'pins_order_in_tariff': 0,
                        'pins_driver_in_tariff': 0,
                        'pins_b': 0,
                        'pins_order': 0,
                        'pins_driver': 0,
                        'prev_pins': 2.8800000000000003,
                    },
                    'ps': 8.836666666666668,
                    'reason': 'pins_free',
                    'deviation_from_target_abs': 2.22,
                    'ps_shift_past_raw': 3.33,
                },
            },
        ],
        'experiments': [],
        'experiment_errors': [],
    }

    expected_resource_requests = [
        {
            '__resource_name__': 'count_by_categories',
            'allowed_classes': ['econom'],
            'limit': 400,
            'max_distance': 2500,
            'point': [13, 13],
        },
        {
            '__resource_name__': 'get_stats/radius',
            'categories': 'econom',
            'point': '13.000000,13.000000',
            'radius': '2785.000000',
        },
    ]

    if not enable_native_fallback:
        expected_resource_requests[1]['high_surge_b'] = '50,70,95,98'

    await taxi_surge_calculator.invalidate_caches()
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)

    assert RESOURCE_REQUESTS == expected_resource_requests
    assert response.status == 200, response.text
    expected_full_calculation_meta = load_json(
        'expected_full_calculation_meta.json',
    )
    actual_response = response.json()
    calculation_id = actual_response.pop('calculation_id', '')

    assert len(calculation_id) == 32

    common.sort_data(expected_response)
    common.sort_data(actual_response)

    expected_response = common.json_override(
        expected_response, expected_response_override,
    )

    assert actual_response == expected_response

    full_calculation_meta = common.get_full_calculation_meta(YT_LOGS)[
        calculation_id
    ]

    expected_full_calculation_meta = common.json_override(
        expected_full_calculation_meta,
        expected_full_calculation_meta_override,
    )

    assert full_calculation_meta == expected_full_calculation_meta


@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    SURGE_ENABLE_SURCHARGE=True,
    SURGE_APPLY_BOUNDS_TO_LINEAR_DEPENDENCY_WITH_BASE_TABLE=True,
)
@pytest.mark.parametrize(
    'resource_logging_mode', ['none', 'params', 'instance', 'instance_params'],
)
async def test_yt_logs_resources(
        taxi_surge_calculator,
        load_json,
        taxi_config,
        mocks_and_testpoint,
        resource_logging_mode,
):
    YT_LOGS.clear()

    taxi_config.set_values(
        {
            'SURGE_PIPELINE_EXECUTION': {
                'ENABLE_UNIFIED_STAGE_OUT_LOGGING': True,
                'UNIFIED_RESOURCES_LOGGING_MODE': resource_logging_mode,
            },
        },
    )
    await taxi_surge_calculator.invalidate_caches()

    expected_yt_logs = load_json(
        f'{resource_logging_mode}_resource_logging.yt_logs.json',
    )

    req = {'tariffs': ['econom'], 'point_a': [13, 13], 'tariff_zone': 'moscow'}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=req)

    assert response.status == 200, response.text

    actual_response = response.json()
    calculation_id = actual_response.pop('calculation_id', '')

    assert len(calculation_id) == 32
    expected_yt_logs[0]['calculation_id'] = calculation_id
    del YT_LOGS[-1]['timestamp']
    del YT_LOGS[0]['calculation']['$pipeline_id']

    assert expected_yt_logs == YT_LOGS
