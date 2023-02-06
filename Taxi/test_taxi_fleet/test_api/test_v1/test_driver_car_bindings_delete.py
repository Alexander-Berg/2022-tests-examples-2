import aiohttp.web


async def test_success(web_app_client, headers, mockserver):
    driver_id_ = '1g34f7amde9bgfd34ab7654d63e6gr68'
    car_id_ = 'agb4c7fdq4ab65hddmdeebg63a6gr1f'

    @mockserver.json_handler('/parks/driver-profiles/car-bindings')
    async def _remove_car_binding(request):
        assert request.query['park_id'] == headers['X-Park-Id']
        assert request.query['driver_profile_id'] == driver_id_
        assert request.query['car_id'] == car_id_
        return aiohttp.web.json_response({})

    response = await web_app_client.delete(
        '/api/v1/drivers/car-bindings',
        headers=headers,
        json={'driver_id': driver_id_, 'car_id': car_id_},
    )

    assert response.status == 200

    content = await response.json()
    assert content == {'status': 'success'}
