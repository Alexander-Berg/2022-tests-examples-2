# pylint: disable=redefined-outer-name,unused-variable
import json

import aiohttp.web
import pytest
import yarl

from taxi.clients import juggler_api

from logs_errors_filters.generated.cron import run_cron
from logs_errors_filters.utils import db_helpers


class ResponseForES:  # pylint: disable=too-many-instance-attributes
    def __init__(
            self,
            text=None,
            json=None,
            read=None,
            status=200,
            url=yarl.URL('http://dummy/url'),
            method=None,
            headers=None,
            request_info=None,
    ):
        self._text = text
        self._json = json
        self._read = read
        self.status = status
        self.url = url
        self.method = method
        if headers is None:
            self.headers = {'Content-Type': 'application/json'}
        else:
            self.headers = headers
        self._request_info = request_info
        self.content_length = 1
        self._released = False
        self._read_called = False

    async def text(self):
        assert self._read is None
        if not self._read_called:
            await self.read()
        return self._text

    async def read(self):
        self._read_called = True
        if self._released:
            raise aiohttp.ClientConnectionError('Connection closed')

        return self._read

    async def release(self):
        self._released = True

    def raise_for_status(self):
        if self.status >= 400:
            self.release()
            raise aiohttp.ClientResponseError(
                request_info=None,
                history=None,
                code=self.status,
                message=self._text,
            )

    @property
    def content_type(self):
        if self._json:
            return 'application/json'

        for key, value in self.headers.items():
            if key.lower() == 'content-type':
                return value.split(';')[0]

        if self._text:
            return 'text/plain'
        return 'application/octet-stream'


@pytest.mark.pgsql('logs_errors_filters', files=['test_error_checker.sql'])
async def test_error_checker(
        patch, patch_aiohttp_session, response_mock, cron_context,
):
    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'logserrors.taxi.yandex.net'

    @patch_aiohttp_session(juggler_api.JUGGLER_PUSH_URL)
    def juggler_api_request(method, url, **kwargs):
        assert kwargs['json'] == {
            'source': 'logserrors.taxi.yandex.net',
            'events': [
                {
                    'description': (
                        'at least one filter "filter_5" exceeded its '
                        'threshold (3/2) for group taxi_billing_replication '
                        '(conductor) in the last 15 minutes, see Kibana: '
                        'http://logserrors.taxi.yandex.net/k/t3'
                    ),
                    'host': 'test_host',
                    'service': (
                        'taxi_logserrors_cgroup_taxi_billing_replication'
                    ),
                    'status': 'WARN',
                    'instance': '',
                    'tags': [],
                },
                {
                    'description': (
                        'at least 3 non-filtered errors found for '
                        'group taxi_imports (conductor) in the '
                        'last 15 minutes, see Kibana: '
                        'http://logserrors.taxi.yandex.net/k/1'
                    ),
                    'host': 'test_host',
                    'service': 'taxi_logerrors_cgroup_taxi_imports',
                    'status': 'WARN',
                    'instance': '',
                    'tags': [],
                },
                {
                    'description': (
                        'no errors found for '
                        'group taxi_logserrors (conductor) in the '
                        'last 15 minutes'
                    ),
                    'host': 'test_host',
                    'service': 'taxi_logserrors_cgroup_taxi_logserrors',
                    'status': 'OK',
                    'instance': '',
                    'tags': [],
                },
            ],
        }
        return response_mock(json={})

    @patch('logs_errors_filters.utils.elastic_client.ElasticClient')
    def elastic_client(*args, **kwargs):
        class ElasticClient:
            async def count_errors(self, cgroup, *args, **kwargs):
                if cgroup.name == 'taxi_imports':
                    return 3
                return 0

            async def count_threshold_errors(
                    self, cgroup, error_filters, *args, **kwargs,
            ):
                assert cgroup.name == 'taxi_billing_replication'
                assert len(error_filters) == 2
                return [(error_filters[0], 3)]

            async def get_related_errors_values(
                    self,
                    cgroup,
                    error_filters,
                    related_errors_field,
                    start_time,
            ):
                return []

            async def __aenter__(self):
                pass

            async def __aexit__(self, *args):
                pass

        return ElasticClient()

    await run_cron.main(
        ['logs_errors_filters.crontasks.error_checker', '-t', '0'],
    )

    assert len(juggler_api_request.calls) == 1

    query = 'SELECT * FROM logs_errors_filters.cgroups ORDER BY name;'
    rows = await db_helpers.get_query_rows(query, (), cron_context)
    result = [(row['name'], row['status']) for row in rows]
    assert result == [
        ('taxi_billing_replication', 'warn'),
        ('taxi_imports', 'warn'),
        ('taxi_logs_from_yt', 'ok'),
        ('taxi_logserrors', 'ok'),
    ]

    # run again to check NDA API calls count
    await run_cron.main(
        ['logs_errors_filters.crontasks.error_checker', '-t', '0'],
    )


@pytest.mark.pgsql(
    'logs_errors_filters', files=['test_suppressing_filters.sql'],
)
@pytest.mark.config(
    {
        'LOGS_ELASTIC_HOSTS': [
            'http://taxi-elastic-logs.taxi.dev.yandex.net:9200',
        ],
    },
)
async def test_suppressing_filters(
        patch, patch_aiohttp_session, response_mock, cron_context,
):
    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'logserrors.taxi.yandex.net'

    @patch_aiohttp_session(juggler_api.JUGGLER_PUSH_URL)
    def juggler_api_request(method, url, **kwargs):
        assert kwargs['json'] == {
            'events': [
                {
                    'description': (
                        'at least one filter "filter_1" exceeded '
                        'its threshold (3/2) for group '
                        'taxi_hejmdal_stable (conductor) in the '
                        'last 15 minutes, see Kibana: '
                        'http://logserrors.taxi.yandex.net/k/t1'
                    ),
                    'host': 'test_host',
                    'instance': '',
                    'service': 'taxi_logerrors_cgroup_taxi_hejmdal_stable',
                    'status': 'WARN',
                    'tags': [],
                },
            ],
            'source': 'logserrors.taxi.yandex.net',
        }
        return response_mock(json={})

    @patch_aiohttp_session('http://taxi-elastic-logs.taxi.dev.yandex.net')
    def elastic_search_request(method, url, **kwargs):
        request = json.loads(kwargs['data'])
        if 'collapse' in request:  # get_related_errors_values
            for must in [
                    {
                        'terms': {
                            'level': [
                                'ERROR',
                                'CRITICAL',
                                'EMERG',
                                'ALERT',
                                'CRITICAL_INFO',
                                'WARNING',
                            ],
                        },
                    },
                    {
                        'query_string': {
                            'query': 'cgroups:"taxi_hejmdal_stable"',
                        },
                    },
                    {
                        'bool': {
                            'should': [
                                {
                                    'query_string': {
                                        'query': (
                                            'field3:"value3" AND '
                                            'field4:"value4"'
                                        ),
                                    },
                                },
                                {
                                    'query_string': {
                                        'query': (
                                            'field5:"value5" AND '
                                            'field6:"value6"'
                                        ),
                                    },
                                },
                            ],
                        },
                    },
            ]:
                assert must in request['query']['bool']['must']

            field = request['collapse']['field']
            return ResponseForES(
                text=json.dumps(
                    {
                        'hits': {
                            'hits': [
                                {'_source': {}},
                                {'_source': {field: f'{field}_1'}},
                                {'_source': {field: f'{field}_2'}},
                            ],
                        },
                    },
                ),
            )
        if 'aggs' not in request:  # count_errors
            for must in [
                    {
                        'terms': {
                            'level': [
                                'ERROR',
                                'CRITICAL',
                                'EMERG',
                                'ALERT',
                                'CRITICAL_INFO',
                                'WARNING',
                            ],
                        },
                    },
                    {
                        'query_string': {
                            'query': 'cgroups:"taxi_hejmdal_stable"',
                        },
                    },
            ]:
                assert must in request['query']['bool']['must']
            for must_not in [
                    {
                        'query_string': {
                            'query': 'field1:"value1" AND field2:"value2"',
                        },
                    },
                    {
                        'query_string': {
                            'query': 'field3:"value3" AND field4:"value4"',
                        },
                    },
                    {'terms': {'link': ['link_1', 'link_2']}},
                    {
                        'terms': {
                            'stq_run_id': ['stq_run_id_1', 'stq_run_id_2'],
                        },
                    },
            ]:
                assert must_not in request['query']['bool']['must_not']
            return ResponseForES(text=json.dumps({'hits': {'hits': []}}))
        # else count_threshold_errors
        for must in [
                {
                    'terms': {
                        'level': [
                            'ERROR',
                            'CRITICAL',
                            'EMERG',
                            'ALERT',
                            'CRITICAL_INFO',
                            'WARNING',
                        ],
                    },
                },
                {'query_string': {'query': 'cgroups:"taxi_hejmdal_stable"'}},
        ]:
            assert must in request['query']['bool']['must']

        assert {
            'query_string': {'query': 'field1:"value1" AND field2:"value2"'},
        } in request['aggs']['filter_1']['filter']['bool']['must']
        assert {
            'query_string': {'query': 'field5:"value5" AND field6:"value6"'},
        } in request['aggs']['filter_3']['filter']['bool']['must']

        assert len(request['aggs']['filter_1']['filter']['bool']['must']) == 2
        assert len(request['aggs']['filter_3']['filter']['bool']['must']) == 2

        return ResponseForES(
            text=json.dumps(
                {
                    'aggregations': {
                        'filter_1': {'doc_count': 3},
                        'filter_3': {'doc_count': 3},
                    },
                },
            ),
        )

    await run_cron.main(
        ['logs_errors_filters.crontasks.error_checker', '-t', '0'],
    )

    assert len(juggler_api_request.calls) == 1
    assert len(elastic_search_request.calls) == 4
