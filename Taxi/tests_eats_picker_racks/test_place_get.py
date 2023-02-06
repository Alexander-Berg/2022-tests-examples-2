async def test_place_get_200(taxi_eats_picker_racks, init_postgresql):
    place_data = {
        'place_id': 1,
        'place_name': 'first place',
        'place_address': 'first address',
    }
    response = await taxi_eats_picker_racks.get('/api/v1/place?place_id=1')
    assert response.status == 200
    assert response.json() == place_data


async def test_place_get_404(taxi_eats_picker_racks, init_postgresql):
    response = await taxi_eats_picker_racks.get('/api/v1/place?place_id=123')
    assert response.status == 404
