import pytest


@pytest.fixture(name='namespaces_retrieve_request')
def _namespaces_retrieve_request(web_app_client):
    async def _wrapper(body: dict):
        return await web_app_client.post('/v1/namespaces/retrieve/', json=body)

    return _wrapper


@pytest.mark.parametrize(
    'with_empty_filters',
    [
        pytest.param(True, id='with_empty_filters'),
        pytest.param(False, id='without_empty_filters'),
    ],
)
@pytest.mark.pgsql('clownductor', ['init_data.sql'])
async def test_retrieve_all(namespaces_retrieve_request, with_empty_filters):
    body = {}
    if with_empty_filters:
        body['filters'] = {}
    response = await namespaces_retrieve_request(body)
    assert response.status == 200
    data = await response.json()
    assert data == {
        'namespaces': [
            {'id': 4, 'name': 'ts'},
            {'id': 3, 'name': 'lavka'},
            {'id': 2, 'name': 'eda'},
            {'id': 1, 'name': 'taxi'},
        ],
    }


@pytest.mark.pgsql('clownductor', ['init_data.sql'])
async def test_retrieve_names(namespaces_retrieve_request):
    response = await namespaces_retrieve_request(
        {'filters': {'names': ['eda', 'taxi', 'not-found']}},
    )
    assert response.status == 200
    data = await response.json()
    assert data == {
        'namespaces': [{'id': 2, 'name': 'eda'}, {'id': 1, 'name': 'taxi'}],
    }
