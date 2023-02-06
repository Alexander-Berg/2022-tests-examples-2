import pytest

from .. import common

VALUE_IN_MAP = 1.3851438760757446
SURGE_MAP_VALUES = [{'x': 0, 'y': 0, 'surge': VALUE_IN_MAP, 'weight': 1.0}]

POINT_IN_SURGE = [37.583369, 55.778821]
POINT_OUT_OF_SURGE = [37.0, 55.778821]


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business'], SURGE_NATIVE_FALLBACK_FORCE=True,
)
@pytest.mark.surge_heatmap(
    cell_size_meter=500.123,
    envelope={
        'br': [POINT_IN_SURGE[0] - 0.00001, POINT_IN_SURGE[1] - 0.00001],
        'tl': [POINT_IN_SURGE[0] + 0.1, POINT_IN_SURGE[1] + 0.1],
    },
    values=SURGE_MAP_VALUES,
)
@pytest.mark.parametrize(
    'expected_code,no_counts,no_base_class_map,expected_response_override',
    [
        pytest.param(200, False, False, None, id='has_counts_and_map'),
        pytest.param(
            200,
            True,
            False,
            {
                'classes': [
                    {  # business
                        'value_raw': VALUE_IN_MAP,
                        'surge': {
                            'value': 1.5,
                            'surcharge': {
                                'alpha': 0.3,
                                'beta': 0.7,
                                'value': 99,
                            },
                        },
                        'calculation_meta': common.JsonOverrideOverwrite(
                            {
                                'reason': 'linear_dependency',
                                'degradation_level': 'linear_dependency',
                                'smooth': {
                                    'point_a': {
                                        'value': VALUE_IN_MAP,
                                        'is_default': (
                                            True  # smoothing is disabled
                                        ),
                                    },
                                },
                            },
                        ),
                    },
                    {  # econom
                        'value_raw': VALUE_IN_MAP,
                        'surge': {
                            'value': 1.5,
                            'surcharge': {
                                'alpha': 0.3,
                                'beta': 0.7,
                                'value': 99,
                            },
                        },
                        'calculation_meta': common.JsonOverrideOverwrite(
                            {
                                'reason': 'pins_free',
                                'degradation_level': 'value_raw_from_map',
                                'smooth': {
                                    'point_a': {
                                        'value': VALUE_IN_MAP,
                                        'is_default': (
                                            True  # smoothing is disabled
                                        ),
                                    },
                                },
                            },
                        ),
                    },
                ],
            },
            id='no_counts',
        ),
    ],
)
async def test_native_fallback_degradation(
        taxi_surge_calculator,
        mockserver,
        load_json,
        expected_code,
        no_counts,
        no_base_class_map,
        expected_response_override,
        heatmap_storage_fixture,
):
    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        if no_counts:
            return mockserver.make_response('Intentional Error', status=500)

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

        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'}, json=response,
        )

    @mockserver.json_handler('/pin-storage/v1/get_stats/radius')
    def _add_pin_radius(request):
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
                        'pins_order_in_tariff': 0,
                        'pins_driver_in_tariff': 0,
                        'surge': 0,
                    },
                },
                'global_pins': 3,
                'global_pins_with_order': 0,
                'global_pins_with_driver': 0,
            },
        }

    request = {
        'point_a': POINT_OUT_OF_SURGE if no_base_class_map else POINT_IN_SURGE,
        'classes': ['econom', 'business'],
    }

    expected_response = load_json('expected_response.json')

    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == expected_code, response.text
    if expected_code != 200:
        return

    response = response.json()
    response.pop('calculation_id')

    common.sort_data(response)
    common.sort_data(expected_response)

    expected_response = common.json_override(
        expected_response, expected_response_override,
    )

    assert expected_response == response
