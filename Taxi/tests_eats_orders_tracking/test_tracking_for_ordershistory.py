import pytest

URL = '/internal/eats-orders-tracking/v1/tracking-for-ordershistory'
MOCK_DATETIME = '2020-10-28T18:20:00.00+00:00'
FRONT_DEEPLINK = 'eda.yandex://tracking/order_nr={}'
FULL_RESPONSE = {
    'orders': [
        {
            'order_nr': '000000-000000',
            'ordershistory_widget': {
                'deeplink': 'eda.yandex://tracking/order_nr=000000-000000',
                'title': 'short_title',
                'subtitle': 'short_title_for_ordershistory',
                'icons': [
                    {
                        'status': 'finished',
                        'uri': 'https://eda.yandex/s3/tracked-order/check.png',
                    },
                    {
                        'status': 'in_progress',
                        'uri': (
                            'https://eda.yandex/s3/tracked-order/cyclist.png'
                        ),
                    },
                ],
            },
        },
        {
            'order_nr': '000000-000002',
            'ordershistory_widget': {
                'deeplink': 'eda.yandex://tracking/order_nr=000000-000002',
                'title': 'short_title',
                'subtitle': 'short_title_for_ordershistory',
                'icons': [
                    {
                        'status': 'finished',
                        'uri': 'https://eda.yandex/s3/tracked-order/check.png',
                    },
                    {
                        'status': 'in_progress',
                        'uri': (
                            'https://eda.yandex/s3/tracked-order/cyclist.png'
                        ),
                    },
                ],
            },
        },
    ],
}


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.config(
    EATS_ORDERS_TRACKING_FRONT_DEEPLINK={
        'deeplink_for_order': FRONT_DEEPLINK,
        'deeplink': 'some_deeplink',
    },
)
@pytest.mark.parametrize(
    'headers',
    [
        pytest.param({'X-Eats-User': 'user_id=eater1'}, id='native'),
        pytest.param({'X-Eats-User': 'partner_user_id=eater1'}, id='partner'),
        pytest.param({'X-Eats-User': ''}, id='empty_in_header'),
    ],
)
@pytest.mark.parametrize(
    'query, expected_response, expected_status_code',
    [
        ({'eater_id': 'eater1'}, FULL_RESPONSE, 200),  # exist_orders_eater_id
        (
            {'eater_id': 'eater_not_found'},
            {'orders': []},
            200,
        ),  # not_exist_orders_eater
        (
            {},
            {'code': '400', 'message': 'Missing eater_id in query'},
            400,
        ),  # empty_eater_id
        (
            {},
            {'code': '400', 'message': 'Missing eater_id in query'},
            400,
        ),  # empty_query
    ],
    ids=[
        'exist_orders_eater_id',
        'not_exist_orders_eater',
        'empty_eater_id',
        'empty_query',
    ],
)
async def test_get_widgets(
        taxi_eats_orders_tracking,
        headers,
        query,
        expected_response,
        expected_status_code,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        URL, headers=headers, params=query,
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_response
