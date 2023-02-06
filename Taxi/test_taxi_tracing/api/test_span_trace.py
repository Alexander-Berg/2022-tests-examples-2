# pylint: disable=redefined-outer-name
import pytest

from taxi_tracing.lib import abc


@pytest.fixture()
def mock_elastic_search(patch, load_json):
    def _do_it(trace_file, trace_id):
        data = load_json(trace_file)['hits']['hits']

        @patch('taxi_tracing.lib.indexes.CommonIndexer.find_trace_id')
        async def _find_trace_id(*args, **kwargs):
            return abc.SpanSearchResult(
                trace_id=trace_id, start_timestamp=123456, end_timestamp=12345,
            )

        @patch('taxi_tracing.lib.clients.elastic.ElasticOTClient.find_trace')
        async def _opentracing_find_trace(*args, **kwargs):
            return [x for x in data if x['_source']['type'] == 'span']

        @patch('taxi_tracing.lib.clients.elastic.ElasticRawClient.find_trace')
        async def _raw_find_trace(*args, **kwargs):
            return [
                x
                for x in data
                if x['_source']['module'].startswith('handleRequest')
                or x['_source']['module'] == 'taxi.util.aiohttp_kit.middleware'
            ]

        @patch(
            'taxi_tracing.lib.clients.elastic.ElasticUserverClient.find_trace',
        )
        async def _userver_find_trace(*args, **kwargs):
            return [
                x for x in data if x['_source']['module'].startswith('~Impl')
            ]

    return _do_it


@pytest.mark.parametrize(
    'span_id, expected_span, expected_children_ids',
    [
        (
            'abcd4175625444cc9fc83defb02593f0',
            {
                'operation_name': '/v1/corp_paymentmethods',
                'host': 'corp-integration-api-myt-01.taxi.yandex.net',
                'endpoint': '/v1/corp_paymentmethods',
                'start_timestamp': 1570811656.142,
                'finish_timestamp': 1570811656.143,
                'context': {
                    'span_id': 'abcd4175625444cc9fc83defb02593f0',
                    'trace_id': 'cc142294211b4e2d9e03b769b27b74c8',
                },
                'tags': {
                    'span.kind': 'server',
                    'http.method': 'POST',
                    'http.url': '/v1/corp_paymentmethods',
                    'http.status_code': 200,
                    'service': 'taxi_corp_integration_api',
                    'error': False,
                },
                'references': {
                    'child_of': {
                        'span_id': '3d7e0123653d4150b501c4a3587e8bcd',
                    },
                },
            },
            [],
        ),
        (
            '92e44c6521e04c5e9b82224bb1f270c4',
            {
                'operation_name': '/internal/stats',
                'host': 'shared-payments-sas-02.taxi.yandex.net',
                'endpoint': (
                    '/internal/stats?owner_yandex_uid=748754265&'
                    'phone_id=5673261df52db432e4e8b4c3'
                ),
                'start_timestamp': 1570811656.164,
                'finish_timestamp': 1570811656.165,
                'context': {
                    'span_id': '92e44c6521e04c5e9b82224bb1f270c4',
                    'trace_id': 'cc142294211b4e2d9e03b769b27b74c8',
                },
                'tags': {
                    'span.kind': 'server',
                    'http.method': 'GET',
                    'http.url': (
                        '/internal/stats?owner_yandex_uid=748754265&'
                        'phone_id=5673261df52db432e4e8b4c3'
                    ),
                    'http.status_code': 200,
                    'service': 'taxi_shared_payments',
                    'error': False,
                },
                'references': {
                    'child_of': {
                        'span_id': '3d7e0123653d4150b501c4a3587e8bcd',
                    },
                },
            },
            [],
        ),
        (
            '3d7e0123653d4150b501c4a3587e8bcd',
            {
                'operation_name': 'http/handler-tc-3.0-paymentmethods',
                'host': 'api-proxy-myt-01.taxi.yandex.net',
                'endpoint': '',
                'finish_timestamp': 1570811663.162837,
                'start_timestamp': 1570811656.135387,
                'context': {
                    'span_id': '3d7e0123653d4150b501c4a3587e8bcd',
                    'trace_id': 'cc142294211b4e2d9e03b769b27b74c8',
                },
                'tags': {
                    'span.kind': 'server',
                    'http.url': '/3.0/paymentmethods',
                    'http.method': 'POST',
                    'http.status_code': 500,
                    'service': 'taxi_api_proxy',
                    'error': True,
                },
                'references': {
                    'parent_for': [
                        {'span_id': '131d24b62c1b4294bdd60ea05a52f4e1'},
                        {'span_id': '2aa6caaacc324a908abf8dd4e1d2c97d'},
                        {'span_id': '3e00aea812a043fcbede723b5a8f3491'},
                        {'span_id': '7d6c9ecf844c41e9ad33082ca15c1c55'},
                        {'span_id': '92e44c6521e04c5e9b82224bb1f270c4'},
                        {'span_id': 'abcd4175625444cc9fc83defb02593f0'},
                    ],
                },
            },
            [
                '131d24b62c1b4294bdd60ea05a52f4e1',
                '2aa6caaacc324a908abf8dd4e1d2c97d',
                '3e00aea812a043fcbede723b5a8f3491',
                '7d6c9ecf844c41e9ad33082ca15c1c55',
                '92e44c6521e04c5e9b82224bb1f270c4',
                'abcd4175625444cc9fc83defb02593f0',
            ],
        ),
    ],
)
async def test_trace_merging_with_fallback(
        mock_elastic_search,
        taxi_tracing_client,
        span_id,
        expected_span,
        expected_children_ids,
):
    mock_elastic_search(
        'test_trace_with_different_sources.json',
        'cc142294211b4e2d9e03b769b27b74c8',
    )
    response = await taxi_tracing_client.post(
        '/v2/span-children/', params={'span_id': span_id},
    )
    assert response.status == 200
    result = await response.json()
    assert result['span'] == expected_span
    assert sorted(
        x['context']['span_id'] for x in result.get('children', [])
    ) == sorted(expected_children_ids)


async def test_sub_trees_merge_from_different_sources(
        mock_elastic_search, taxi_tracing_client,
):
    mock_elastic_search(
        'test_trace_with_diff_sources_and_fallbacks.json',
        '8dc01feec8ea4ba8b7b6a5b617f64139',
    )
    response = await taxi_tracing_client.post(
        '/v2/span-children/',
        params={'span_id': 'fa9dafb1117b46789d809c40018a8401'},
    )
    assert response.status == 200
    result = await response.json()
    assert result['span']['context'] == {
        'span_id': 'fa9dafb1117b46789d809c40018a8401',
        'trace_id': '8dc01feec8ea4ba8b7b6a5b617f64139',
    }
    assert (
        result['span']['references']['child_of']['span_id']
        == '66df771e2c4607f2fc04c9d2bec0c919'
    )
    assert result['span']['references']['parent_for'] == [
        {'span_id': '4c04ac5718ff431bac40319e5d86cf55'},
        {'span_id': '4f100f5f7e34448593934da13cb3c455'},
        {'span_id': '63b8a19427de4b87af4a4e74bcd55cda'},
        {'span_id': 'afe260e3c068459a87b03193577d9fd4'},
        {'span_id': 'ba8aca93263245f19f0d19232c379f67'},
    ]

    response = await taxi_tracing_client.post(
        '/v2/span-children/',
        params={'span_id': '171129ca64934362a6a5f09081fb76ff'},
    )
    result = await response.json()
    assert 'fa9dafb1117b46789d809c40018a8401' in {
        x['context']['span_id'] for x in result['children']
    }
