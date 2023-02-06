import json

import pytest

from tests_eventus_sample import pipeline_tools

_OEP_PIPELINES = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'lbkx_test_events'},
        'root': {
            'output': {'sink_name': 'bulk-sink'},
            'operations': [
                {
                    'name': 'topic-filter',
                    'operation_variant': {
                        'arguments': {'src': 'topic', 'match_with': 'smth'},
                        'operation_name': 'string_equal',
                        'type': 'filter',
                    },
                },
                {
                    'name': 'add-seq-num',
                    'operation_variant': {
                        'arguments': {},
                        'operation_name': 'set_seq_num',
                        'type': 'mapper',
                    },
                },
            ],
        },
        'name': 'lbkx_test_events',
    },
]

_OEP_INVALID_PIPELINES_1 = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'lbkx_test_events'},
        'root': {
            'output': {'sink_name': 'bulk-sink'},
            'operations': [
                {
                    'name': 'topic-filter',
                    'operation_variant': {
                        'arguments': {'src': 'topic', 'match_with': 'smth'},
                        'operation_name': 'string_equal',
                        'type': 'filter',
                    },
                },
                {
                    'name': 'add-seq-num',
                    'operation_variant': {
                        'arguments': {},
                        'operation_name': 'bad-operation-name',
                        'type': 'mapper',
                    },
                },
            ],
        },
        'name': 'lbkx_test_events',
    },
]

_OEP_INVALID_PIPELINES_2 = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'lbkx_test_events'},
        'root': {
            'output': {'sink_name': 'bulk-sink'},
            'operations': [
                {
                    'name': 'topic-filter',
                    'operation_variant': {
                        'arguments': {'src': 'topic', 'match_with': 'smth'},
                        'operation_name': 'string_equal',
                        'type': 'filter',
                    },
                },
                {
                    'name': 'add-seq-num',
                    'operation_variant': {
                        'arguments': {'bad-key': 'none'},
                        'operation_name': 'set_key_flat',
                        'type': 'mapper',
                    },
                },
            ],
        },
        'name': 'lbkx_test_events',
    },
]

_OEP_INVALID_PIPELINES_SOURCE = [
    {
        'description': '',
        'st_ticket': '',
        'is_disabled': True,
        'source': {'name': 'bad-source-name'},
        'root': {'sink_name': 'bulk-sink'},
        'name': 'lbkx_test_events',
    },
]

_OEP_INVALID_PIPELINES_DISABLED = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'lbkx_test_events'},
        'root': {
            'output': {'sink_name': 'bulk-sink'},
            'operations': [
                {
                    'name': 'topic-filter',
                    'operation_variant': {
                        'arguments': {'src': 'topic', 'match_with': 'smth'},
                        'operation_name': 'string_equal',
                        'type': 'filter',
                    },
                },
            ],
        },
        'name': 'lbkx_test_events',
    },
    {
        'description': '',
        'st_ticket': '',
        'is_disabled': True,
        'source': {'name': 'bad-source-name'},
        'root': {'sink_name': 'bulk-sink'},
        'name': 'bad-source-in-ppl',
    },
]

_OEP_INVALID_PIPELINES_SINK = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'lbkx_test_events'},
        'root': {
            'output': {'sink_name': 'bad-sink-name'},
            'operations': [
                {
                    'name': 'topic-filter',
                    'operation_variant': {
                        'arguments': {'src': 'topic', 'match_with': 'smth'},
                        'operation_name': 'string_equal',
                        'type': 'filter',
                    },
                },
            ],
        },
        'name': 'lbkx_test_events',
    },
]


@pytest.mark.parametrize(
    'should_fail_reconfigure, invalid_pipeline_configs',
    [
        pytest.param(
            True, _OEP_INVALID_PIPELINES_1, id='invalid-operation_name',
        ),
        pytest.param(
            True, _OEP_INVALID_PIPELINES_2, id='invalid-operation-argument',
        ),
        pytest.param(
            False, _OEP_INVALID_PIPELINES_DISABLED, id='invalid-source',
        ),
        pytest.param(True, _OEP_INVALID_PIPELINES_SINK, id='invalid-sink'),
    ],
)
async def test_invalid_pipeline(
        taxi_eventus_sample,
        taxi_config,
        testpoint,
        taxi_eventus_orchestrator_mock,
        should_fail_reconfigure,
        invalid_pipeline_configs,
        metrics_snapshot,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    async def reconfigure(pipeline_configs):
        await taxi_eventus_orchestrator_mock.set_pipelines_config(
            testpoint,
            taxi_eventus_sample,
            pipeline_configs,
            testpoint_timeout=3.0,
        )

    await reconfigure(_OEP_PIPELINES)
    await taxi_eventus_sample.run_task('invalidate-seq_num')

    response = await taxi_eventus_sample.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'lbkx_test_events',
                'data': json.dumps(pipeline_tools.create_event(1)),
                'topic': 'smth',
                'cookie': 'cookie_for_bulk-sink_',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_for_bulk-sink_'

    await metrics_snapshot.take_snapshot()
    if should_fail_reconfigure:
        bad_pipeline_config_accepted = False
        try:
            await reconfigure(invalid_pipeline_configs)
            bad_pipeline_config_accepted = True
        except Exception as exc:  # pylint: disable=broad-except
            print('Caught expected exception: ', exc)
        assert not bad_pipeline_config_accepted
    else:
        await reconfigure(invalid_pipeline_configs)

    metrics = await metrics_snapshot.get_metrics_diff()
    if should_fail_reconfigure:
        assert (
            metrics['pipeline-statistics']['lbkx_test_events'][
                'initial_errors'
            ].get_diff()
            > 0
        )

    await taxi_eventus_sample.run_task('invalidate-seq_num')

    response = await taxi_eventus_sample.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'lbkx_test_events',
                'data': json.dumps(pipeline_tools.create_event(1)),
                'topic': 'smth',
                'cookie': 'cookie_for_bulk-sink_',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_for_bulk-sink_'
