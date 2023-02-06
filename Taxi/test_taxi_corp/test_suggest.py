import aiohttp.hdrs
import pytest


async def test_get_cities(taxi_corp_real_auth_client, mock_corp_suggest):
    data = {'query': 'Балаха', 'country': 'rus'}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/suggest/cities', json=data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_suggest.get_cities.has_calls

    mock_call = mock_corp_suggest.get_cities.next_call()
    assert mock_call['request'].json == data
    assert not mock_corp_suggest.get_cities.has_calls


@pytest.mark.config(
    CORP_CORS_SETTINGS=[
        {
            'path': '/1.0/suggest/cities',
            'methods': ['POST'],
            'hosts': ['front.com', 'com.front'],
        },
    ],
)
async def test_get_cities_cors(taxi_corp_real_auth_client, mock_corp_suggest):
    data = {'query': 'Балаха', 'country': 'rus'}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/suggest/cities', json=data,
    )

    hosts = response.headers[aiohttp.hdrs.ACCESS_CONTROL_ALLOW_ORIGIN]
    assert hosts == 'front.com com.front'
