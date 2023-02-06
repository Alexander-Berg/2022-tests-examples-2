import urllib


async def test_banners_bot_device_id(taxi_eats_communications, mockserver):
    @mockserver.handler('/eda-catalog/v1/_internal/banner-places')
    def _banner_places(request):
        assert request.headers['x-device-id'][:4] == 'bot.'
        return mockserver.make_response(json={}, status=500)

    path: str = '/eats/v1/eats-communications/v1/banners'
    params: dict = {
        'latitude': 55.802998,
        'longitude': 37.591503,
        'showTime': '2021-02-10T16:10:12+03:00',
    }
    response = await taxi_eats_communications.get(
        path + '?' + urllib.parse.urlencode(params),
        headers={'x-app-version': '5.4.0', 'x-platform': 'eda_ios_app'},
    )
    assert response.status_code == 200
