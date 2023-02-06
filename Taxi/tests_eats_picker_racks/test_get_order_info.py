import pytest


@pytest.mark.parametrize(
    'eats_id, response_json',
    [
        [
            1,
            {
                'order_cells': [
                    {
                        'cell_id': 1,
                        'cell_number': 1,
                        'rack_id': 1,
                        'rack_name': 'first',
                        'packets_number': 1,
                    },
                    {
                        'cell_id': 4,
                        'cell_number': 1,
                        'rack_id': 2,
                        'rack_name': 'second',
                        'packets_number': 2,
                    },
                ],
            },
        ],
        [
            2,
            {
                'order_cells': [
                    {
                        'cell_id': 1,
                        'cell_number': 1,
                        'rack_id': 1,
                        'rack_name': 'first',
                        'packets_number': 2,
                    },
                ],
            },
        ],
        [3, {'order_cells': []}],
    ],
)
async def test_get_order_info(
        taxi_eats_picker_racks, init_postgresql, eats_id, response_json,
):
    response = await taxi_eats_picker_racks.get(
        f'/api/v1/cells?eats_id={eats_id}',
    )
    assert response.status == 200
    assert response.json() == response_json
