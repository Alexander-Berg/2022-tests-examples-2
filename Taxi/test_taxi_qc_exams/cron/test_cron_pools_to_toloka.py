from aiohttp import web
import pytest

from taxi_qc_exams.generated.cron import run_cron
from test_taxi_qc_exams import utils


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(pools_to_toloka=utils.job_settings()),
    QC_JOB_POOLS_TO_TOLOKA={'qc_pool': 'toloka_project'},
    QC_TOLOKA_PROJECTS_URL_FORMAT={
        '__default__': {'urls': 'external', 'avatar': True},
    },
)
@pytest.mark.now('2020-01-01T16:30:00Z')
async def test_pools_to_toloka(mock_qc_pools, mock_toloka, mock_media_storage):
    @mock_toloka('/api/v1/pools')
    async def _get_pools(request):
        assert request.headers['Authorization'] == 'OAuth token'
        return {
            'items': [
                {
                    'id': 'pool_id',
                    'status': 'OPEN',
                    'created': '2020-01-01T16:30:00Z',
                },
            ],
            'has_more': False,
        }

    @mock_qc_pools('/internal/qc-pools/v1/pool/retrieve')
    async def _internal_qc_pools_v1_pool_retrieve_post(request):
        return {
            'items': [
                {
                    'id': 'qc_id',
                    'exam': 'exam',
                    'entity_id': 'entity_id',
                    'entity_type': 'entity_type',
                    'created': '2020-01-01T16:30:00Z',
                    'date': [
                        {
                            'field': 'array_field',
                            'value': ['value_1', 'value_2'],
                        },
                        {'field': 'array_field_empty', 'value': []},
                    ],
                    'media': [
                        {
                            'code': 'biometry_etalons.selfie.0',
                            'url': (
                                'http://s3.mds.yandex.net/quality-control/'
                                'ph1?Signature=s1'
                            ),
                        },
                        {
                            'code': 'selfie',
                            'url': (
                                'https://s3.mds.yandex.net/'
                                'media-storage-public/ph2?Signature=s2'
                            ),
                            'bucket': 'driver-photo',
                            'id': '4a77ed606922456c88929abc10fbebf5',
                        },
                    ],
                },
            ],
            'cursor': 'next',
        }

    @mock_media_storage('/service/driver-photo/v1/avatars')
    async def _service_type_v1_avatars(request):
        return web.json_response(
            {
                'imagename': 'imagename',
                'avatar_id': 123,
                'version': '1',
                'expired_at': '2021-12-12',
            },
        )

    @mock_toloka('/api/v1/tasks')
    async def _create_task(request):
        assert request.json == [
            {
                'pool_id': 'pool_id',
                'input_values': {
                    'id': 'qc_id',
                    'entity_id': 'entity_id',
                    'entity_type': 'entity_type',
                    'exam': 'exam',
                    'created': '2020-01-01T19:30:00+03:00',
                    'media': [
                        {
                            'code': 'biometry_etalons.selfie.0',
                            'url': (
                                'https://quality-control.s3-private.'
                                'mds.yandex.net/ph1?Signature=s1'
                            ),
                        },
                        {
                            'code': 'selfie',
                            'url': (
                                'https://media-storage-public.s3-private.'
                                'mds.yandex.net/ph2?Signature=s2'
                            ),
                            'bucket': 'driver-photo',
                            'id': '4a77ed606922456c88929abc10fbebf5',
                            'avatar_name': 'imagename',
                            'avatar_id': 123,
                        },
                    ],
                },
            },
        ]
        return web.json_response(
            {
                'items': {
                    '0': {
                        'id': 'toloka_id',
                        'pool_id': 'pool_id',
                        'input_values': {},
                        'overlap': 1,
                        'created': '2020-01-01T19:30:00+03:00',
                    },
                },
                'validation_errors': {},
            },
            status=201,
        )

    @mock_qc_pools('/internal/qc-pools/v1/pool/push')
    async def _internal_qc_pools_v1_pool_push_post(request):
        assert request.json == {
            'items': [
                {
                    'id': 'qc_id',
                    'entity_id': 'entity_id',
                    'entity_type': 'entity_type',
                    'exam': 'exam',
                    'created': '2020-01-01T19:30:00+03:00',
                    'data': [
                        {'field': 'task_id', 'value': 'toloka_id'},
                        {'field': 'pool_id', 'value': 'pool_id'},
                        {
                            'field': 'toloka_project_id',
                            'value': 'toloka_project',
                        },
                    ],
                },
            ],
        }
        return {'failed': []}

    await run_cron.main(['taxi_qc_exams.crontasks.pools.to_toloka', '-t', '0'])

    assert _get_pools.times_called == 1
    assert _internal_qc_pools_v1_pool_retrieve_post.times_called == 1
    assert _create_task.times_called == 1
    assert _internal_qc_pools_v1_pool_push_post.times_called == 1
