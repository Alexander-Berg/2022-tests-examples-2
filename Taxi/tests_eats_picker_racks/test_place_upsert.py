async def test_place_update_200(taxi_eats_picker_racks, init_postgresql):
    place_data = {
        'place_id': 1,
        'place_name': 'new name',
        'place_address': 'new address',
        'brand_id': 'new brand',
        'brand_name': 'new brand name',
    }
    response = await taxi_eats_picker_racks.post(
        '/api/v1/place', json=place_data,
    )
    assert response.status == 200
    assert response.json() == place_data


async def test_place_create_new_200(taxi_eats_picker_racks, init_postgresql):
    place_data = {
        'place_id': 123,
        'place_name': 'name 123',
        'place_address': 'address 123',
        'brand_id': 'brand 123',
        'brand_name': 'brand name 123',
    }
    response = await taxi_eats_picker_racks.post(
        '/api/v1/place', json=place_data,
    )
    assert response.status == 200
    assert response.json() == place_data
