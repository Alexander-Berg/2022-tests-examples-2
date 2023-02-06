MODELS = ['AA', 'BB', 'CC1', 'CC2']


async def test_car_models(taxi_selfreg, mockserver):
    @mockserver.json_handler(
        '/cars-catalog/cars-catalog/v1/autocomplete-models',
    )
    def _brands(request):
        return {'brand': 'Skoda', 'models': MODELS}

    response = await taxi_selfreg.post(
        '/selfreg/v1/car/models',
        params={'token': 'token1'},
        json={'brand': 'Skoda', 'filter': ''},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'models': MODELS}


async def test_car_models_bad_brand(taxi_selfreg, mockserver):
    @mockserver.json_handler(
        '/cars-catalog/cars-catalog/v1/autocomplete-models',
    )
    def _brands(request):
        return mockserver.make_response(
            status=404, json={'code': '', 'message': ''},
        )

    response = await taxi_selfreg.post(
        '/selfreg/v1/car/models',
        params={'token': 'token1'},
        json={'brand': 'Skoda', 'filter': ''},
    )

    assert response.status == 400
    content = await response.json()
    assert content == {'code': 'bad_car_brand', 'message': 'Unknown car brand'}
