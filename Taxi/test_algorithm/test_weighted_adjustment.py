# pylint: disable=W0621
import pytest

from .. import common

YT_LOGS = []
HEADERS = {
    'User-Agent': 'yandex-taxi/3.18.0.7675 Android/6.0 (testenv client)',
}


@pytest.fixture
def testpoint_service(testpoint):
    @testpoint('yt_logger::messages::calculations')
    def _handler(data_json):
        YT_LOGS.append(data_json)


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
                        # business
                        'surge': {'value': 1.0},
                        'calculation_meta': {
                            'pins_meta': {
                                'eta_by_category': common.JsonOverrideDelete(),
                                'surge_by_category': (
                                    common.JsonOverrideDelete()
                                ),
                                'pins_surge_b_percentiles': (
                                    common.JsonOverrideDelete()
                                ),
                            },
                        },
                    },
                    {
                        # econom
                        'value_raw': 1.8,
                        'surge': {'value': 1.8},
                        'calculation_meta': {
                            'deviation_from_target_abs': (
                                common.JsonOverrideDelete()
                            ),
                            'ps_shift_past_raw': common.JsonOverrideDelete(),
                            'ps': 4.466666666666667,
                            'f_derivative': common.JsonOverrideDelete(),
                            'smooth': {'point_a': {'value': 1.8}},
                            'pins_meta': {
                                'eta_by_category': common.JsonOverrideDelete(),
                                'surge_by_category': (
                                    common.JsonOverrideDelete()
                                ),
                            },
                        },
                    },
                ],
            },
            {
                'business': {
                    'extra': common.JsonOverrideDelete(),
                    # pipeline writes null, fallback writes nothing
                    # outcome is effectively the same
                    'smooth': {'point_b': common.JsonOverrideDelete()},
                    'pins_meta': {
                        'eta_by_category': common.JsonOverrideDelete(),
                        'surge_by_category': common.JsonOverrideDelete(),
                        'pins_surge_b_percentiles': (
                            common.JsonOverrideDelete()
                        ),
                    },
                },
                'econom': {
                    'deviation_from_target_abs': common.JsonOverrideDelete(),
                    'ps_shift_past_raw': common.JsonOverrideDelete(),
                    'extra': common.JsonOverrideDelete(),
                    'ps': 4.466666666666667,
                    'f_derivative': common.JsonOverrideDelete(),
                    'smooth': {
                        'point_a': {'value': 1.8},
                        'point_b': common.JsonOverrideDelete(),
                    },
                    'pins_meta': {
                        'eta_by_category': common.JsonOverrideDelete(),
                        'surge_by_category': common.JsonOverrideDelete(),
                    },
                },
            },
        ),
    ],
    ids=['pipeline_execution', 'native_fallback'],
)
@pytest.mark.parametrize(
    'umlaas_fail,corp_client_id,use_umlaas_pricing',
    [
        (True, None, False),
        (False, 'limitedguy', False),
        (False, 'limitedguy', True),
    ],
)
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business'], SURGE_ENABLE_UMLAAS_STATISTICS=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='weighted_surge_adjustment',
    consumers=['surge-calculator/user'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='sample_dynamic_config',
    consumers=['surge-calculator/user'],
    clauses=[],
    default_value={'foo': 'bar', 'eleven': [11]},
    is_config=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='surge_corp_limit',
    consumers=['surge-calculator/user'],
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'corp_client_id',
                    'set': ['limitedguy'],
                    'set_elem_type': 'string',
                },
            },
            'value': {
                'econom': {'min': 1.0, 'max': 1.9},
                'business': {'min': 1.0, 'max': 1.3},
            },
        },
    ],
    default_value={},
    is_config=True,
)
async def test_basic(
        taxi_surge_calculator,
        mockserver,
        testpoint_service,
        load_json,
        taxi_config,
        enable_native_fallback,
        expected_response_override,
        expected_full_calculation_meta_override,
        umlaas_fail,
        corp_client_id,
        use_umlaas_pricing,
        experiments3,
):
    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        assert sorted(request.json.get('allowed_classes', [])) == [
            'business',
            'econom',
        ]

        response = {
            'radius': 2785,
            'reposition': {},
            'generic': {
                'econom': {
                    'free': 12,
                    'free_chain': 3,
                    'total': 30,
                    'free_chain_groups': {'short': 3, 'medium': 3, 'long': 3},
                },
                'business': {
                    'free': 2,
                    'on_order': 3,
                    'free_chain': 1,
                    'total': 5,
                    'free_chain_groups': {'short': 1, 'medium': 1, 'long': 1},
                },
            },
        }

        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'}, json=response,
        )

    @mockserver.json_handler('/pin-storage/v1/get_stats/radius')
    def _get_stats_radius(request):
        request = dict(request.query)
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

    actual_req_surge_statistics = None

    @mockserver.json_handler(
        '/umlaas-pricing/umlaas-pricing/v1/surge-statistics',
    )
    def _umlaas_pricing_surge_statistics(request):
        request = request.json

        nonlocal actual_req_surge_statistics
        actual_req_surge_statistics = request

        assert use_umlaas_pricing

        if umlaas_fail:
            return mockserver.make_response('Resource fail', status=500)

        return {
            'by_category': {
                'econom': {
                    'results': [
                        {'name': 'sample_one', 'value': 18.1},
                        {'name': 'sample_two', 'value': 11.2},
                    ],
                },
            },
        }

    @mockserver.json_handler('/umlaas/umlaas/v1/surge-statistics')
    def _surge_statistics(request):
        request = request.json

        nonlocal actual_req_surge_statistics
        actual_req_surge_statistics = request

        assert not use_umlaas_pricing
        if umlaas_fail:
            return mockserver.make_response('Resource fail', status=500)

        return {
            'by_category': {
                'econom': {
                    'results': [
                        {'name': 'sample_one', 'value': 18.1},
                        {'name': 'sample_two', 'value': 11.2},
                    ],
                },
            },
        }

    if use_umlaas_pricing:
        experiments3.add_experiments_json(
            load_json(
                'umlaas_pricing_surge_statistic_enabled_exp3_config.json',
            ),
        )
    else:
        experiments3.add_experiments_json(
            load_json(
                'umlaas_pricing_surge_statistic_disabled_exp3_config.json',
            ),
        )

    taxi_config.set_values(
        {'SURGE_NATIVE_FALLBACK_FORCE': enable_native_fallback},
    )

    expected_result = {
        'method': 1,
        'zone_id': 'Funtown',
        'classes': [
            {
                'antisurge': False,
                'br': [13.025671809614137, 12.974826113235078],
                'tl': [12.974328190385863, 13.025173886764922],
                'free': 12,
                'free_chain': 3,
                'name': 'econom',
                'reason': 'pins_free',
                'value': 1.5,
                'value_raw': 1.5,
                'value_smooth': 1,
                'value_smooth_is_default': True,
                'pins': 3,
                'pins_meta': {
                    'pins_b': 0,
                    'pins_order': 0,
                    'pins_driver': 0,
                    'prev_pins': 2.8800000000000003,
                    'eta_in_tariff': 0.0,
                    'surge_in_tariff': 0.0,
                    'pins_order_in_tariff': 0,
                    'pins_driver_in_tariff': 0,
                },
                'radius': 2785,
                'total': 30,
                'f_derivative': -0.056999999999999995,
                'ps': 8.836666666666668,
                'eta': 5.78220960242758,
                'etr': 2.8293345405160704,
                'deviation_from_target_abs': 2.22,
                'ps_shift_past_raw': 3.33,
            },
            {
                'antisurge': False,
                'br': [13.025671809614137, 12.974826113235078],
                'free': 2,
                'free_chain': 1,
                'name': 'business',
                'pins': 3,
                'pins_meta': {
                    'pins_b': 0,
                    'pins_order': 0,
                    'pins_driver': 0,
                    'cost': 1.1,
                    'distance': 11,
                    'time': 1,
                    'prev_pins': 2.8800000000000003,
                    'eta_in_tariff': 0.0,
                    'surge_in_tariff': 0.0,
                    'surge_b_in_tariff': 0.1,
                    'pins_order_in_tariff': 0,
                    'pins_driver_in_tariff': 0,
                    'pins_surge_b_percentiles': [
                        dict(percentile=prc, value=val)
                        for prc, val in [(50, 0), (70, 1), (95, 2), (98, 3)]
                    ],
                },
                'radius': 2785.0,
                'reason': 'pins_free',
                'tl': [12.974328190385863, 13.025173886764922],
                'total': 5,
                'value': (
                    1.1
                ),  # weighted adjustment: 1.0 + (1.5 - 1.0) / (1 + 5) ~ 1.1
                'value_raw': 1.0,
                'value_smooth': 1.0,
                'value_smooth_is_default': True,
            },
        ],
        'experiments': [],
    }

    expected_result = common.convert_response(
        expected_result,
        base={'experiment_id': 'e5d8a86361064b17833c3a42d7fd6b38'},
        class_info_base={},
    )

    request = {
        'user_id': 'a29e6a811131450f9a28337906594208',
        'classes': ['econom', 'business'],
        'point_a': [13, 13],
    }
    if corp_client_id:
        request['corp_client_id'] = corp_client_id

    await taxi_surge_calculator.invalidate_caches()
    response = await taxi_surge_calculator.post(
        'v1/calc-surge', json=request, headers=HEADERS,
    )

    assert response.status == 200, response.text
    expected_full_calculation_meta = load_json(
        'expected_full_calculation_meta.json',
    )

    if corp_client_id:
        expected = {
            'econom': {'min': 1.0, 'max': 1.9},
            'business': {'min': 1.0, 'max': 1.3},
        }
        meta = expected_full_calculation_meta
        for key, value in expected.items():
            meta[key]['extra']['corp_bound'] = value

    if umlaas_fail:
        econom_extra = expected_full_calculation_meta['econom']['extra']
        del econom_extra['surge_statistics']

    actual_result = response.json()
    calculation_id = actual_result.pop('calculation_id', '')

    assert len(calculation_id) == 32

    common.sort_data(actual_result)
    common.sort_data(expected_result)

    expected_result = common.json_override(
        expected_result, expected_response_override,
    )

    assert actual_result == expected_result

    full_calculation_meta = common.get_full_calculation_meta(YT_LOGS)[
        calculation_id
    ]
    expected_full_calculation_meta = common.json_override(
        expected_full_calculation_meta,
        expected_full_calculation_meta_override,
    )
    assert full_calculation_meta == expected_full_calculation_meta

    if enable_native_fallback:
        return

    assert actual_req_surge_statistics == {
        'point_a': [13.0, 13.0],
        'radius': 2785,
        'user_id': 'a29e6a811131450f9a28337906594208',
        'client': {'name': 'android', 'version': [3, 18, 0]},
        'by_category': {
            'business': {
                'free': 2,
                'free_chain': 1,
                'pins': 3,
                'pins_b': 0,
                'pins_order': 0,
                'prev_chain': 0.0,
                'prev_eta': 0.0,
                'prev_free': 0.0,
                'prev_pins': 2.8800000000000003,
                'prev_surge': 0.0,
                'prev_total': 0.0,
                'total': 5,
            },
            'econom': {
                'free': 12,
                'free_chain': 3,
                'pins': 3,
                'pins_b': 0,
                'pins_order': 0,
                'prev_pins': 2.8800000000000003,
                'total': 30,
            },
        },
    }
    if umlaas_fail:
        stage_logs = common.get_stage_logs(YT_LOGS)[calculation_id]
        fetch_umlaas_stage_logs = stage_logs['fetch_surge_statistics']

        assert len(fetch_umlaas_stage_logs) == 1
        assert fetch_umlaas_stage_logs[0]['$level'] == 'error'
        assert fetch_umlaas_stage_logs[0]['$region'] == 'native_code'
        assert 'Stage failed' in fetch_umlaas_stage_logs[0]['$message']
