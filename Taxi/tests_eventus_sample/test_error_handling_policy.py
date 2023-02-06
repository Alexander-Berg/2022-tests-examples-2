import copy
import json

import pytest

_OEP_PIPELINES = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'lbkx_test_events'},
        'root': {
            'output': {'sink_name': 'bulk-sink'},
            'operations': [
                {
                    'name': 'test-error-policy',
                    'operation_variant': {
                        'arguments': {'to': 'test_field'},
                        'operation_name': 'timestamp',
                        'type': 'mapper',
                    },
                },
            ],
        },
        'name': 'lbkx_test_events',
    },
]


@pytest.mark.config(
    EVENTUS_PIPELINE_DEFAULT_RETRY_POLICY={
        'max_attempts': 2,
        'min_delay_ms': 101,
        'max_delay_ms': 180001,
        'delay_factor': 3,
    },
)
@pytest.mark.parametrize(
    'action_after_error, retry_policy_fields',
    [
        ('', {'attempts': 10}),
        ('', {}),
        ('reject', {}),
        ('propagate', {}),
        ('reject', {'attempts': 5, 'min_delay_ms': 10}),
        ('reject', {'attempts': 5, 'max_delay_ms': 10}),
        ('reject', {'attempts': 5, 'delay_factor': 10}),
        (
            'reject',
            {
                'attempts': 5,
                'min_delay_ms': 66,
                'max_delay_ms': 66,
                'delay_factor': 66,
            },
        ),
        (
            'propagate',
            {
                'attempts': 5,
                'min_delay_ms': 66,
                'max_delay_ms': 66,
                'delay_factor': 66,
            },
        ),
    ],
)
async def test_set_error_policy_from_taxi_config(
        taxi_eventus_sample,
        taxi_config,
        testpoint,
        mockserver,
        taxi_eventus_orchestrator_mock,
        action_after_error,
        retry_policy_fields,
):
    @testpoint('error_handler::try_execute')
    def get_retry_policy(data):
        pass

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    pipelines_to_set = copy.deepcopy(_OEP_PIPELINES)

    error_handling_policy = {}
    # default from service
    error_handling_policy_expected = {
        'action_after_erroneous_execution': 'propagate',
        'retry_policy': {
            'attempts': 2,
            'min_delay_ms': 101,
            'max_delay_ms': 180001,
            'delay_factor': 3,
        },
    }

    if action_after_error:
        error_handling_policy[
            'action_after_erroneous_execution'
        ] = action_after_error
        error_handling_policy_expected[
            'action_after_erroneous_execution'
        ] = action_after_error

    for r_field, r_value in retry_policy_fields.items():
        if 'retry_policy' not in error_handling_policy:
            error_handling_policy['retry_policy'] = {}
            # TODO: EFFICIENCYDEV-20027
            # default from v1_pipelines_config_schema.fbs
            error_handling_policy_expected['retry_policy'] = {
                'attempts': 1,
                'min_delay_ms': 0,
                'max_delay_ms': 2000000000,
                'delay_factor': 1,
            }

        error_handling_policy['retry_policy'][r_field] = r_value
        error_handling_policy_expected['retry_policy'][r_field] = r_value

    if error_handling_policy:
        pipelines_to_set[0]['root']['operations'][0][
            'error_handling_policy'
        ] = error_handling_policy

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_eventus_sample, pipelines_to_set,
    )

    response = await taxi_eventus_sample.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'lbkx_test_events',
                'data': '{"test":"test"}',
                'topic': 'smth',
                'cookie': 'cookie_test_error_policy',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_test_error_policy'

    policy_val = (await get_retry_policy.wait_call())['data']

    error_handling_policy_expected.update(
        {
            'node_name': '[0]test-error-policy',
            'erroneous_statistics_level': 'error',
        },
    )
    assert policy_val == error_handling_policy_expected
