# pylint: disable=protected-access,unused-variable
import copy
import datetime

import pytest

from eslogadminpy3.lib import log_list
from test_eslogadminpy3 import constants


@pytest.mark.parametrize(
    'time_from,time_to,expected_lengths,expected',
    [
        (None, None, [1, 1, 1, 2, 2, 3, 3, 21, 21, 21, 21], None),
        (
            datetime.datetime(2019, 11, 14, 12, 0),
            datetime.datetime(2019, 11, 14, 12, 5),
            None,
            [
                ['yandex-taxi-archive'],
                ['yandex-taxi-*2019.11.14.12'],
                ['pilorama-core-*2019.11.14.12'],
            ],
        ),
        (
            datetime.datetime(2019, 11, 14, 11, 59),
            datetime.datetime(2019, 11, 14, 12, 0),
            None,
            [
                ['yandex-taxi-archive'],
                ['yandex-taxi-*2019.11.14.12'],
                ['pilorama-core-*2019.11.14.12'],
                ['yandex-taxi-*2019.11.14.11'],
                ['pilorama-core-*2019.11.14.11'],
            ],
        ),
    ],
)
@pytest.mark.now('2019-11-14T12:00:00.000Z')
def test_build_indices_set(
        web_context, time_from, time_to, expected_lengths, expected,
):
    log_list_context = log_list.LogListContext(
        context=web_context,
        typed_requests=[
            log_list.TypedRequest(
                'response',
                {
                    'query': {
                        'bool': {
                            'must': [
                                {'term': {'meta_type': 'response'}},
                                {'term': {'meta_code': 200}},
                            ],
                        },
                    },
                },
            ),
        ],
        limit=1,
        offset=0,
        time_from=time_from,
        time_to=time_to,
        from_archive=False,
        log_extra={},
    )
    indices_sets = log_list_context._build_indices_sets()
    if expected_lengths is not None:
        lengths = [len(indices_set) for indices_set in indices_sets]
        assert lengths == expected_lengths
    if expected:
        assert indices_sets == expected


@pytest.mark.config(
    LOGS_ELASTIC_LIST_REQUEST_SETTINGS={
        'distribution': [1, 2, 3, 21],
        'full_range': 48,
        'group_by_index': True,
    },
)
@pytest.mark.parametrize(
    'index_patterns, time_from, time_to, with_extra_filter, expected',
    [
        (
            [],
            datetime.datetime(2019, 11, 14, 12, 0),
            datetime.datetime(2019, 11, 14, 12, 5),
            True,
            [
                ['yandex-taxi-archive'],
                ['yandex-taxi-*2019.11.14.12'],
                ['pilorama-core-*2019.11.14.12'],
            ],
        ),
        (
            ['index-1'],
            datetime.datetime(2019, 11, 14, 12, 0),
            datetime.datetime(2019, 11, 14, 12, 5),
            True,
            [['yandex-taxi-archive'], ['index-1-2019.11.14.12']],
        ),
        (
            ['index-1', 'index-2'],
            datetime.datetime(2019, 11, 14, 12, 0),
            datetime.datetime(2019, 11, 14, 12, 5),
            True,
            [
                ['yandex-taxi-archive'],
                ['index-1-2019.11.14.12'],
                ['index-2-2019.11.14.12'],
            ],
        ),
        (
            ['index-1', 'index-2'],
            datetime.datetime(2019, 11, 14, 12, 0),
            datetime.datetime(2019, 11, 14, 14, 5),
            True,
            [
                ['yandex-taxi-archive'],
                ['index-1-2019.11.14.14'],
                ['index-2-2019.11.14.14'],
                ['index-1-2019.11.14.13', 'index-1-2019.11.14.12'],
                ['index-2-2019.11.14.13', 'index-2-2019.11.14.12'],
            ],
        ),
        (
            ['index-1', 'index-2'],
            datetime.datetime(2019, 11, 14, 12, 0),
            datetime.datetime(2019, 11, 14, 14, 5),
            False,
            [
                ['yandex-taxi-archive'],
                ['index-1-2019.11.14.14'],
                ['index-2-2019.11.14.14'],
            ],
        ),
    ],
)
@pytest.mark.now('2019-11-14T12:00:00.000Z')
def test_build_indices_set_with_patterns(
        web_context,
        index_patterns,
        time_from,
        time_to,
        with_extra_filter,
        expected,
):
    request_body = {
        'query': {'bool': {'must': [{'term': {'meta_type': 'response'}}]}},
    }
    if with_extra_filter:
        request_body['query']['bool']['must'].append(
            {'term': {'meta_code': 200}},
        )

    log_list_context = log_list.LogListContext(
        context=web_context,
        typed_requests=[log_list.TypedRequest('response', request_body)],
        limit=1,
        offset=0,
        time_from=time_from,
        time_to=time_to,
        from_archive=False,
        log_extra={},
        index_patterns=index_patterns,
    )
    indices_sets = log_list_context._build_indices_sets()
    assert indices_sets == expected


@pytest.mark.now('2019-11-14T12:00:00.000Z')
async def test_log_list(patch, web_app_client):
    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def search(**kwargs):
        index = kwargs['index'].split(',')[0]
        if 'size' in kwargs:
            example_hit = constants.ES_RESPONSE_EXAMPLE_REQUESTS['hits'][
                'hits'
            ][0]
            hits = []
            for _ in range(2):
                hit = copy.deepcopy(example_hit)
                hit['_index'] = index  # first index from request
                hits.append(hit)
            result = copy.deepcopy(constants.ES_RESPONSE_EXAMPLE_REQUESTS)
            result['hits']['hits'] = hits
            return result
        assert index in {
            'yandex-taxi-*2019.11.14.12',
            'yandex-taxi-*2019.11.14.11',
            'yandex-taxi-*2019.11.14.09',
        }
        return copy.deepcopy(constants.ES_RESPONSE_EXAMPLE_RESPONSES)

    await web_app_client.post(
        '/v2/logs/list/',
        params={'limit': 5},
        json={'filters': [{'name': 'http_code', 'value': '200'}]},
    )
    # TODO: ensure that not checking response is OK
    assert len(search.calls) == 14  # 1 archive, 5 first and 3 second
