from aiohttp import web


async def test_suggests_citizenship(taxi_selfreg, mock_hiring_selfreg_forms):
    @mock_hiring_selfreg_forms(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
    )
    def suggests_handler(request):
        assert request.method == 'GET'
        assert request.query.get('region') == 'Санкт-Петербург'
        return {
            'citizenships': [
                {'id': 'RU', 'name': 'Российская Федерация'},
                {'id': 'KZ', 'name': 'Казахстан'},
            ],
            'vehicle_types': [],
        }

    response = await taxi_selfreg.get(
        '/selfreg/v1/eats/suggests/citizenships', params={'token': 'token1'},
    )

    assert suggests_handler.times_called == 1
    assert response.status == 200
    assert await response.json() == {
        'citizenships': [
            {'id': 'RU', 'name': 'Российская Федерация'},
            {'id': 'KZ', 'name': 'Казахстан'},
        ],
    }


async def test_suggests_citizenship_without_city(
        taxi_selfreg, mock_hiring_selfreg_forms,
):
    @mock_hiring_selfreg_forms(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
    )
    def suggests_handler(request):
        assert request.method == 'GET'
        assert request.query.get('region') == 'Москва'
        return {
            'citizenships': [
                {'id': 'RU', 'name': 'Российская Федерация'},
                {'id': 'KZ', 'name': 'Казахстан'},
            ],
            'vehicle_types': [],
        }

    response = await taxi_selfreg.get(
        '/selfreg/v1/eats/suggests/citizenships',
        params={'token': 'token2', 'region': 'Москва'},
    )

    assert response.status == 200
    assert suggests_handler.times_called == 1
    assert await response.json() == {
        'citizenships': [
            {'id': 'RU', 'name': 'Российская Федерация'},
            {'id': 'KZ', 'name': 'Казахстан'},
        ],
    }


async def test_suggests_citizenship_not_cache(
        taxi_selfreg, mock_hiring_selfreg_forms,
):
    @mock_hiring_selfreg_forms(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
    )
    def suggests_handler(_):
        pass

    response = await taxi_selfreg.get(
        '/selfreg/v1/eats/suggests/citizenships',
        params={'token': 'token2', 'region': 'not_cache'},
    )

    assert response.status == 400
    assert suggests_handler.times_called == 0


async def test_suggests_citizenship_bad_token(
        taxi_selfreg, mock_hiring_selfreg_forms,
):
    @mock_hiring_selfreg_forms(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
    )
    def suggests_handler(_):
        pass

    response = await taxi_selfreg.get(
        '/selfreg/v1/eats/suggests/citizenships',
        params={'token': 'incorrect_token', 'region': 'Москва'},
    )

    assert response.status == 401
    assert suggests_handler.times_called == 0


async def test_suggests_citizenship_forms_404(
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
        '/selfreg/v1/eats/suggests/citizenships',
        params={'token': 'token2', 'region': 'Москва'},
    )

    assert response.status == 404
    assert suggests_handler.times_called == 1
