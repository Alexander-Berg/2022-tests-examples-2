import pytest

from . import utils


def make_cell(
        cell_id: int,
        cell_number: int,
        rack_id: int,
        rack_name: str,
        packets_number: int,
):
    return {
        'cell_id': cell_id,
        'cell_number': cell_number,
        'rack_id': rack_id,
        'rack_name': rack_name,
        'packets_number': packets_number,
    }


def make_package(eats_id: str, cells: list):
    return {'eats_id': eats_id, 'order_package': {'order_cells': cells}}


ORDER_PACKAGE_1 = make_package(
    '1', [make_cell(1, 1, 1, 'first', 1), make_cell(4, 1, 2, 'second', 2)],
)
ORDER_PACKAGE_2 = make_package('2', [make_cell(1, 1, 1, 'first', 2)])
ORDER_PACKAGE_4 = make_package(
    '4', [make_cell(1, 1, 1, 'first', 1), make_cell(5, 1, 3, 'second', 2)],
)


@pytest.mark.parametrize(
    'eats_ids, picker_id, response_json',
    [
        [['1'], '1', {'order_packages': [ORDER_PACKAGE_1]}],
        [['1'], '2', {'order_packages': []}],
        [['2'], '1', {'order_packages': []}],
        [['2'], '2', {'order_packages': [ORDER_PACKAGE_2]}],
        [['3'], '1', {'order_packages': []}],
        [['3'], '2', {'order_packages': []}],
        [['1', '2'], '1', {'order_packages': [ORDER_PACKAGE_1]}],
        [['1', '2'], '2', {'order_packages': [ORDER_PACKAGE_2]}],
        [['1', '2', '3'], '1', {'order_packages': [ORDER_PACKAGE_1]}],
        [['1', '2', '3'], '2', {'order_packages': [ORDER_PACKAGE_2]}],
        [['1', '2', '3'], '3', {'order_packages': []}],
        [['4'], '2', {'order_packages': [ORDER_PACKAGE_4]}],
        [['1', '2', '3', '4'], '1', {'order_packages': [ORDER_PACKAGE_1]}],
        [
            ['1', '2', '3', '4'],
            '2',
            {'order_packages': [ORDER_PACKAGE_2, ORDER_PACKAGE_4]},
        ],
        [['1', '2', '3', '4'], '3', {'order_packages': []}],
    ],
)
async def test_get_order_info(
        taxi_eats_picker_racks,
        init_postgresql,
        eats_ids,
        picker_id,
        response_json,
):
    response = await taxi_eats_picker_racks.post(
        '/4.0/eats-picker-racks/api/v1/package',
        headers=utils.da_headers(picker_id),
        json={'eats_ids': eats_ids},
    )
    assert response.status == 200
    assert response.json() == response_json
