import pytest

DEFAULT_PICKER_AVAILABLE_UNTIL = '2020-09-20T20:00:00+00:00'


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


@pytest.mark.parametrize('handle', ['/api/v1/select-store-pickers'])
async def test_select_store_picker_with_order(
        taxi_eats_picker_supply,
        mock_eats_core_get_orders,
        create_picker,
        load_json,
        handle,
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

    response = await taxi_eats_picker_supply.post(handle, json={'stores': [1]})
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
                        'order': expected_order,
                    },
                ],
            },
        ],
    }


@pytest.mark.parametrize('handle', ['/api/v1/select-store-pickers'])
async def test_select_store_picker_without_order(
        taxi_eats_picker_supply,
        mock_eats_core_get_orders,
        create_picker,
        handle,
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

    response = await taxi_eats_picker_supply.post(handle, json={'stores': [1]})
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
                    },
                ],
            },
        ],
    }


@pytest.mark.parametrize('handle', ['/api/v1/select-store-pickers'])
async def test_select_store_picker_empty(
        taxi_eats_picker_supply, mock_eats_core_get_orders, handle,
):
    await taxi_eats_picker_supply.invalidate_caches(clean_update=False)
    assert mock_eats_core_get_orders.times_called >= 1

    response = await taxi_eats_picker_supply.post(
        handle, json={'stores': [1, 2, 3]},
    )
    assert response.status == 200

    response_data = response.json()

    assert response_data == {
        'stores': [{'place_id': 1}, {'place_id': 2}, {'place_id': 3}],
    }


@pytest.mark.parametrize('handle', ['/api/v1/select-store-pickers'])
@pytest.mark.parametrize('request_body', [{}, {'stores': []}])
async def test_select_all_stores_pickers(
        taxi_eats_picker_supply,
        mock_eats_core_get_orders,
        create_picker,
        load_json,
        request_body,
        handle,
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

    response = await taxi_eats_picker_supply.post(handle, json=request_body)
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
                    },
                ],
            },
            {
                'place_id': 2,
                'pickers': [
                    {
                        'picker_id': '2',
                        'picker_available_until': '2020-09-20T19:00:00+00:00',
                        'order': expected_order,
                    },
                ],
            },
        ],
    }
