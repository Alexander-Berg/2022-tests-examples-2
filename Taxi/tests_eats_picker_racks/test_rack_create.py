async def test_rack_create_already_created_409(
        taxi_eats_picker_racks, init_postgresql,
):
    response = await taxi_eats_picker_racks.post(
        '/api/v1/rack',
        json={
            'place_id': 1,
            'name': 'first',
            'description': 'description-1',
            'cells_number': 1,
        },
    )
    assert response.status == 409


async def test_rack_create_new_200(taxi_eats_picker_racks, init_postgresql):
    response = await taxi_eats_picker_racks.post(
        '/api/v1/rack',
        json={
            'place_id': 1,
            'name': 'fourth',
            'cells_number': 3,
            'has_fridge': True,
            'has_freezer': False,
        },
    )
    assert response.status == 200
    assert response.json() == {'id': 4}
    response = await taxi_eats_picker_racks.get(f'/api/v1/racks?place_id=1')
    for rack in response.json()['racks']:
        if rack['id'] == 4:
            assert len(rack['cells']) == 3
            assert rack['has_fridge']
            assert not rack['has_freezer']
