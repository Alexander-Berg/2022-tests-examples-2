from tests_fleet_orders_manager import common

ENDPOINT = 'fleet/fleet-orders-manager/v1/active-orders/search'
REQUEST_BODY = {'phone_pd_id': 'id_+7123'}

OK_INT_API_RESPONSE = {
    'orders': [
        {
            'cancel_disabled': False,
            'cost_message_details': {'cost_breakdown': []},
            'created': '2021-04-29T07:38:34.462+0000',
            'orderid': '8f3f6852843e2518a758834f67814930',
            'payment': {'type': 'cash'},
            'request': {
                'class': 'econom',
                'comment': '',
                'due': '2021-04-29T07:48:47.487+0000',
                'requirements': {},
                'route': [
                    {
                        'country': 'Оман',
                        'fullname': 'AAA',
                        'geopoint': [58, 23],
                        'short_text': 'Маскат 1',
                    },
                    {
                        'country': 'Оман',
                        'fullname': 'BBB',
                        'geopoint': [58.5, 23],
                        'short_text': 'Маскат 2',
                    },
                ],
            },
            'status': 'search',
            'userid': 'b5cfdff704264db6bcc5e513d631d4a4',
        },
        {
            'cancel_disabled': False,
            'cost_message_details': {'cost_breakdown': []},
            'created': '2021-04-29T07:38:34.462+0000',
            'orderid': 'aaaaaa_order_id',
            'payment': {'type': 'cash'},
            'request': {
                'class': 'econom',
                'comment': '',
                'due': '2021-04-29T07:48:47.487+0000',
                'requirements': {},
                'route': [
                    {
                        'country': 'Оман',
                        'fullname': 'AAA',
                        'geopoint': [58, 23],
                        'short_text': 'Маскат 1',
                    },
                    {
                        'country': 'Оман',
                        'fullname': 'BBB',
                        'geopoint': [58.5, 23],
                        'short_text': 'Маскат 2',
                    },
                ],
            },
            'status': 'cancelled',
            'userid': 'b5cfdff704264db6bcc5e513d631d4a4',
        },
    ],
}


async def test_ok(
        mockserver,
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _mock_orders_search(request):
        return OK_INT_API_RESPONSE

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=REQUEST_BODY, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        'orders': [
            {
                'class_id': 'econom',
                'created_at': '2021-04-29T07:38:34.462+00:00',
                'order_id': '8f3f6852843e2518a758834f67814930',
                'route': [
                    {
                        'geopoint': [58.0, 23.0],
                        'short_address_description': 'Маскат 1',
                    },
                    {
                        'geopoint': [58.5, 23.0],
                        'short_address_description': 'Маскат 2',
                    },
                ],
            },
        ],
    }

    assert _mock_orders_search.times_called == 1
    orders_search_request = _mock_orders_search.next_call()['request']
    assert orders_search_request.json == {
        'user': {
            'personal_phone_id': 'id_+7123',
            'user_id': 'user_id_id_+7123',
        },
    }
    assert (
        orders_search_request.headers['User-Agent']
        == 'whitelabel/superweb/label_id'
    )
    assert orders_search_request.headers['Accept-Language'] == 'de'
