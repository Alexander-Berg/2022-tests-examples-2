from tests_grocery_dispatch import configs
from tests_grocery_dispatch import constants as const


@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_schedule_dummy(
        taxi_grocery_dispatch, test_dummy_dispatch_cfg, testpoint,
):
    depot_id = const.DEPOT_ID

    order = {
        'order_id': 'order_id',
        'short_order_id': 'short_order_id_1',
        'depot_id': depot_id,
        'location': {'lon': 35.5, 'lat': 55.6},
        'zone_type': 'pedestrian',
        'created_at': '2020-10-05T16:28:00+00:00',
        'max_eta': 900,
        'items': [
            {
                'item_id': 'item_id_1',
                'title': 'some product',
                'price': '12.99',
                'currency': 'RUB',
                'quantity': '1',
                'item_tags': [],
            },
        ],
        'user_locale': 'ru',
        'personal_phone_id': 'personal_phone_id_1',
    }

    @testpoint('test_dispatch_schedule')
    def check_scheduling_data(data):
        data_order = data['order']
        assert data_order.pop('created') == order['created_at']
        assert data_order.pop('location') == [
            order['location']['lon'],
            order['location']['lat'],
        ]
        for k in data_order:
            assert data_order[k] == order[k]

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', json=order,
    )
    assert response.status_code == 200
    assert check_scheduling_data.times_called == 1

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', json=order,
    )
    assert response.status_code == 200
    assert check_scheduling_data.times_called == 1
