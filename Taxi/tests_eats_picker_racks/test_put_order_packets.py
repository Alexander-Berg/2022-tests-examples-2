from . import utils


async def test_put_order_packets_200(taxi_eats_picker_racks, init_postgresql):
    cells = [
        {'rack_id': 1, 'cell_number': 1, 'packets_number': 1},
        {'rack_id': 1, 'cell_number': 2, 'packets_number': 2},
        {'rack_id': 2, 'cell_number': 1, 'packets_number': 3},
    ]
    eats_id = '123'
    picker_id = '1'
    response = await taxi_eats_picker_racks.get(
        f'/api/v1/cells?eats_id={eats_id}',
    )
    assert response.status == 200
    order_cells_before = {
        (item['rack_id'], item['cell_number']): item['packets_number']
        for item in response.json()['order_cells']
    }
    response = await taxi_eats_picker_racks.post(
        '/4.0/eats-picker-racks/api/v1/cells/put-order-packets',
        headers=utils.da_headers(picker_id),
        json={'eats_id': eats_id, 'cells': cells},
    )
    assert response.status == 200
    response = await taxi_eats_picker_racks.get(
        f'/api/v1/cells?eats_id={eats_id}',
    )
    assert response.status == 200
    order_cells_after = {
        (item['rack_id'], item['cell_number']): item['packets_number']
        for item in response.json()['order_cells']
    }

    for cell in cells:
        order_cells_before[cell['rack_id'], cell['cell_number']] = cell[
            'packets_number'
        ]
    assert order_cells_after == order_cells_before
