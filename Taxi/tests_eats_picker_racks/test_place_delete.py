async def test_place_delete_200(taxi_eats_picker_racks, init_postgresql):
    response = await taxi_eats_picker_racks.delete('/api/v1/place?place_id=1')
    assert response.status == 200

    response = await taxi_eats_picker_racks.get(f'/api/v1/racks?place_id=1')
    assert response.status == 200
    assert response.json()['racks'] == []


async def test_place_delete_404(taxi_eats_picker_racks, init_postgresql):
    response = await taxi_eats_picker_racks.delete(
        '/api/v1/place?place_id=123',
    )
    assert response.status == 404
