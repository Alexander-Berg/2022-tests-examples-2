BRANDS = ['AA', 'BB', 'CC1', 'CC2']


async def test_car_brands(taxi_selfreg, mockserver):
    @mockserver.json_handler(
        '/cars-catalog/cars-catalog/v1/autocomplete-brands',
    )
    def _brands(request):
        return {'brands': BRANDS}

    response = await taxi_selfreg.post(
        '/selfreg/v1/car/brands',
        params={'token': 'token1'},
        json={'filter': ''},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'brands': BRANDS}
