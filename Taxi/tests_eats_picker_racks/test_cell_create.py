async def test_cell_create_rack_not_found_404(
        taxi_eats_picker_racks, init_postgresql,
):
    response = await taxi_eats_picker_racks.post(
        '/api/v1/cell', json={'rack_id': 4},
    )
    assert response.status == 404


async def test_cell_create_new_200(taxi_eats_picker_racks, init_postgresql):
    response = await taxi_eats_picker_racks.post(
        '/api/v1/cell', json={'rack_id': 1},
    )
    assert response.status == 200
    assert response.json() == {'id': 6, 'number': 4}
