import copy

from elasticsearch import exceptions
import pytest

from test_eslogadminpy3 import constants


ORDER_ID = '92c97516135a554c8db7bae1e85510a1'


async def test_elastic_fails(patch, web_app_client):
    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def _search_mock(index, *args, **kwargs):
        if index.startswith('pilorama'):
            raise exceptions.RequestError(400, 'some error', 'some info')
        return {'hits': {'hits': []}}

    response = await web_app_client.post(
        '/v2/logs/list/', params={'limit': 1}, json={'filters': []},
    )
    assert response.status == 200
    assert (await response.json()) == []


@pytest.mark.parametrize(
    'mock_hits_kwargs',
    [
        {'order_id': ORDER_ID},
        {'meta_order_id': ORDER_ID},
        {'order_id': ORDER_ID, 'meta_order_id': ORDER_ID},
    ],
)
async def test_elastic_order_id(patch, web_app_client, mock_hits_kwargs):
    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def _search_mock(*args, **kwargs):
        es_response = copy.deepcopy(constants.ES_RESPONSE_EXAMPLE_RESPONSES)
        es_response['hits']['hits'][0]['_source'].update(**mock_hits_kwargs)
        return es_response

    response = await web_app_client.post(
        '/v2/logs/list/', params={'limit': 10}, json={'filters': []},
    )
    assert response.status == 200
    data = await response.json()
    assert data
    for log in data:
        assert log.get('order_id', '') == ORDER_ID
