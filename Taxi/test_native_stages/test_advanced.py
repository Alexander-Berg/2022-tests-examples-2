import uuid

import pytest

from .. import common


YT_LOGS = []
JS_PIPELINE_ACTIVITIES = []
RESOURCE_REQUESTS = []


# Cases to test:
# 1) Native section at start
# 2) Native section in JS non blocking (via call)
# 3) Native section in JS blocking (via yield)
# 4) Native section at end
# 5) + stage status condition
# 6) + native predicate

# 7) Stage with JS bindings and conditions, but native body and output
# 8) + native predicate
# 9) + partially native predicate
# 10) + not native predicate
# 11) + blocking


@pytest.fixture(autouse=True)
def testpoint_service(testpoint):
    @testpoint('yt_logger::messages::calculations')
    def _handler1(data_json):
        YT_LOGS.append(data_json)

    @testpoint('js-pipeline')
    def _handler2(data_json):
        JS_PIPELINE_ACTIVITIES.append(data_json['activity'])


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business'], SURGE_COEFFICIENT_PRECISION=2,
)
@pytest.mark.now('2020-05-27T14:03:10')
@pytest.mark.parametrize(
    'stages,expected_override,expected_activities',
    [
        pytest.param(
            ['native_init', 'js_update_raw'],
            {},
            ['run_pre_js_native_section', 'js_execution'],
            id='native_stage_at_start',
        ),
        pytest.param(
            ['js_init_not_rounded', 'native_round', 'js_update_raw'],
            {
                'classes': [
                    {
                        'surge': {
                            'value': 1.12,
                            'surcharge': {
                                'value': 100,
                                'alpha': 0.854,
                                'beta': 0.13,
                            },
                        },
                        'calculation_meta': {'reason': 'pins_free'},
                    },
                    {
                        'surge': {
                            'value': 1.12,
                            'surcharge': {
                                'value': 100,
                                'alpha': 0.854,
                                'beta': 0.13,
                            },
                        },
                        'calculation_meta': {'reason': 'pins_free'},
                    },
                ],
            },
            ['js_execution', 'js_to_native_section'],
            id='native_section_call',
        ),
        pytest.param(
            [
                'native_is_present',
                'js_init_not_rounded',
                (
                    'native_round',
                    {
                        'conditions': [
                            {
                                'args': [{'name': 'value', 'value': 'surge'}],
                                'predicate': 'native_is_present',
                                'type': 'predicate',
                            },
                        ],
                    },
                ),
                'native_fetch_driver_info',
                'js_apply_driver_info',
                (
                    'js_round_raw',
                    {
                        'conditions': [
                            {
                                'args': [
                                    {'name': 'value', 'value': 'value_raw'},
                                ],
                                'predicate': 'native_is_present',
                                'type': 'predicate',
                            },
                        ],
                    },
                ),
            ],
            {
                'classes': [
                    {
                        'surge': {
                            'value': 1.12,
                            'surcharge': {
                                'value': 100,
                                'alpha': 0.854,
                                'beta': 0.13,
                            },
                        },
                        'value_raw': 1.43,  # round 10/7 with precision 2
                        'calculation_meta': {'reason': 'pins_free'},
                    },
                    {
                        'surge': {
                            'value': 1.12,
                            'surcharge': {
                                'value': 100,
                                'alpha': 0.854,
                                'beta': 0.13,
                            },
                        },
                        'value_raw': 1.43,
                        'calculation_meta': {'reason': 'pins_free'},
                    },
                ],
            },
            [
                'run_pre_js_native_section',
                'js_execution',
                'js_to_native_section_yield',
                'js_to_native_predicate',
                'js_to_native_predicate',
            ],
            id='native_section_yield',
        ),
        pytest.param(
            [
                'semi_native_is_present',
                'js_init_not_rounded',
                (
                    'native_round',
                    {
                        'conditions': [
                            {
                                'args': [{'name': 'value', 'value': 'surge'}],
                                'predicate': 'semi_native_is_present',
                                'type': 'predicate',
                            },
                        ],
                    },
                ),
                'native_fetch_driver_info',
                'js_apply_driver_info',
                'js_round_raw',
            ],
            {
                'classes': [
                    {
                        'surge': {
                            'value': 1.12,
                            'surcharge': {
                                'value': 100,
                                'alpha': 0.854,
                                'beta': 0.13,
                            },
                        },
                        'value_raw': 1.43,  # round 10/7 with precision 2
                        'calculation_meta': {'reason': 'pins_free'},
                    },
                    {
                        'surge': {
                            'value': 1.12,
                            'surcharge': {
                                'value': 100,
                                'alpha': 0.854,
                                'beta': 0.13,
                            },
                        },
                        'value_raw': 1.43,
                        'calculation_meta': {'reason': 'pins_free'},
                    },
                ],
            },
            [
                'js_execution',
                'js_to_native_function',
                'js_to_native_stage',
                'js_to_native_function',
                'js_to_native_stage',
                'js_to_native_section_yield',
            ],
            id='semi_native_predicate',
        ),
        pytest.param(
            [
                'js_is_present',
                'js_init_not_rounded',
                'native_round',
                (
                    'native_fetch_driver_info',
                    {
                        'conditions': [
                            {
                                'args': [
                                    {'name': 'value', 'value': 'point_a'},
                                ],
                                'predicate': 'js_is_present',
                                'type': 'predicate',
                            },
                        ],
                    },
                ),
                'js_apply_driver_info',
                'js_round_raw',
            ],
            {
                'classes': [
                    {
                        'surge': {
                            'value': 1.12,
                            'surcharge': {
                                'value': 100,
                                'alpha': 0.854,
                                'beta': 0.13,
                            },
                        },
                        'value_raw': 1.43,  # round 10/7 with precision 2
                        'calculation_meta': {'reason': 'pins_free'},
                    },
                    {
                        'surge': {
                            'value': 1.12,
                            'surcharge': {
                                'value': 100,
                                'alpha': 0.854,
                                'beta': 0.13,
                            },
                        },
                        'value_raw': 1.43,
                        'calculation_meta': {'reason': 'pins_free'},
                    },
                ],
            },
            [
                'js_execution',
                'js_to_native_section',
                'js_to_native_stage_yield',
            ],
            id='native_stage_yield',
        ),
        pytest.param(
            ['js_is_present', 'js_init_not_rounded', 'native_round'],
            {
                'classes': [
                    {
                        'surge': {
                            'value': 1.12,
                            'surcharge': {
                                'value': 100,
                                'alpha': 0.854,
                                'beta': 0.13,
                            },
                        },
                        'value_raw': 1.02345,
                        'calculation_meta': {'reason': 'pins_free'},
                    },
                    {
                        'surge': {
                            'value': 1.12,
                            'surcharge': {
                                'value': 100,
                                'alpha': 0.854,
                                'beta': 0.13,
                            },
                        },
                        'value_raw': 1.02345,
                        'calculation_meta': {'reason': 'pins_free'},
                    },
                ],
            },
            ['js_execution', 'run_post_js_native_section'],
            id='native_section_at_end',
        ),
        pytest.param(
            [
                'js_is_present',
                'js_init_not_rounded',
                (
                    'native_round',
                    {
                        'conditions': [
                            {
                                'args': [{'name': 'value', 'value': 'surge'}],
                                'predicate': 'js_is_present',
                                'type': 'predicate',
                            },
                        ],
                    },
                ),
            ],
            {
                'classes': [
                    {
                        'surge': {
                            'value': 1.12,
                            'surcharge': {
                                'value': 100,
                                'alpha': 0.854,
                                'beta': 0.13,
                            },
                        },
                        'value_raw': 1.02345,
                        'calculation_meta': {'reason': 'pins_free'},
                    },
                    {
                        'surge': {
                            'value': 1.12,
                            'surcharge': {
                                'value': 100,
                                'alpha': 0.854,
                                'beta': 0.13,
                            },
                        },
                        'value_raw': 1.02345,
                        'calculation_meta': {'reason': 'pins_free'},
                    },
                ],
            },
            ['js_execution', 'js_to_native_stage', 'js_to_native_stage'],
            id='native_stage_call_at_end',
        ),
    ],
)
async def test_native_stages_advanced(
        taxi_surge_calculator,
        load_json,
        admin_pipeline,
        mockserver,
        stages,
        expected_override,
        expected_activities,
):
    YT_LOGS.clear()
    JS_PIPELINE_ACTIVITIES.clear()

    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        request = request.json

        response = {'radius': 2785, 'generic': {}, 'reposition': {}}

        for category in request.get('allowed_classes', []):
            response['generic'][category] = {
                'free': 7,
                'on_order': 0,
                'free_chain': 0,
                'total': 0,
                'free_chain_groups': {'short': 0, 'medium': 0, 'long': 0},
            }

        request['__resource_name__'] = 'count_by_categories'
        RESOURCE_REQUESTS.append(request)
        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'}, json=response,
        )

    def get_stages():
        prev_stage = None
        for stage_info in stages:
            stage_name, stage_override = (
                (stage_info, {}) if isinstance(stage_info, str) else stage_info
            )
            stage = load_json(f'{stage_name}.json')
            stage = common.json_override(stage, stage_override)
            is_predicate_stage = 'args' in stage
            conditions = stage.setdefault('conditions', [])
            if prev_stage and not conditions and not is_predicate_stage:
                # check status conditions always do work
                conditions.append(
                    {
                        'stage_name': prev_stage,
                        'stage_statuses': ['passed'],
                        'type': 'stage_status',
                    },
                )
            yield stage
            if not is_predicate_stage:
                prev_stage = stage_name

    pipeline_id = str(uuid.uuid4())
    pipeline = {
        'id': pipeline_id,
        'name': 'default',
        'stages': list(get_stages()),
        'comment': 'comment 1',
        'created': '2019-12-16T23:38:47+03:00',
        'updated': '2019-12-16T23:38:47+03:00',
        'state': 'active',
        'version': 0,
    }
    admin_pipeline.set_pipelines_by_consumer(
        {'taxi-surge': {pipeline_id: pipeline}},
    )

    request = {
        'point_a': [37.583369, 55.778821],
        'classes': ['econom', 'business'],
    }
    expected = {
        'zone_id': 'MSK-Yandex HQ',
        'user_layer': 'default',
        'experiment_id': 'a29e6a811131450f9a28337906594207',
        'experiment_name': 'default',
        'experiment_layer': 'default',
        'is_cached': False,
        'classes': [
            {
                'name': 'econom',
                'value_raw': 1.5,
                'surge': {'value': 1.0},
                'calculation_meta': {'reason': 'no'},
            },
            {
                'name': 'business',
                'value_raw': 1.5,
                'surge': {'value': 1.0},
                'calculation_meta': {'reason': 'no'},
            },
        ],
        'experiments': [],
        'experiment_errors': [],
    }

    expected = common.json_override(expected, expected_override)

    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200, response.text
    actual = response.json()

    calculation_id = actual.pop('calculation_id', '')

    assert len(calculation_id) == 32

    common.sort_data(expected)
    common.sort_data(actual)

    assert expected == actual
    assert expected_activities == JS_PIPELINE_ACTIVITIES

    stage_yt_logs = common.get_stage_logs(YT_LOGS)[calculation_id]

    # expect that all logic stages will be in YT logs
    assert {
        stage['name']
        for stage in pipeline['stages']
        if 'out_bindings' in stage
    }.issubset(stage_yt_logs.keys())
