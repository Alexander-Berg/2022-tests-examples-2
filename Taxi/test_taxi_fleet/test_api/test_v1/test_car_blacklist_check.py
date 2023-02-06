import aiohttp.web


async def test_success(web_app_client, headers, mockserver, load_json):
    stub = load_json('success.json')

    @mockserver.json_handler('taximeter-xservice/utils/blacklist/cars/check')
    async def _car_blacklist_check(request):
        assert request.json == stub['request']
        return aiohttp.web.json_response(stub['response'])

    response = await web_app_client.post(
        '/api/v1/cars/blacklist/check',
        headers=headers,
        json={
            'query': {
                'park': {
                    'id': '7ad36bc7560449998acbe2c57a75c293',
                    'car': {'id': '01e5a2d43e44c367a8c37152f982af5a'},
                },
            },
            'locale': 'ru',
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
