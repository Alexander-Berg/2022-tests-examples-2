async def test_cell_delete_existing_200(
        taxi_eats_picker_racks,
        init_postgresql,
        get_packets_in_cell,
        get_cells_in_rack,
):
    rack_id = 1
    cell_id = 2
    cells_in_rack = {row[0]: row[2] for row in get_cells_in_rack(rack_id)}
    response = await taxi_eats_picker_racks.delete(
        f'/api/v1/cell?cell_id={cell_id}',
    )
    assert response.status == 200
    assert not get_packets_in_cell(cell_id)
    assert all(
        [
            row[2] == cells_in_rack[row[0]] - (1 if row[0] > cell_id else 0)
            for row in get_cells_in_rack(rack_id)
        ],
    )


async def test_cell_delete_not_found_404(
        taxi_eats_picker_racks, init_postgresql,
):
    response = await taxi_eats_picker_racks.delete('/api/v1/cell?cell_id=6')
    assert response.status == 404
