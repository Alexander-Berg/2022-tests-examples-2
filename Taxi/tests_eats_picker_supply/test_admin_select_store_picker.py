import pytest

DEFAULT_PICKER_AVAILABLE_UNTIL = '2020-09-20T20:00:00+00:00'
HANDLE = '/admin/v1/select-store-pickers'


def format_order(order):
    return {
        key: order[key]
        for key in [
            'eats_id',
            'estimated_picking_time',
            'status',
            'status_updated_at',
            'place_id',
        ]
    }


async def test_select_store_picker_400(taxi_eats_picker_supply):
    response = await taxi_eats_picker_supply.post(HANDLE, json={'stores': []})
    assert response.status == 400


async def test_select_store_picker_with_order(
        taxi_eats_picker_supply,
        mock_eats_core_get_orders,
        create_picker,
        load_json,
):
    create_picker(
        picker_id='2',
        name='Иванов Пётр Иванович',
        phone_id='4',
        places_ids=[1],
        requisite_type='TinkoffCard',
        requisite_value='1029384756',
    )

    await taxi_eats_picker_supply.invalidate_caches(clean_update=False)
    assert mock_eats_core_get_orders.times_called >= 1

    response = await taxi_eats_picker_supply.post(HANDLE, json={'stores': [1]})
    assert response.status == 200

    response_data = response.json()
    expected_data = load_json('orders_expected_response.json')
    expected_order = format_order(expected_data['orders'][0])

    assert response_data == {
        'stores': [
            {
                'place_id': 1,
                'pickers': [
                    {
                        'picker_id': '2',
                        'picker_available_until': (
                            DEFAULT_PICKER_AVAILABLE_UNTIL
                        ),
                        'name': 'Иванов Пётр Иванович',
                        'phone_id': '4',
                        'requisite_type': 'TinkoffCard',
                        'requisite_value': '1029384756',
                        'order': expected_order,
                    },
                ],
            },
        ],
    }


async def test_select_store_picker_without_order(
        taxi_eats_picker_supply, mock_eats_core_get_orders, create_picker,
):
    create_picker(
        picker_id='1',
        name='Иванов Иван Иванович',
        phone_id='1',
        places_ids=[1],
        requisite_type='TinkoffCard',
        requisite_value='1234567890',
    )

    await taxi_eats_picker_supply.invalidate_caches(clean_update=False)
    assert mock_eats_core_get_orders.times_called >= 1

    response = await taxi_eats_picker_supply.post(HANDLE, json={'stores': [1]})
    assert response.status == 200

    response_data = response.json()
    assert response_data == {
        'stores': [
            {
                'place_id': 1,
                'pickers': [
                    {
                        'picker_id': '1',
                        'picker_available_until': (
                            DEFAULT_PICKER_AVAILABLE_UNTIL
                        ),
                        'name': 'Иванов Иван Иванович',
                        'phone_id': '1',
                        'requisite_type': 'TinkoffCard',
                        'requisite_value': '1234567890',
                    },
                ],
            },
        ],
    }


async def test_select_store_picker_empty(
        taxi_eats_picker_supply, mock_eats_core_get_orders,
):
    await taxi_eats_picker_supply.invalidate_caches(clean_update=False)
    assert mock_eats_core_get_orders.times_called >= 1

    response = await taxi_eats_picker_supply.post(
        HANDLE, json={'stores': [1, 2, 3]},
    )
    assert response.status == 200

    response_data = response.json()

    assert response_data == {
        'stores': [{'place_id': 1}, {'place_id': 2}, {'place_id': 3}],
    }


@pytest.mark.parametrize('request_body', [{'stores': [1, 2]}])
async def test_select_all_stores_pickers(
        taxi_eats_picker_supply,
        mock_eats_core_get_orders,
        create_picker,
        load_json,
        request_body,
):
    create_picker(
        picker_id='1',
        name='Иванов Пётр Иванович',
        phone_id='1',
        places_ids=[1],
        requisite_type='TinkoffCard',
        requisite_value='1029384756',
    )
    create_picker(
        picker_id='2',
        name='Иванов Иван Иванович',
        phone_id='2',
        places_ids=[2],
        requisite_type='TinkoffCard',
        requisite_value='1234567890',
        available_until='2020-09-20T22:00:00+03:00',
    )

    await taxi_eats_picker_supply.invalidate_caches(clean_update=False)
    assert mock_eats_core_get_orders.times_called >= 1

    response = await taxi_eats_picker_supply.post(HANDLE, json=request_body)
    assert response.status == 200

    response_data = response.json()
    expected_data = load_json('orders_expected_response.json')
    expected_order = format_order(expected_data['orders'][0])

    response_data['stores'].sort(key=lambda store: store['place_id'])
    assert response_data == {
        'stores': [
            {
                'place_id': 1,
                'pickers': [
                    {
                        'picker_id': '1',
                        'picker_available_until': (
                            DEFAULT_PICKER_AVAILABLE_UNTIL
                        ),
                        'name': 'Иванов Пётр Иванович',
                        'phone_id': '1',
                        'requisite_type': 'TinkoffCard',
                        'requisite_value': '1029384756',
                    },
                ],
            },
            {
                'place_id': 2,
                'pickers': [
                    {
                        'picker_id': '2',
                        'picker_available_until': '2020-09-20T19:00:00+00:00',
                        'name': 'Иванов Иван Иванович',
                        'phone_id': '2',
                        'requisite_type': 'TinkoffCard',
                        'requisite_value': '1234567890',
                        'order': expected_order,
                    },
                ],
            },
        ],
    }
