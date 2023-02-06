import pytest

from taxi_qc_exams.generated.cron import run_cron
from test_taxi_qc_exams import utils


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(pools_from_toloka=utils.job_settings()),
    QC_JOB_POOLS_FROM_TOLOKA=['qc_pool_result'],
    QC_JOB_POOLS_FROM_TOLOKA_LIMITS=dict(concurrency=1, sleep_ms=1000),
)
@pytest.mark.now('2020-01-01T16:30:00Z')
async def test_pools_from_toloka(mock_qc_pools, mock_toloka):
    @mock_qc_pools('/internal/qc-pools/v1/pool/retrieve')
    async def _internal_qc_pools_v1_pool_retrieve_post(request):
        return {
            'items': [
                {
                    'id': 'id',
                    'exam': 'exam',
                    'entity_id': 'entity_id',
                    'pool_id': 'pool_id',
                    'entity_type': 'entity_type',
                    'created': '2020-01-01T16:30:00Z',
                    'data': [
                        {'field': 'task.task_id', 'value': 'task_id'},
                        {'field': 'task.pool_id', 'value': 'pool_id'},
                    ],
                },
                {
                    'id': 'id2',
                    'exam': 'exam',
                    'entity_id': 'entity_id',
                    'pool_id': 'pool_id',
                    'entity_type': 'entity_type',
                    'created': '2020-01-01T16:30:00Z',
                    'data': [
                        {'field': 'task.task_id', 'value': 'task_id2'},
                        {'field': 'task.pool_id', 'value': 'pool_id'},
                    ],
                },
                {
                    'id': 'id3',
                    'exam': 'exam',
                    'entity_id': 'entity_id',
                    'pool_id': 'pool_id',
                    'entity_type': 'entity_type',
                    'created': '2020-01-01T16:30:00Z',
                    'data': [
                        {'field': 'task.task_id', 'value': 'task_id3'},
                        {'field': 'task.pool_id', 'value': 'pool_id'},
                    ],
                    'date': [
                        {
                            'field': 'array_field',
                            'value': ['value_1', 'value_2'],
                        },
                        {'field': 'array_field_empty', 'value': []},
                    ],
                },
            ],
            'cursor': 'next',
        }

    @mock_toloka('/api/v1/assignments')
    async def _get_assignments(request):
        return {
            'items': [
                {
                    'id': request.query.get('task_id', 'task_id'),
                    'pool_id': request.query.get('pool_id', 'toloka_pool'),
                    'task_suite_id': request.query.get(
                        'task_suite_id', 'task_suite_id',
                    ),
                    'user_id': 'user_id_1',
                    'status': request.query.get('status', 'ACCEPTED'),
                    'tasks': [],
                    'solutions': [
                        {'output_values': {'valid': True, 'same_name': False}},
                    ],
                    'accepted': '2020-01-01T16:30:00Z',
                },
            ],
            'has_more': False,
        }

    @mock_qc_pools('/internal/qc-pools/v1/pool/push')
    async def _internal_qc_pools_v1_pool_push_post(request):
        assert request.json == {
            'items': [
                {
                    'id': 'id',
                    'entity_id': 'entity_id',
                    'entity_type': 'entity_type',
                    'exam': 'exam',
                    'created': '2020-01-01T19:30:00+03:00',
                    'data': [
                        {'field': 'valid', 'value': True},
                        {'field': 'same_name', 'value': False},
                        {'field': 'yang_user_ids', 'value': ['user_id_1']},
                    ],
                },
                {
                    'id': 'id2',
                    'entity_id': 'entity_id',
                    'entity_type': 'entity_type',
                    'exam': 'exam',
                    'created': '2020-01-01T19:30:00+03:00',
                    'data': [
                        {'field': 'valid', 'value': True},
                        {'field': 'same_name', 'value': False},
                        {'field': 'yang_user_ids', 'value': ['user_id_1']},
                    ],
                },
                {
                    'id': 'id3',
                    'entity_id': 'entity_id',
                    'entity_type': 'entity_type',
                    'exam': 'exam',
                    'created': '2020-01-01T19:30:00+03:00',
                    'data': [
                        {'field': 'valid', 'value': True},
                        {'field': 'same_name', 'value': False},
                        {'field': 'yang_user_ids', 'value': ['user_id_1']},
                    ],
                },
            ],
        }
        return {'failed': []}

    await run_cron.main(
        ['taxi_qc_exams.crontasks.pools.from_toloka', '-t', '0'],
    )

    assert _get_assignments.times_called == 3
    assert _internal_qc_pools_v1_pool_retrieve_post.times_called == 1
    assert _internal_qc_pools_v1_pool_push_post.times_called == 1
