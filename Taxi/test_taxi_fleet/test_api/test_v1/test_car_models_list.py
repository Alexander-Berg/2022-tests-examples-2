import aiohttp.web


async def test_success(web_app_client, headers, mockserver, load_json):
    stub = load_json('success.json')

    @mockserver.json_handler('/parks/cars/models/list')
    async def _list_cars_models(request):
        assert request.json == stub['parks_request']
        return aiohttp.web.json_response(stub['parks_response'])

    response = await web_app_client.post(
        '/api/v1/parks/cars/models/list',
        headers=headers,
        json={
            'query': {
                'park': {'id': '7ad36bc7560449998acbe2c57a75c293'},
                'brand': {'name': 'brand_1'},
            },
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
