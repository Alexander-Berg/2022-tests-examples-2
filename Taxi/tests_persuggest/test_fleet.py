import pytest


URL = '/fleet/persuggest/v1/{}'
DEFAULT_APPLICATION = 'app_name=android,app_ver1=3,app_ver2=18,app_ver3=0'

AUTHORIZED_HEADERS = {
    'X-Request-Application': DEFAULT_APPLICATION,
    'X-Request-Language': 'ru',
    'platform': 'goplatform',
}


@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_suggest(taxi_persuggest, mockserver, load_json):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        return load_json('suggest_response.json')

    request = load_json('fleet_suggest_request.json')
    url = URL.format('suggest')
    response = await taxi_persuggest.post(
        url, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('fleet_suggest_response.json')
