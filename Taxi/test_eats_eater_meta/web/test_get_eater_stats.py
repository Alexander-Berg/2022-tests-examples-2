import datetime

import pytest

DEFAULT_ORDERS_STATS_DATA = (
    {
        'data': [
            {
                'identity': {'type': 'eater_id', 'value': '152767624'},
                'counters': [
                    {
                        'properties': [
                            {'name': 'business_type', 'value': 'retail'},
                            {'name': 'brand_id', 'value': '1'},
                        ],
                        'value': 1,
                        'first_order_at': '2019-12-11T09:00:00+0000',
                        'last_order_at': '2019-12-11T09:00:00+0000',
                    },
                    {
                        'properties': [
                            {'name': 'business_type', 'value': 'restaurant'},
                            {'name': 'brand_id', 'value': '1'},
                        ],
                        'value': 1,
                        'first_order_at': '2019-12-11T09:00:00+0000',
                        'last_order_at': '2019-12-11T09:00:00+0000',
                    },
                ],
            },
        ],
    },
)

ORDER_STATS_BAD_BRAND = (
    {
        'data': [
            {
                'identity': {'type': 'eater_id', 'value': '152767624'},
                'counters': [
                    {
                        'properties': [
                            {'name': 'business_type', 'value': 'retail'},
                            {'name': 'brand_id', 'value': '123'},
                        ],
                        'value': 1,
                        'first_order_at': '2019-12-11T09:00:00+0000',
                        'last_order_at': '2019-12-11T09:00:00+0000',
                    },
                ],
            },
        ],
    },
)

ORDERS_STATS_DATA_STARTER = (
    {
        'data': [
            {
                'identity': {'type': 'eater_id', 'value': '152767624'},
                'counters': [],
            },
        ],
    },
)

ORDERS_STATS_DATA_PURCHASE = (
    {
        'data': [
            {
                'identity': {'type': 'eater_id', 'value': '152767624'},
                'counters': [
                    {
                        'properties': [
                            {'name': 'business_type', 'value': 'retail'},
                            {'name': 'brand_id', 'value': '1'},
                        ],
                        'value': 1,
                        'first_order_at': '2019-12-11T09:00:00+0000',
                        'last_order_at': datetime.datetime.now(
                            datetime.timezone.utc,
                        ).isoformat(),
                    },
                    {
                        'properties': [
                            {'name': 'business_type', 'value': 'restaurant'},
                            {'name': 'brand_id', 'value': '1'},
                        ],
                        'value': 1,
                        'first_order_at': '2019-12-11T09:00:00+0000',
                        'last_order_at': '2019-12-11T09:00:00+0000',
                    },
                ],
            },
        ],
    },
)

ORDERS_STATS_DATA_REACTIVATE = (
    {
        'data': [
            {
                'identity': {'type': 'eater_id', 'value': '152767624'},
                'counters': [
                    {
                        'properties': [
                            {'name': 'business_type', 'value': 'retail'},
                            {'name': 'brand_id', 'value': '1'},
                        ],
                        'value': 12,
                        'first_order_at': '2019-12-11T09:00:00+0000',
                        'last_order_at': '2019-12-11T09:00:00+0000',
                    },
                    {
                        'properties': [
                            {'name': 'business_type', 'value': 'restaurant'},
                            {'name': 'brand_id', 'value': '1'},
                        ],
                        'value': 1,
                        'first_order_at': '2019-12-11T09:00:00+0000',
                        'last_order_at': '2019-12-11T09:00:00+0000',
                    },
                ],
            },
        ],
    },
)

ORDERS_STATS_DATA_DIFF_BUSSINESS = (
    {
        'data': [
            {
                'identity': {'type': 'eater_id', 'value': '152767624'},
                'counters': [
                    {
                        'properties': [
                            {'name': 'business_type', 'value': 'retail'},
                            {'name': 'brand_id', 'value': '1'},
                        ],
                        'value': 6,
                        'first_order_at': '2019-12-11T09:00:00+0000',
                        'last_order_at': datetime.datetime.now(
                            datetime.timezone.utc,
                        ).isoformat(),
                    },
                    {
                        'properties': [
                            {'name': 'business_type', 'value': 'shop'},
                            {'name': 'brand_id', 'value': '1'},
                        ],
                        'value': 6,
                        'first_order_at': '2019-12-11T09:00:00+0000',
                        'last_order_at': '2019-12-11T09:00:00+0000',
                    },
                ],
            },
        ],
    },
)


@pytest.mark.parametrize(
    [
        'header',
        'eats_order_stats_response_status_code',
        'eats_order_stats_response_body',
        'expected_response',
        'expected_mock_times_called',
    ],
    [
        [  # id = user with orders
            'user_id=152767624, personal_phone_id=21788213',
            200,
            *DEFAULT_ORDERS_STATS_DATA,
            {
                'has_retail': True,
                'has_restaurants': True,
                'has_lavka': False,
                'has_gas_station': False,
            },
            1,
        ],
        [  # id = partner user with orders
            'personal_phone_id=21788213, partner_user_id=152767624',
            200,
            *DEFAULT_ORDERS_STATS_DATA,
            {
                'has_retail': True,
                'has_restaurants': True,
                'has_lavka': False,
                'has_gas_station': False,
            },
            1,
        ],
        [  # id = empty counters
            'user_id=152767624',
            200,
            {
                'data': [
                    {
                        'identity': {'type': 'eater_id', 'value': '152767624'},
                        'counters': [],
                    },
                ],
            },
            {
                'has_retail': False,
                'has_restaurants': False,
                'has_lavka': False,
                'has_gas_station': False,
            },
            1,
        ],
        [  # id = without user id
            'personal_phone_id=21788213',
            200,
            {
                'data': [
                    {
                        'identity': {'type': 'eater_id', 'value': '152767624'},
                        'counters': [],
                    },
                ],
            },
            {
                'has_retail': False,
                'has_restaurants': False,
                'has_lavka': False,
                'has_gas_station': False,
            },
            0,
        ],
        [  # id = 400 response
            'user_id=152767624',
            400,
            {},
            {
                'has_retail': False,
                'has_restaurants': False,
                'has_lavka': False,
                'has_gas_station': False,
            },
            1,
        ],
        [  # id = 429 response
            'user_id=152767624',
            429,
            {},
            {
                'has_retail': False,
                'has_restaurants': False,
                'has_lavka': False,
                'has_gas_station': False,
            },
            1,
        ],
        [  # id = 500 response
            'user_id=152767624',
            500,
            {},
            {
                'has_retail': False,
                'has_restaurants': False,
                'has_lavka': False,
                'has_gas_station': False,
            },
            1,
        ],
    ],
    ids=[
        'user with orders',
        'partner user with orders',
        'empty counters',
        'without user id',
        '400 response',
        '429 response',
        '500 response',
    ],
)
async def test_get_eater_stats(
        # ---- fixtures ----
        mockserver,
        taxi_eats_eater_meta_web,
        # ---- parameters ----
        header,
        eats_order_stats_response_status_code,
        eats_order_stats_response_body,
        expected_response,
        expected_mock_times_called,
):
    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _mock_eats_orders_stats_(request):
        return mockserver.make_response(
            status=eats_order_stats_response_status_code,
            json=eats_order_stats_response_body,
        )

    response = await taxi_eats_eater_meta_web.get(
        '/eats/v1/eats-eater-meta/v1/order-stats',
        headers={'X-Eats-User': header},
    )
    assert response.status == 200
    assert _mock_eats_orders_stats_.times_called == expected_mock_times_called

    data = await response.json()
    assert data == expected_response


@pytest.mark.config(EDA_DELIVERY_PRICE_PROMO={'bad_native_brands': ['123']})
@pytest.mark.parametrize(
    [
        'header',
        'eats_order_stats_response_status_code',
        'eats_order_stats_response_body',
        'expected_response',
        'expected_mock_times_called',
    ],
    [
        [  # id = user with orders
            'user_id=152767624, personal_phone_id=21788213',
            200,
            *DEFAULT_ORDERS_STATS_DATA,
            {
                'info': [
                    {'type': 'fp', 'value': False},
                    {'type': 'rp', 'value': True},
                    {'type': 'rsp', 'value': True},
                    {'type': 'cp', 'value': True},
                    {'type': 'lr', 'value': False},
                    {'type': 'cr', 'value': False},
                    {'type': 'fsp', 'value': False},
                ],
            },
            1,
        ],
        [  # id = user starter
            'user_id=152767624, personal_phone_id=21788213',
            200,
            *ORDERS_STATS_DATA_STARTER,
            {
                'info': [
                    {'type': 'fp', 'value': True},
                    {'type': 'rp', 'value': False},
                    {'type': 'rsp', 'value': False},
                    {'type': 'cp', 'value': True},
                    {'type': 'lr', 'value': False},
                    {'type': 'cr', 'value': False},
                    {'type': 'fsp', 'value': True},
                ],
            },
            1,
        ],
        [  # id = user purchase
            'user_id=152767624, personal_phone_id=21788213',
            200,
            *ORDERS_STATS_DATA_PURCHASE,
            {
                'info': [
                    {'type': 'fp', 'value': False},
                    {'type': 'rp', 'value': True},
                    {'type': 'rsp', 'value': True},
                    {'type': 'cp', 'value': False},
                    {'type': 'lr', 'value': False},
                    {'type': 'cr', 'value': False},
                    {'type': 'fsp', 'value': False},
                ],
            },
            1,
        ],
        [  # id = user reactivate
            'user_id=152767624, personal_phone_id=21788213',
            200,
            *ORDERS_STATS_DATA_REACTIVATE,
            {
                'info': [
                    {'type': 'fp', 'value': False},
                    {'type': 'rp', 'value': True},
                    {'type': 'rsp', 'value': True},
                    {'type': 'cp', 'value': True},
                    {'type': 'lr', 'value': True},
                    {'type': 'cr', 'value': True},
                    {'type': 'fsp', 'value': False},
                ],
            },
            1,
        ],
        [  # id = partner user with orders
            'personal_phone_id=21788213, partner_user_id=152767624',
            200,
            *DEFAULT_ORDERS_STATS_DATA,
            {
                'info': [
                    {'type': 'fp', 'value': False},
                    {'type': 'rp', 'value': True},
                    {'type': 'rsp', 'value': True},
                    {'type': 'cp', 'value': True},
                    {'type': 'lr', 'value': False},
                    {'type': 'cr', 'value': False},
                    {'type': 'fsp', 'value': False},
                ],
            },
            1,
        ],
        [  # id = empty counters
            'user_id=152767624',
            200,
            {
                'data': [
                    {
                        'identity': {'type': 'eater_id', 'value': '152767624'},
                        'counters': [],
                    },
                ],
            },
            {
                'info': [
                    {'type': 'fp', 'value': True},
                    {'type': 'rp', 'value': False},
                    {'type': 'rsp', 'value': False},
                    {'type': 'cp', 'value': True},
                    {'type': 'lr', 'value': False},
                    {'type': 'cr', 'value': False},
                    {'type': 'fsp', 'value': True},
                ],
            },
            1,
        ],
        [  # id = without user id
            'personal_phone_id=21788213',
            200,
            {
                'data': [
                    {
                        'identity': {'type': 'eater_id', 'value': '152767624'},
                        'counters': [],
                    },
                ],
            },
            {
                'info': [
                    {'type': 'fp', 'value': True},
                    {'type': 'rp', 'value': False},
                    {'type': 'rsp', 'value': False},
                    {'type': 'cp', 'value': True},
                    {'type': 'lr', 'value': False},
                    {'type': 'cr', 'value': False},
                    {'type': 'fsp', 'value': True},
                ],
            },
            0,
        ],
        [  # id = 400 response
            'user_id=152767624',
            400,
            {},
            {
                'info': [
                    {'type': 'fp', 'value': True},
                    {'type': 'rp', 'value': False},
                    {'type': 'rsp', 'value': False},
                    {'type': 'cp', 'value': True},
                    {'type': 'lr', 'value': False},
                    {'type': 'cr', 'value': False},
                    {'type': 'fsp', 'value': True},
                ],
            },
            1,
        ],
        [  # id = 429 response
            'user_id=152767624',
            429,
            {},
            {
                'info': [
                    {'type': 'fp', 'value': True},
                    {'type': 'rp', 'value': False},
                    {'type': 'rsp', 'value': False},
                    {'type': 'cp', 'value': True},
                    {'type': 'lr', 'value': False},
                    {'type': 'cr', 'value': False},
                    {'type': 'fsp', 'value': True},
                ],
            },
            1,
        ],
        [  # id = 500 response
            'user_id=152767624',
            500,
            {},
            {
                'info': [
                    {'type': 'fp', 'value': True},
                    {'type': 'rp', 'value': False},
                    {'type': 'rsp', 'value': False},
                    {'type': 'cp', 'value': True},
                    {'type': 'lr', 'value': False},
                    {'type': 'cr', 'value': False},
                    {'type': 'fsp', 'value': True},
                ],
            },
            1,
        ],
        [  # id = bad brand_id
            'user_id=152767624, personal_phone_id=21788213',
            200,
            *ORDER_STATS_BAD_BRAND,
            {
                'info': [
                    {'type': 'fp', 'value': True},
                    {'type': 'rp', 'value': False},
                    {'type': 'rsp', 'value': False},
                    {'type': 'cp', 'value': True},
                    {'type': 'lr', 'value': False},
                    {'type': 'cr', 'value': False},
                    {'type': 'fsp', 'value': True},
                ],
            },
            1,
        ],
    ],
    ids=[
        'user with orders',
        'user starter',
        'user purchase',
        'user reactivate',
        'partner user with orders',
        'empty counters',
        'without user id',
        '400 response',
        '429 response',
        '500 response',
        'bad brand_id',
    ],
)
async def test_get_eater_stats_in_detail(
        # ---- fixtures ----
        mockserver,
        taxi_eats_eater_meta_web,
        # ---- parameters ----
        header,
        eats_order_stats_response_status_code,
        eats_order_stats_response_body,
        expected_response,
        expected_mock_times_called,
):
    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _mock_eats_orders_stats_(request):
        return mockserver.make_response(
            status=eats_order_stats_response_status_code,
            json=eats_order_stats_response_body,
        )

    response = await taxi_eats_eater_meta_web.get(
        '/eats/v1/eats-eater-meta/v1/next-order-flags?business_type=retail',
        headers={'X-Eats-User': header},
    )
    assert response.status == 200
    assert _mock_eats_orders_stats_.times_called == expected_mock_times_called

    data = await response.json()
    assert data == expected_response


@pytest.mark.parametrize(
    [
        'header',
        'eats_order_stats_response_status_code',
        'eats_order_stats_response_body',
        'expected_mock_times_called',
    ],
    [
        [
            'user_id=152767624, personal_phone_id=21788213',
            200,
            *ORDERS_STATS_DATA_DIFF_BUSSINESS,
            1,
        ],
    ],
)
@pytest.mark.parametrize(
    'url,ans',
    [
        (
            'restaurant',
            {
                'info': [
                    {'type': 'fp', 'value': False},
                    {'type': 'cp', 'value': False},
                    {'type': 'rp', 'value': True},
                    {'type': 'rrp', 'value': False},
                    {'type': 'lr', 'value': False},
                    {'type': 'cr', 'value': False},
                    {'type': 'frp', 'value': True},
                ],
            },
        ),
        (
            'retail',
            {
                'info': [
                    {'type': 'fp', 'value': False},
                    {'type': 'rp', 'value': True},
                    {'type': 'rsp', 'value': True},
                    {'type': 'cp', 'value': False},
                    {'type': 'lr', 'value': False},
                    {'type': 'cr', 'value': False},
                    {'type': 'fsp', 'value': False},
                ],
            },
        ),
    ],
)
async def test_get_eater_stats_in_detail_diff_bussiness_type(
        # ---- fixtures ----
        mockserver,
        taxi_eats_eater_meta_web,
        # ---- parameters ----
        header,
        eats_order_stats_response_status_code,
        eats_order_stats_response_body,
        expected_mock_times_called,
        url,
        ans,
):
    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _mock_eats_orders_stats_(request):
        return mockserver.make_response(
            status=eats_order_stats_response_status_code,
            json=eats_order_stats_response_body,
        )

    response = await taxi_eats_eater_meta_web.get(
        '/eats/v1/eats-eater-meta/v1/next-order-flags?business_type='
        + str(url),
        headers={'X-Eats-User': header},
    )
    assert response.status == 200
    assert _mock_eats_orders_stats_.times_called == expected_mock_times_called

    data = await response.json()
    assert data['info'] == ans['info']
