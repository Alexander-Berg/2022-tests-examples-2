import pytest

from eslogadminpy3.crontasks import update_log_types
from eslogadminpy3.generated.cron import run_cron


@pytest.mark.now('2019-11-20T16:50:00Z')
async def test_task(patch, mongo):
    @patch('elasticsearch.client.Elasticsearch.search')
    async def _search(*args, **kwargs):
        assert kwargs['index'] in {
            'yandex-taxi-2019.11.20.15',
            'pilorama-core-2019.11.20.15',
        }

        return {
            'aggregations': {
                'types': {
                    'types': {
                        'buckets': [{'key': 'routestats'}, {'key': 'ping'}],
                        'sum_other_doc_count': 0,
                    },
                },
            },
        }

    @patch('elasticsearch.client.indices.IndicesClient.get_settings')
    async def _get_settings(*args, **kwargs):
        assert kwargs['index'] in {
            'yandex-taxi-*2019.11.20.15,pilorama-core-*2019.11.20.15',
            'yandex-taxi-*2019.11.20.16,pilorama-core-*2019.11.20.16',
        }
        return {
            'yandex-taxi-2019.11.20.15': {},
            'pilorama-core-2019.11.20.15': {},
        }

    await run_cron.main(
        ['eslogadminpy3.crontasks.update_log_types', '-t', '0', '-d'],
    )
    log_types = await mongo.log_types.find().to_list(None)
    assert {x['name'] for x in log_types} == {'ping', 'routestats'}


@pytest.mark.parametrize(
    'request_params,expected_filter',
    [
        pytest.param(
            update_log_types.SEARCH_TYPES['http'],
            {'term': {'type': 'response'}},
            marks=pytest.mark.config(LOGS_TYPES_EXCLUDES={'patterns': []}),
        ),
        pytest.param(
            update_log_types.SEARCH_TYPES['http'],
            {
                'bool': {
                    'must': {'term': {'type': 'response'}},
                    'must_not': [
                        {
                            'wildcard': {
                                'meta_type': {
                                    'value': '*/driver/cctv-map/v1/zones/*',
                                },
                            },
                        },
                    ],
                },
            },
            marks=pytest.mark.config(
                LOGS_TYPES_EXCLUDES={
                    'patterns': ['/driver/cctv-map/v1/zones/'],
                },
            ),
        ),
        pytest.param(
            update_log_types.SEARCH_TYPES['stq'],
            {'term': {'type': 'stq_task_finish'}},
            marks=pytest.mark.config(LOGS_TYPES_EXCLUDES={'patterns': []}),
        ),
        pytest.param(
            update_log_types.SEARCH_TYPES['stq'],
            {
                'bool': {
                    'must': {'term': {'type': 'stq_task_finish'}},
                    'must_not': [
                        {
                            'wildcard': {
                                'queue': {
                                    'value': '*/driver/cctv-map/v1/zones/*',
                                },
                            },
                        },
                    ],
                },
            },
            marks=pytest.mark.config(
                LOGS_TYPES_EXCLUDES={
                    'patterns': ['/driver/cctv-map/v1/zones/'],
                },
            ),
        ),
    ],
)
def test_request_build(loop, cron_context, request_params, expected_filter):
    task = update_log_types.Task(
        loop=loop,
        context=cron_context,
        request_params=request_params,
        log_extra=None,
    )
    assert task.request['aggs']['types']['filter'] == expected_filter
