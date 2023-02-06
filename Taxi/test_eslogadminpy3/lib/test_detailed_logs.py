# pylint: disable=protected-access,unused-variable
import copy
import datetime

import pytest

from eslogadminpy3.lib import detailed_logs
from eslogadminpy3.lib import enrich_request
from eslogadminpy3.lib import log_list
from test_eslogadminpy3 import constants


@pytest.mark.now('2019-01-01T10:00:00.0Z')
@pytest.mark.parametrize(
    'start, end, index_pattern, expected',
    [
        (None, None, None, 'yandex-taxi-*'),
        (None, None, 'yandex-taxi-api', 'yandex-taxi-api*'),
        (None, None, 'yandex-taxi-api*', 'yandex-taxi-api*'),
        (None, None, 'yandex-taxi-api-*', 'yandex-taxi-api-*'),
        (
            datetime.datetime(2019, 1, 1, 0),
            datetime.datetime(2019, 1, 1, 1),
            'yandex-taxi-*',
            'yandex-taxi-*2019.01.01.00,yandex-taxi-*2019.01.01.01',
        ),
        (
            datetime.datetime(2019, 1, 1, 0),
            datetime.datetime(2019, 1, 1, 1),
            'yandex-taxi-api-',
            'yandex-taxi-api-2019.01.01.00,yandex-taxi-api-2019.01.01.01',
        ),
        (
            datetime.datetime(2019, 1, 1, 0),
            datetime.datetime(2019, 1, 1, 1),
            None,
            'yandex-taxi-*2019.01.01.00,yandex-taxi-*2019.01.01.01',
        ),
        (
            datetime.datetime(2019, 1, 1, 1),
            None,
            'yandex-taxi-*',
            'yandex-taxi-*',
        ),
        (
            datetime.datetime(2019, 1, 1, 7),
            None,
            'yandex-taxi-*',
            'yandex-taxi-*2019.01.01.07,yandex-taxi-*2019.01.01.08,'
            'yandex-taxi-*2019.01.01.09,yandex-taxi-*2019.01.01.10',
        ),
        (
            datetime.datetime(2019, 1, 1, 6),
            None,
            'yandex-taxi-*',
            'yandex-taxi-*',
        ),
        (
            None,
            datetime.datetime(2019, 1, 1, 9),
            'yandex-taxi-*',
            'yandex-taxi-*',
        ),
        (
            None,
            datetime.datetime(2018, 12, 1),
            'yandex-taxi-*',
            'yandex-taxi-*',
        ),
        (
            None,
            datetime.datetime(2018, 12, 30, 12),
            'yandex-taxi-*',
            'yandex-taxi-*2018.12.30.10,yandex-taxi-*2018.12.30.11,'
            'yandex-taxi-*2018.12.30.12',
        ),
    ],
)
def test_make_es_index_from_time_range(start, end, index_pattern, expected):
    assert expected == detailed_logs.make_es_index_from_time_range(
        [index_pattern], start, end,
    )


@pytest.mark.parametrize(
    'expected_request_performer,expected_request_performer_path',
    [
        pytest.param(
            enrich_request._parallel_with_single_terms,
            'eslogadminpy3.lib.enrich_request._parallel_with_single_terms',
            marks=pytest.mark.config(
                LOGS_ENRICH_REQUEST_IMPROVEMENT={
                    'enable': True,
                    'concurency': 2,
                    'fail_retries': 0,
                    'retries_delay': 0.0,
                    'request_in_single_terms': True,
                },
            ),
        ),
        pytest.param(
            enrich_request._parallel_with_multi_terms,
            'eslogadminpy3.lib.enrich_request._parallel_with_multi_terms',
            marks=pytest.mark.config(
                LOGS_ENRICH_REQUEST_IMPROVEMENT={
                    'enable': True,
                    'concurency': 2,
                    'fail_retries': 0,
                    'retries_delay': 0.0,
                },
            ),
        ),
        pytest.param(
            enrich_request._simple_request,
            'eslogadminpy3.lib.enrich_request._simple_request',
            marks=pytest.mark.config(
                LOGS_ENRICH_REQUEST_IMPROVEMENT={
                    'enable': False,
                    'concurency': 2,
                    'fail_retries': 0,
                    'retries_delay': 0.0,
                },
            ),
        ),
    ],
)
async def test_parallel_enrich(
        patch,
        web_context,
        expected_request_performer,
        expected_request_performer_path,
):
    first_request_done = False

    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def search(*args, **kwargs):
        if 'archive' in kwargs['index']:
            return {'hits': {'hits': []}}
        nonlocal first_request_done
        if not first_request_done:
            first_request_done = True
            return copy.deepcopy(constants.ES_RESPONSE_EXAMPLE_REQUESTS)

        return copy.deepcopy(constants.ES_RESPONSE_EXAMPLE_RESPONSES)

    @patch(expected_request_performer_path)
    async def _mock(*args, **kwargs):
        return await expected_request_performer(*args, **kwargs)

    await log_list.get_log_records(
        context=web_context,
        typed_requests=[
            log_list.TypedRequest(
                'response',
                {
                    'query': {
                        'bool': {
                            'must': [{'term': {'meta_type': 'response'}}],
                        },
                    },
                },
            ),
        ],
        limit=None,
        offset=10,
        time_from=None,
        time_to=None,
        from_archive=False,
        log_extra=None,
        index_patterns=None,
    )
    assert _mock.calls
