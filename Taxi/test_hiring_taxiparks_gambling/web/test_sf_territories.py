import pytest

EXPECTED_RESPONSES = 'expected_responses.json'
URL_V2_TERRITORIES = '/v2/territories/'


async def test_get_all_sf_territories(web_app_client, load_json):
    expected_response = load_json(EXPECTED_RESPONSES)
    response = await web_app_client.post(URL_V2_TERRITORIES)
    assert response.status == expected_response['status']
    data = sorted(await response.json(), key=lambda x: x['sf_id'])
    assert data == expected_response['data']


@pytest.mark.config(TAXIPARKS_GAMBLING_FETCH_HIRING_TERRITORIES_ENABLED=True)
async def test_get_all_hiring_sf_territories(web_app_client, load_json):
    expected_response = load_json(EXPECTED_RESPONSES)
    response = await web_app_client.post(URL_V2_TERRITORIES)
    assert response.status == expected_response['status']
    data = sorted(await response.json(), key=lambda x: x['sf_id'])
    assert data == expected_response['data']


@pytest.mark.parametrize(
    ('sf_id', 'expected_response_name'),
    [
        ('full_territory', 'full_territory'),
        ('empty_territory', 'empty_territory'),
        ('not_existing_territory', 'not_existing_territory'),
    ],
)
async def test_get_sf_territory_by_id(
        web_app_client, load_json, sf_id, expected_response_name,
):
    expected_response = load_json('expected_responses.json')[
        expected_response_name
    ]
    response = await web_app_client.get('/v2/territories/{}'.format(sf_id))
    assert response.status == expected_response['status']
    data = await response.json()
    assert data == expected_response['data']
