import pytest

INTERNAL_ENDPOINT = 'internal/fleet-orders/orders/v1/order/calculation'
FLEET_ENDPOINT = 'fleet/fleet-orders/orders/v1/order/calculation'

PARK_ID = 'test_park'
WRONG_PARK_ID = 'wrong_park_id'
ORDER_ID = 'order_finished'


def build_headers(**kwargs):
    headers = {
        'Accept-Language': 'ru',
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-UID': '1',
    }
    if kwargs:
        headers.update(**kwargs)
    return headers


def build_params(order_id, **kwargs):
    params = {'id': order_id}
    if kwargs:
        params.update(**kwargs)
    return params


TAXIMETER_BACKEND_FLEET_ORDERS = {
    'FleetOrders_Order_Cost': {'ru': 'Стоимость'},
    'OrderCalculation_OptionByCountSubtitle': {'ru': '%(count)s × %(price)s'},
    'FleetOrders_Option_Booster': {'ru': 'Бустеры'},
    'OrderCalculation_OptionByMinuteSubtitle': {
        'ru': '%(minutes)s мин × %(price)s',
    },
    'FleetOrders_Option_Paid_Waiting': {'ru': 'Платное ожидание в точке A'},
    'OrderCalculation_OptionRentSubtitle': {'ru': '%(hours)s часа'},
    'FleetOrders_Option_Rent': {'ru': 'Почасовая аренда'},
    'FleetOrders_Option_Callcenter': {'ru': 'Наценку за заказ по телефону'},
    'FleetOrders_Bonus': {'ru': 'Бонус'},
    'FleetOrders_Platform_Fees': {'ru': 'Списания'},
    'FleetOrders_Income': {'ru': 'Заработок'},
    'OrderCalculation_CommissionPercent': {
        'ru': '%(percent)s от стоимости заказа',
    },
    'OrderCalculation_CallcenterCommission': {'ru': 'Сервисный сбор'},
    'OrderCalculation_DiscountPayback': {'ru': 'Возмещение скидки'},
    'OrderCalculation_OrderCost': {'ru': 'Цена'},
    'OrderCalculation_HoldedAmount': {'ru': 'Ожидается'},
    'OrderCalculation_Date_Format': {'ru': '%(day)s %(month)s'},
    'OrderCalculation_HoldedAmount_Date': {
        'ru': 'Поступит до вечера %(date)s',
    },
}

FLEET_ORDERS_ORDER_DETAILS = {
    'paid_options': [
        {
            'localization': {
                'key': 'FleetOrders_Option_Booster',
                'keyset': 'taximeter_backend_fleet_orders',
            },
            'path': 'meta.driver',
            'price': 'req:childchair_v2.infant:price',
            'option_details': {
                'per_unit': 'req:childchair_v2.infant:per_unit',
                'count': 'req:childchair_v2.infant:count',
                'included': 'req:childchair_v2.infant:included',
            },
        },
        {
            'localization': {
                'key': 'FleetOrders_Option_Paid_Waiting',
                'keyset': 'taximeter_backend_fleet_orders',
            },
            'path': 'meta.driver',
            'price': 'waiting_delta',
            'option_details': {
                'per_unit': 'waiting_per_unit',
                'seconds': 'waiting_count',
            },
        },
        {
            'localization': {
                'key': 'FleetOrders_Option_Rent',
                'keyset': 'taximeter_backend_fleet_orders',
            },
            'path': 'meta.driver',
            'price': 'req:hourly_rental.2_hours:price',
            'option_details': {'hours_count': 2},
        },
        {
            'localization': {
                'key': 'FleetOrders_Option_Callcenter',
                'keyset': 'taximeter_backend_fleet_orders',
            },
            'path': 'meta.user',
            'price': 'callcenter_delta',
        },
    ],
    'payment_group_ids': [
        'cash_collected',
        'platform_card',
        'platform_corporate',
        'platform_promotion',
    ],
    'blocks': {
        'fleet': [
            {
                'localization': {
                    'key': 'FleetOrders_Order_Cost',
                    'keyset': 'taximeter_backend_fleet_orders',
                },
                'show_if_zero': True,
                'type': 'order_cost',
            },
            {
                'localization': {
                    'key': 'FleetOrders_Bonus',
                    'keyset': 'taximeter_backend_fleet_orders',
                },
                'type': 'default',
                'detalization': False,
                'group_ids': ['platform_bonus'],
                'hold_categories_ids': ['platform_bonus'],
            },
            {
                'localization': {
                    'key': 'FleetOrders_Platform_Fees',
                    'keyset': 'taximeter_backend_fleet_orders',
                },
                'type': 'default',
                'show_percentage': True,
                'show_callcenter_percentage': False,
                'group_ids': ['platform_fees', 'platform_other'],
            },
            {
                'localization': {
                    'key': 'FleetOrders_Income',
                    'keyset': 'taximeter_backend_fleet_orders',
                },
                'show_if_zero': True,
                'type': 'driver_income',
            },
        ],
        'driver_money': [],
    },
}


@pytest.mark.parametrize(
    'endpoint, params, headers',
    [
        (
            INTERNAL_ENDPOINT,
            {'park_id': WRONG_PARK_ID, 'consumer': 'fleet'},
            {},
        ),
        (FLEET_ENDPOINT, {}, {'X-Park-ID': WRONG_PARK_ID}),
    ],
)
async def test_park_not_found(
        taxi_fleet_orders, mock_fleet_parks, endpoint, params, headers,
):
    mock_fleet_parks.set_data(park_id=WRONG_PARK_ID, is_park_found=False)

    response = await taxi_fleet_orders.get(
        endpoint,
        params=build_params(ORDER_ID, **params),
        headers=build_headers(**headers),
    )

    assert mock_fleet_parks.has_mock_parks_calls
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'Park not found'}


@pytest.mark.parametrize(
    'endpoint, params, headers',
    [
        (INTERNAL_ENDPOINT, {'park_id': PARK_ID, 'consumer': 'fleet'}, {}),
        (FLEET_ENDPOINT, {}, {'X-Park-ID': PARK_ID}),
    ],
)
async def test_order_not_found(
        taxi_fleet_orders,
        mock_fleet_parks,
        mock_order_archive,
        endpoint,
        params,
        headers,
):
    mock_fleet_parks.set_data(park_id=PARK_ID)
    mock_order_archive.set_data(
        order_id=ORDER_ID, park_id=PARK_ID, is_order_found=False,
    )

    response = await taxi_fleet_orders.get(
        endpoint,
        params=build_params(ORDER_ID, **params),
        headers=build_headers(**headers),
    )

    assert mock_fleet_parks.has_mock_parks_calls
    assert mock_order_archive.has_mock_calls
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'Order not found'}


@pytest.mark.now('2022-07-02T00:00:00+0300')
@pytest.mark.parametrize(
    'order_id',
    [
        ORDER_ID,
        'order_cancelled',
        'order_cancelled_2',
        'order_driving',
        'order_corp',
    ],
)
@pytest.mark.parametrize(
    'endpoint, params, headers',
    [
        (INTERNAL_ENDPOINT, {'park_id': PARK_ID, 'consumer': 'fleet'}, {}),
        (FLEET_ENDPOINT, {}, {'X-Park-ID': PARK_ID}),
    ],
)
@pytest.mark.translations(
    tariff={'currency_sign.rub': {'ru': '₽'}},
    notify={'helpers.month_7_part': {'ru': 'июля'}},
    taximeter_backend_fleet_orders=TAXIMETER_BACKEND_FLEET_ORDERS,
)
@pytest.mark.config(
    FLEET_ORDERS_ORDER_DETAILS=FLEET_ORDERS_ORDER_DETAILS,
    MAX_DISCOUNT_PAYBACK_CURRENCY={'__default__': 2000},
    TAXIMETER_CALLCENTER_URLS={
        'rus': 'https://driver.yandex/ru-ru/phone-comission',
    },
)
async def test_ok(
        taxi_fleet_orders,
        mock_fleet_parks,
        mock_order_archive,
        mockserver,
        load_json,
        order_id,
        endpoint,
        params,
        headers,
):
    @mockserver.json_handler('/territories/v1/countries/retrieve')
    async def _v1_countries_retrieve(request):
        assert request.json == {'_id': 'rus'}
        return {'_id': 'rus_id', 'country': 'rus', 'currency': 'RUB'}

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/transactions'
        '/categories/list/by-platform',
    )
    async def _list_transaction_categories(request):
        assert request.json == {'query': {'park': {'id': PARK_ID}}}
        return load_json('fta_items_response.json')

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/orders/'
        'transactions/with-antifraud/list',
    )
    def _v1_parks_orders_transactions_list(request):
        assert request.json['query']['park']['id'] == PARK_ID
        assert request.json['query']['park']['order']['ids'] == [order_id]
        return load_json('fta_response.json')[order_id]

    mock_fleet_parks.set_data(park_id=PARK_ID)
    mock_order_archive.set_data(
        order_id=order_id,
        park_id=PARK_ID,
        response=load_json('order_archive_response.json')[order_id],
    )

    response = await taxi_fleet_orders.get(
        endpoint,
        params=build_params(order_id, **params),
        headers=build_headers(**headers),
    )

    assert _v1_countries_retrieve.has_calls
    assert _v1_parks_orders_transactions_list.has_calls
    assert _list_transaction_categories.has_calls
    assert mock_fleet_parks.has_mock_parks_calls
    assert mock_order_archive.has_mock_calls

    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')[order_id]
