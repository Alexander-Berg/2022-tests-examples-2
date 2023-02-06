# pylint: disable=redefined-outer-name
import asyncio
import datetime
import typing
import urllib.parse

import pytest

import client_product_automatization.crontasks.missing_translation_lib as mtl
from client_product_automatization.generated.cron import run_cron


YT_PATH = '//home/tests/missing_translation'
EXPECTED_ROW = {
    'project': 'taxi',
    'service': 'some-service',
    'keyset': 'some_keyset',
    'key': 'some.key',
    'locale': 'en',
    'count': 1,
}
KIBANA_URL_TEMPLATE_WITH_TRACE_ID = (
    'https://kibana/app?{trace_id}&{dt_from}&{dt_to}'
)
KIBANA_URL_TEMPLATE_WITH_TEXT = 'https://kibana/app?{text}'
DEFAULT_TEXT = (
    'Missing translation[some_keyset][some.key][en][1]: '
    'fallback to "ru" locale'
)


@pytest.fixture
def mock_elastic(patch):
    @patch(
        (
            'client_product_automatization.crontasks.missing_translation_lib.'
            'ElasticClient'
        ),
    )
    def _elastic_client(*args, **kwargs):
        class ElasticClient:
            async def close(self):
                pass

            async def select_logs(
                    self, log_type: mtl.LogType,
            ) -> typing.List[dict]:
                rows = [
                    {
                        '_source': {
                            'ngroups': 'taxi_some-service_stable',
                            'trace_id': 'some_trace_id',
                            'text': DEFAULT_TEXT,
                        },
                    },
                ]
                return rows

        return ElasticClient()

    return _elastic_client


@pytest.mark.config(
    MISSING_TRANSLATION_SETTINGS={
        'enabled': True,
        'elastic': {},
        'yt': {'cluster': 'hahn', 'path': YT_PATH},
        'startrack': {
            'default_assignee': 'someone',
            'default_assignee_map': [
                {'service': 'some-service2', 'assignee': 'someone2'},
            ],
            'force_default_assignee': False,
            'rows_limit': 50,
            'services_limit': 10,
            'queue': 'TESTKEY',
            'ticket_type': 'bug',
            'tags': ['translation_error'],
            'kibana_url_template_with_trace_id': (
                KIBANA_URL_TEMPLATE_WITH_TRACE_ID
            ),
            'kibana_url_template_with_text': KIBANA_URL_TEMPLATE_WITH_TEXT,
            'tanker_host': 'http://tanker.ru',
            'enabled': True,
            'select_query': (
                'Queue: TAXIDUTY AND '
                'Tags: "missing_translation" AND Status: open'
            ),
        },
    },
    LOCALIZATIONS_KEYSETS={
        'keysets': {
            'some_keyset': {
                'tanker_project_id': 'taxi',
                'tanker_keyset_id': 'backend.some_keyset',
            },
        },
    },
)
@pytest.mark.now(datetime.datetime(2021, 9, 28, 11, 0, 0).isoformat())
async def test_missing_translation(
        patch, mock_elastic, yt_client, mock_clownductor,
):
    @mock_clownductor('/v1/services/search/')
    def _services_search_handler(request):
        return {
            'projects': [
                {
                    'project_id': 1,
                    'project_name': 'some-project',
                    'services': [
                        {
                            'id': 42,
                            'project_id': 1,
                            'cluster_type': 'nanny',
                            'name': 'some-service',
                        },
                    ],
                },
            ],
        }

    @mock_clownductor('/v1/services/')
    def _services_handler(request):
        return [
            {
                'id': 42,
                'project_id': 1,
                'cluster_type': 'nanny',
                'name': 'some-service',
                'maintainers': ['artemshmelev'],
            },
        ]

    @patch('taxi.clients.startrack.StartrackAPIClient.search')
    async def _startrek_search(*args, **kwargs):
        return []

    @patch('taxi.clients.startrack.StartrackAPIClient._request')
    async def _startrek_client(*args, **kwargs):
        json = kwargs['json']
        assert json['summary'] == '[some-service] ошибки с переводами'
        assert json['queue'] == {'key': 'TESTKEY'}
        assert json['type'] == {'key': 'bug'}
        assert json['employees'] == ['artemshmelev']
        assert json['tags'] == [
            'translation_error',
            'ngroups=taxi_some-service_stable',
        ]

        expected_kibana_url1 = KIBANA_URL_TEMPLATE_WITH_TRACE_ID.format(
            trace_id='some_trace_id',
            dt_from='2021-09-28T08:00:00Z',
            dt_to='2021-09-28T10:00:00Z',
        )
        expected_kibana_url2 = KIBANA_URL_TEMPLATE_WITH_TEXT.format(
            text=urllib.parse.quote(DEFAULT_TEXT).replace('%22', '%5C%22'),
        )
        expected_description = (
            '#|\n||**кейсет**|**ключ**|**локаль**|'
            '**пример лога**|**ссылка на перевод**|**число ошибок**||\n'
            '||some_keyset|some.key|en|'
            f'[kibana1]({expected_kibana_url1} )\n'
            f'[kibana2]({expected_kibana_url2} )|'
            '((http://tanker.ru/project/taxi/keyset'
            '/backend.some_keyset/key/some.key tanker))|1||\n|#'
        )
        assert expected_description in json['description']

        return {'key': 'TESTKEY-1'}

    await run_cron.main(
        [
            'client_product_automatization.crontasks.missing_translation',
            '-t',
            '0',
        ],
    )

    assert len(mock_elastic.calls) == 1
    assert _services_search_handler.times_called == 1
    assert _services_handler.times_called == 1
    assert len(_startrek_client.calls) == 1
    assert len(_startrek_search.calls) == 1
    assert next(yt_client.read_table(YT_PATH)) == EXPECTED_ROW


@pytest.mark.config(
    MISSING_TRANSLATION_SETTINGS={
        'enabled': True,
        'elastic': {},
        'yt': {'cluster': 'hahn', 'path': YT_PATH},
        'startrack': {'enabled': False},
    },
)
async def test_startrack_disabled(patch, mock_elastic, yt_client):
    await run_cron.main(
        [
            'client_product_automatization.crontasks.missing_translation',
            '-t',
            '0',
        ],
    )

    assert len(mock_elastic.calls) == 1
    assert next(yt_client.read_table(YT_PATH)) == EXPECTED_ROW


@pytest.mark.config(
    MISSING_TRANSLATION_SETTINGS={
        'enabled': False,
        'elastic': {},
        'yt': {},
        'startrack': {},
    },
)
async def test_disabled():
    await run_cron.main(
        [
            'client_product_automatization.crontasks.missing_translation',
            '-t',
            '0',
        ],
    )


@pytest.mark.parametrize(
    ['text', 'log_type', 'expected'],
    [
        pytest.param(None, mtl.LogType.CPP, None, id='text=None'),
        pytest.param(
            (
                '\'fields.cheque_id, ru\' not found in translations, '
                'name:chatterbox'
            ),
            mtl.LogType.PYT,
            ('chatterbox', 'fields.cheque_id', 'ru'),
            id='ok python',
        ),
        pytest.param(
            (
                '\'fields.cheque_id, \' not found in translations, '
                'name:chatterbox'
            ),
            mtl.LogType.PYT,
            ('chatterbox', 'fields.cheque_id', 'null'),
            id='empty locale python',
        ),
        pytest.param(
            (
                '\'fields.cheque_id, ru\' not found in translations, '
                'name:chatterbox'
            ),
            mtl.LogType.CPP,
            None,
            id='mismatched text',
        ),
        pytest.param(
            (
                'Missing translation[client_messages][errors.key][ro][1]: '
                'fallback to "en" locale'
            ),
            mtl.LogType.CPP,
            ('client_messages', 'errors.key', 'ro'),
            id='ok cpp',
        ),
        pytest.param(
            (
                'Missing translation[client_messages][errors.key][][1]: '
                'fallback to "en" locale'
            ),
            mtl.LogType.CPP,
            ('client_messages', 'errors.key', 'null'),
            id='empty locale cpp',
        ),
    ],
)
async def test_parse_text(text, log_type, expected):
    res = mtl.LogParser.parse_text(text, log_type)
    if expected is None:
        assert res is None
    else:
        assert res == expected


@pytest.mark.parametrize(
    ['ngroups', 'cgroups', 'expected'],
    [
        pytest.param(
            None,
            None,
            ('null', 'null', 'null'),
            id='ngroups=None, cgroups=None',
        ),
        pytest.param('taxiservice', None, None, id='invalid ngroups'),
        pytest.param(
            'taxi_ivr-api_pre_stable',
            None,
            ('taxi', 'ivr-api', 'ngroups=taxi_ivr-api_pre_stable'),
            id='ok ngroups',
        ),
        pytest.param(
            'eda_ivr-api_pre_stable',
            ['eda_service'],
            ('eda', 'ivr-api', 'ngroups=eda_ivr-api_pre_stable'),
            id='got ngroups and cgroups',
        ),
        pytest.param(
            None,
            ['taxi_prestable_service', 'taxi_service'],
            ('taxi', 'service', 'cgroups=taxi_service'),
            id='ok cgroups',
        ),
    ],
)
async def test_parse_service_name(ngroups, cgroups, expected):
    try:
        res = mtl.LogParser.parse_service_name(ngroups, cgroups)
        assert res == expected
    except ValueError:
        assert expected is None


@pytest.mark.parametrize(
    ['log_type', 'expected'],
    [
        pytest.param(
            mtl.LogType.CPP,
            {
                'query': {
                    'bool': {
                        'must': [
                            {'match_phrase': {'text': 'Missing translation'}},
                            {'match_phrase': {'text': 'locale'}},
                            {
                                'range': {
                                    '@timestamp': {
                                        'gte': '2021-09-28T09:00:00Z',
                                        'lt': '2021-09-28T10:00:00Z',
                                    },
                                },
                            },
                        ],
                    },
                },
            },
            id='cpp',
        ),
        pytest.param(
            mtl.LogType.PYT,
            {
                'query': {
                    'bool': {
                        'must': [
                            {
                                'match_phrase': {
                                    'text': 'not found in translations',
                                },
                            },
                            {
                                'range': {
                                    '@timestamp': {
                                        'gte': '2021-09-28T09:00:00Z',
                                        'lt': '2021-09-28T10:00:00Z',
                                    },
                                },
                            },
                        ],
                    },
                },
            },
            id='py',
        ),
    ],
)
@pytest.mark.now(datetime.datetime(2021, 9, 28, 11, 0, 0).isoformat())
async def test_make_query(patch, log_type, expected):
    @patch('elasticsearch_async.AsyncElasticsearch')
    def _elastic_client(*args, **kwargs):
        class ElasticClient:
            pass

        return ElasticClient()

    config = {
        'hosts': [],
        'timeout': 0,
        'retries': 0,
        'index': '',
        'excluded_ngroups': [],
        'excluded_cgroups': [],
        'included_ngroups': [],
        'included_cgroups': [],
    }
    client = mtl.ElasticClient(config, asyncio.AbstractEventLoop())
    query = (
        client._make_query_cpp_logs()  # pylint: disable=protected-access
        if log_type == mtl.LogType.CPP
        else client._make_query_py_logs()  # pylint: disable=protected-access
    )
    assert query == expected


@pytest.mark.parametrize(
    [
        'excluded_ngroups',
        'excluded_cgroups',
        'included_ngroups',
        'included_cgroups',
        'expected',
    ],
    [
        pytest.param(
            [], [], [], [], {'query': {'bool': {'must': []}}}, id='all empty',
        ),
        pytest.param(
            ['taxi_api_stable'],
            [],
            [],
            [],
            {
                'query': {
                    'bool': {
                        'must': [],
                        'must_not': {
                            'bool': {
                                'should': [
                                    {'term': {'ngroups': 'taxi_api_stable'}},
                                ],
                                'minimum_should_match': 1,
                            },
                        },
                    },
                },
            },
            id='excluded_ngroups',
        ),
        pytest.param(
            [],
            ['taxi_api_stable'],
            [],
            [],
            {
                'query': {
                    'bool': {
                        'must': [],
                        'must_not': {
                            'bool': {
                                'should': [
                                    {'term': {'cgroups': 'taxi_api_stable'}},
                                ],
                                'minimum_should_match': 1,
                            },
                        },
                    },
                },
            },
            id='excluded_cgroups',
        ),
        pytest.param(
            [],
            [],
            ['taxi_api_stable'],
            [],
            {
                'query': {
                    'bool': {
                        'must': [
                            {
                                'bool': {
                                    'should': [
                                        {
                                            'term': {
                                                'ngroups': 'taxi_api_stable',
                                            },
                                        },
                                    ],
                                    'minimum_should_match': 1,
                                },
                            },
                        ],
                    },
                },
            },
            id='included_ngroups',
        ),
        pytest.param(
            [],
            [],
            [],
            ['taxi_api_stable'],
            {
                'query': {
                    'bool': {
                        'must': [
                            {
                                'bool': {
                                    'should': [
                                        {
                                            'term': {
                                                'cgroups': 'taxi_api_stable',
                                            },
                                        },
                                    ],
                                    'minimum_should_match': 1,
                                },
                            },
                        ],
                    },
                },
            },
            id='included_cgroups',
        ),
        pytest.param(
            ['taxi_api_stable'],
            ['taxi_api_stable'],
            ['taxi_api_stable'],
            ['taxi_api_stable'],
            {
                'query': {
                    'bool': {
                        'must': [
                            {
                                'bool': {
                                    'should': [
                                        {
                                            'term': {
                                                'ngroups': 'taxi_api_stable',
                                            },
                                        },
                                        {
                                            'term': {
                                                'cgroups': 'taxi_api_stable',
                                            },
                                        },
                                    ],
                                    'minimum_should_match': 1,
                                },
                            },
                        ],
                        'must_not': {
                            'bool': {
                                'should': [
                                    {'term': {'ngroups': 'taxi_api_stable'}},
                                    {'term': {'cgroups': 'taxi_api_stable'}},
                                ],
                                'minimum_should_match': 1,
                            },
                        },
                    },
                },
            },
            id='mix',
        ),
    ],
)
async def test_update_query(
        patch,
        excluded_ngroups,
        excluded_cgroups,
        included_ngroups,
        included_cgroups,
        expected,
):
    @patch('elasticsearch_async.AsyncElasticsearch')
    def _elastic_client(*args, **kwargs):
        class ElasticClient:
            pass

        return ElasticClient()

    config = {
        'hosts': [],
        'timeout': 0,
        'retries': 0,
        'index': '',
        'excluded_ngroups': excluded_ngroups,
        'excluded_cgroups': excluded_cgroups,
        'included_ngroups': included_ngroups,
        'included_cgroups': included_cgroups,
    }
    client = mtl.ElasticClient(config, asyncio.AbstractEventLoop())
    # pylint: disable=protected-access
    query = client._update_query_with_excluded(
        {'query': {'bool': {'must': []}}},
    )
    # pylint: disable=protected-access
    query = client._update_query_with_included(query)
    assert query == expected
