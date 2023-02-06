from aiohttp import web


async def test_suggests_vehicle_types(taxi_selfreg, mock_hiring_selfreg_forms):
    @mock_hiring_selfreg_forms(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
    )
    def suggests_handler(request):
        assert request.method == 'GET'
        assert request.query.get('region') == 'Санкт-Петербург'
        return {
            'citizenships': [],
            'vehicle_types': [
                {'id': 'car'},
                {'id': 'bicycle'},
                {'id': 'pedestrian'},
            ],
        }

    response = await taxi_selfreg.get(
        '/selfreg/v1/eats/suggests/vehicle-types',
        params={'token': 'token1', 'region': 'region'},
    )

    assert suggests_handler.times_called == 1
    assert response.status == 200
    assert await response.json() == {
        'vehicle_types': [
            {'id': 'car'},
            {'id': 'bicycle'},
            {'id': 'pedestrian'},
        ],
    }


async def test_suggests_vehicle_types_without_region(
        taxi_selfreg, mock_hiring_selfreg_forms,
):
    @mock_hiring_selfreg_forms(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
    )
    def suggests_handler(request):
        assert request.method == 'GET'
        assert request.query.get('region') == 'Москва'
        return {
            'citizenships': [],
            'vehicle_types': [
                {'id': 'car'},
                {'id': 'bicycle'},
                {'id': 'pedestrian'},
            ],
        }

    response = await taxi_selfreg.get(
        '/selfreg/v1/eats/suggests/vehicle-types',
        params={'token': 'token2', 'region': 'Москва'},
    )

    assert response.status == 200
    assert suggests_handler.times_called == 1
    assert await response.json() == {
        'vehicle_types': [
            {'id': 'car'},
            {'id': 'bicycle'},
            {'id': 'pedestrian'},
        ],
    }


async def test_suggests_vehicle_types_not_cache(
        taxi_selfreg, mock_hiring_selfreg_forms,
):
    @mock_hiring_selfreg_forms(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
    )
    def suggests_handler(_):
        pass

    response = await taxi_selfreg.get(
        '/selfreg/v1/eats/suggests/vehicle-types',
        params={'token': 'token2', 'region': 'not_cache'},
    )

    assert response.status == 400
    assert suggests_handler.times_called == 0


async def test_suggests_vehicle_types_bad_token(
        taxi_selfreg, mock_hiring_selfreg_forms,
):
    @mock_hiring_selfreg_forms(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
    )
    def suggests_handler(_):
        pass

    response = await taxi_selfreg.get(
        '/selfreg/v1/eats/suggests/vehicle-types',
        params={'token': 'incorrect_token', 'region': 'Москва'},
    )

    assert response.status == 401
    assert suggests_handler.times_called == 0


async def test_suggests_vehicle_types_forms_404(
        taxi_selfreg, mock_hiring_selfreg_forms,
):
    @mock_hiring_selfreg_forms(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
    )
    def suggests_handler(_):
        return web.json_response(
            {'code': 'code', 'message': 'message'}, status=404,
        )

    response = await taxi_selfreg.get(
        '/selfreg/v1/eats/suggests/vehicle-types',
        params={'token': 'token2', 'region': 'Москва'},
    )

    assert response.status == 404
    assert suggests_handler.times_called == 1
