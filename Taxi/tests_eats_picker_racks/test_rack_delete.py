async def test_rack_delete_existing_200(
        taxi_eats_picker_racks,
        init_postgresql,
        get_cells_in_rack,
        get_packets_in_rack,
):
    rack_id = 1
    response = await taxi_eats_picker_racks.delete(
        f'/api/v1/rack?rack_id={rack_id}',
    )
    assert response.status == 200
    assert not get_cells_in_rack(rack_id)
    assert not get_packets_in_rack(rack_id)


async def test_rack_delete_not_found_404(
        taxi_eats_picker_racks, init_postgresql,
):
    response = await taxi_eats_picker_racks.delete('/api/v1/rack?rack_id=4')
    assert response.status == 404
