import pytest

# pylint: disable=unused-variable

CATALOG_RESPONSE = {
    'slug': {
        'place': {
            'name': 'Тестовое заведение',
            'brand': {'id': 1, 'slug': 'test'},
            'business': 'restaurant',
            'location': {
                'country': {'id': 35, 'code': 'RU'},
                'address': {'short': 'Новодмитровская улица, 2к6'},
                'position': [37.5916, 55.8129],
                'region_id': 1,
            },
            'currency': {'code': 'USD', 'sign': '$'},
            'assembly_cost': '123',
            'delivery': {
                'type': 'native',
                'thresholds': [
                    {'order_price': '0', 'delivery_cost': '139'},
                    {'order_price': '500', 'delivery_cost': '89'},
                    {'order_price': '2000', 'delivery_cost': '0'},
                ],
                'estimated_duration': {'min': 10, 'max': 20},
                'courier_type': 'pedestrian',
                'available_courier_types': [
                    {'priority': 1, 'type': 'pedestrian'},
                ],
            },
            'available_shipping_types': (['pickup', 'delivery']),
            'available_payment_methods': ['googlePay', 'applePay', 'payture'],
            'constraints': {
                'maximum_order_price': {'value': '500', 'text': '500 $'},
                'maximum_order_weight': {'value': 12.0, 'text': '12 кг'},
            },
            'surge': {
                'title': 'Повышенный спрос',
                'message': (
                    'Заказов сейчас очень много — чтобы еда приехала в срок, '
                    'стоимость доставки временно увеличена'
                ),
                'description': 'Повышенный спрос',
                'delivery_fee': '100',
            },
            'timings': {
                'avg_preparation': 12,
                'extra_preparation': 1,
                'fixed': 20,
                'preparation': 0,
            },
            'is_available': True,
            'is_marketplace': False,
            'is_ultima': False,
        },
        'timepicker': [[], []],
    },
    'unavailable_place_slug': {
        'place': {
            'name': 'Тестовое заведение',
            'brand': {'id': 1, 'slug': 'test'},
            'business': 'restaurant',
            'location': {
                'country': {'id': 35, 'code': 'RU'},
                'address': {'short': 'Новодмитровская улица, 2к6'},
                'position': [37.5916, 55.8129],
                'region_id': 1,
            },
            'currency': {'code': 'USD', 'sign': '$'},
            'assembly_cost': '123',
            'delivery': {
                'type': 'native',
                'thresholds': [
                    {'order_price': '0', 'delivery_cost': '139'},
                    {'order_price': '500', 'delivery_cost': '89'},
                    {'order_price': '2000', 'delivery_cost': '0'},
                ],
                'estimated_duration': {'min': 10, 'max': 20},
                'courier_type': 'pedestrian',
                'available_courier_types': [
                    {'priority': 1, 'type': 'pedestrian'},
                ],
            },
            'available_shipping_types': (['pickup', 'delivery']),
            'available_payment_methods': ['googlePay', 'applePay', 'payture'],
            'constraints': {
                'maximum_order_price': {'value': '500', 'text': '500 $'},
                'maximum_order_weight': {'value': 12.0, 'text': '12 кг'},
            },
            'surge': {
                'title': 'Повышенный спрос',
                'message': (
                    'Заказов сейчас очень много — чтобы еда приехала в срок, '
                    'стоимость доставки временно увеличена'
                ),
                'description': 'Повышенный спрос',
                'delivery_fee': '100',
            },
            'timings': {
                'avg_preparation': 12,
                'extra_preparation': 1,
                'fixed': 20,
                'preparation': 0,
            },
            'is_available': False,
            'is_marketplace': False,
            'is_ultima': False,
        },
        'timepicker': [[], []],
    },
}

OFFERS_RESPONSE = {
    'session-id-2': {
        'session_id': 'session-id-2',
        'expiration_time': '2019-10-31T11:20:00+00:00',
        'request_time': '2019-10-31T11:00:00+00:00',
        'prolong_count': 1,
        'parameters': {
            'location': [1, 1],
            'delivery_time': '2019-10-31T12:00:00+00:00',
        },
        'payload': {'extra-data': 'value'},
        'status': 'NO_CHANGES',
    },
    'session-id-3': {
        'session_id': 'session-id-3',
        'expiration_time': '2019-10-31T11:20:00+00:00',
        'request_time': '2019-10-31T11:00:00+00:00',
        'prolong_count': 1,
        'parameters': {
            'location': [1, 1],
            'delivery_time': '2019-10-31T12:00:00+00:00',
        },
        'payload': {'extra-data': 'value'},
        'status': 'NO_CHANGES',
    },
    'session-id-5': {
        'session_id': 'session-id-5',
        'expiration_time': '2020-01-01T00:00:01+00:00',
        'request_time': '2019-10-31T11:00:00+00:00',
        'prolong_count': 1,
        'parameters': {
            'location': [1, 1],
            'delivery_time': '2019-10-31T12:00:00+00:00',
        },
        'payload': {'extra-data': 'value'},
        'status': 'NO_CHANGES',
    },
    'session-id-7': {
        'session_id': 'session-id-1',
        'expiration_time': '2019-10-31T11:20:00+00:00',
        'request_time': '2019-10-31T11:00:00+00:00',
        'prolong_count': 1,
        'parameters': {
            'location': [1, 1],
            'delivery_time': '2019-10-31T12:00:00+00:00',
        },
        'payload': {'extra-data': 'value'},
        'status': 'NO_CHANGES',
    },
}

ORDERSHISTORY_RESPONSE = {
    1000: {
        'orders': [
            {
                'order_id': '1',
                'status': 'delivered',
                'created_at': '2019-12-31T23:58:59+00:00',
                'source': 'eda',
                'delivery_location': {'lat': 1.0, 'lon': 1.0},
                'total_amount': '123.45',
                'is_asap': True,
                'place_id': 40000,
            },
        ],
    },
    1001: {
        'orders': [
            {
                'order_id': '2',
                'status': 'delivered',
                'created_at': '2019-12-31T23:58:59+00:00',
                'source': 'eda',
                'delivery_location': {'lat': 1.0, 'lon': 1.0},
                'total_amount': '123.45',
                'is_asap': True,
                'place_id': 40000,
            },
        ],
    },
    1002: {
        'orders': [
            {
                'order_id': '3',
                'status': 'delivered',
                'created_at': '2019-12-31T23:58:59+00:00',
                'source': 'eda',
                'delivery_location': {'lat': 1.0, 'lon': 1.0},
                'total_amount': '123.45',
                'is_asap': True,
                'place_id': 40000,
            },
        ],
    },
    1003: {
        'orders': [
            {
                'order_id': '4',
                'status': 'delivered',
                'created_at': '2019-12-31T23:59:00+00:00',
                'source': 'eda',
                'delivery_location': {'lat': 1.0, 'lon': 1.0},
                'total_amount': '123.45',
                'is_asap': True,
                'place_id': 40000,
            },
        ],
    },
    1004: {
        'orders': [
            {
                'order_id': '3',
                'status': 'delivered',
                'created_at': '2019-12-31T23:58:59+00:00',
                'source': 'eda',
                'delivery_location': {'lat': 1.0, 'lon': 1.0},
                'total_amount': '123.45',
                'is_asap': True,
                'place_id': 40000,
            },
        ],
    },
    1006: {
        'orders': [
            {
                'order_id': '4',
                'status': 'delivered',
                'created_at': '2019-12-31T23:59:00+00:00',
                'source': 'eda',
                'delivery_location': {'lat': 1.0, 'lon': 1.0},
                'total_amount': '123.45',
                'is_asap': True,
                'place_id': 40000,
            },
        ],
    },
}

SURGE_RESOLVER_RESPONSE = {
    49000: [
        {
            'placeId': 49000,
            'nativeInfo': {
                'surgeLevel': 0,
                'loadLevel': 2,
                'deliveryFee': 4.0,
            },
        },
    ],
    49001: [
        {
            'placeId': 49001,
            'nativeInfo': {
                'surgeLevel': 1,
                'loadLevel': 2,
                'deliveryFee': 4.0,
            },
        },
    ],
    49002: [
        {
            'placeId': 49002,
            'nativeInfo': {
                'surgeLevel': 3,
                'loadLevel': 2,
                'deliveryFee': 4.0,
            },
        },
    ],
    49006: [
        {
            'placeId': 49006,
            'nativeInfo': {
                'surgeLevel': 3,
                'loadLevel': 2,
                'deliveryFee': 4.0,
            },
        },
    ],
}

NOTIFICATION_IDEMPOTENCY_KEYS = [
    'surge_notify.1000.2020-01-01T00:00:00+0000',
    'surge_notify.1001.2020-01-01T00:00:00+0000',
]


@pytest.mark.pgsql('eats_surge_notify', files=['add_subscriptions.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    EATS_SURGE_NOTIFY_NOTIFY_PERIODIC_SETTINGS={
        'enabled': True,
        'check_interval': 1,
    },
)
@pytest.mark.experiments3(filename='active_order_experiment.json')
@pytest.mark.experiments3(filename='notification_params_experiment.json')
async def test_notify_periodic_eats_ordershistory(
        taxi_eats_surge_notify, mockserver,
):
    @mockserver.json_handler('/eats-offers/v1/offer/match')
    def _mock_eda_eats_offers_match_(request):
        if request.json['session_id'] in OFFERS_RESPONSE:
            return mockserver.make_response(
                json=OFFERS_RESPONSE[request.json['session_id']], status=200,
            )
        return mockserver.make_response(
            status=404,
            json={'code': 'OFFER_NOT_FOUND', 'message': 'Offer not found'},
        )

    @mockserver.json_handler('/eats-offers/v1/offer/set')
    def _mock_eda_eats_offers_set_(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eda_eats_ordershistory_(request):
        assert request.json['eats_user_id'] in ORDERSHISTORY_RESPONSE
        return mockserver.make_response(
            json=ORDERSHISTORY_RESPONSE[request.json['eats_user_id']],
            status=200,
        )

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _mock_eda_eats_surge_resolver_(request):
        return mockserver.make_response(
            json=SURGE_RESOLVER_RESPONSE[request.json['placeIds'][0]],
            status=200,
        )

    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eda_eats_notifications_(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-catalog/internal/v1/place')
    def _mock_eda_eats_catalog_(request):
        return mockserver.make_response(
            json=CATALOG_RESPONSE[request.json['slug']], status=200,
        )

    await taxi_eats_surge_notify.run_task('notify-periodic')

    expected_mock_times_called = 5
    assert (
        _mock_eda_eats_ordershistory_.times_called
        == expected_mock_times_called
    )


@pytest.mark.pgsql('eats_surge_notify', files=['add_subscriptions.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    EATS_SURGE_NOTIFY_NOTIFY_PERIODIC_SETTINGS={
        'enabled': True,
        'check_interval': 1,
    },
)
@pytest.mark.experiments3(filename='active_order_experiment.json')
@pytest.mark.experiments3(filename='notification_params_experiment.json')
async def test_notify_periodic_eats_catalog(
        taxi_eats_surge_notify, mockserver,
):
    @mockserver.json_handler('/eats-offers/v1/offer/match')
    def _mock_eda_eats_offers_match_(request):
        if request.json['session_id'] in OFFERS_RESPONSE:
            return mockserver.make_response(
                json=OFFERS_RESPONSE[request.json['session_id']], status=200,
            )
        return mockserver.make_response(
            status=404,
            json={'code': 'OFFER_NOT_FOUND', 'message': 'Offer not found'},
        )

    @mockserver.json_handler('/eats-offers/v1/offer/set')
    def _mock_eda_eats_offers_set_(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eda_eats_ordershistory_(request):
        return mockserver.make_response(
            json=ORDERSHISTORY_RESPONSE[request.json['eats_user_id']],
            status=200,
        )

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _mock_eda_eats_surge_resolver_(request):
        return mockserver.make_response(
            json=SURGE_RESOLVER_RESPONSE[request.json['placeIds'][0]],
            status=200,
        )

    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eda_eats_notifications_(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-catalog/internal/v1/place')
    def _mock_eda_eats_catalog_(request):
        return mockserver.make_response(
            json=CATALOG_RESPONSE[request.json['slug']], status=200,
        )

    await taxi_eats_surge_notify.run_task('notify-periodic')

    assert _mock_eda_eats_catalog_.times_called == 5


@pytest.mark.pgsql('eats_surge_notify', files=['add_subscriptions.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    EATS_SURGE_NOTIFY_NOTIFY_PERIODIC_SETTINGS={
        'enabled': True,
        'check_interval': 1,
    },
)
@pytest.mark.experiments3(filename='active_order_experiment.json')
@pytest.mark.experiments3(filename='notification_params_experiment.json')
async def test_notify_periodic_eats_offers(taxi_eats_surge_notify, mockserver):
    offer_prolong_times_called = {True: 0, False: 0}

    @mockserver.json_handler('/eats-offers/v1/offer/match')
    def _mock_eda_eats_offers_match_(request):
        if request.json['session_id'] in OFFERS_RESPONSE:
            offer_prolong_times_called[request.json['need_prolong']] += 1
            return mockserver.make_response(
                json=OFFERS_RESPONSE[request.json['session_id']], status=200,
            )
        return mockserver.make_response(
            status=404,
            json={'code': 'OFFER_NOT_FOUND', 'message': 'Offer not found'},
        )

    @mockserver.json_handler('/eats-offers/v1/offer/set')
    def _mock_eda_eats_offers_set_(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eda_eats_ordershistory_(request):
        return mockserver.make_response(
            json=ORDERSHISTORY_RESPONSE[request.json['eats_user_id']],
            status=200,
        )

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _mock_eda_eats_surge_resolver_(request):
        return mockserver.make_response(
            json=SURGE_RESOLVER_RESPONSE[request.json['placeIds'][0]],
            status=200,
        )

    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eda_eats_notifications_(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-catalog/internal/v1/place')
    def _mock_eda_eats_catalog_(request):
        return mockserver.make_response(
            json=CATALOG_RESPONSE[request.json['slug']], status=200,
        )

    await taxi_eats_surge_notify.run_task('notify-periodic')

    expected_mock_times_called = 4
    assert (
        offer_prolong_times_called[False]
        == expected_mock_times_called - _mock_eda_eats_offers_set_.times_called
    )


@pytest.mark.pgsql('eats_surge_notify', files=['add_subscriptions.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    EATS_SURGE_NOTIFY_NOTIFY_PERIODIC_SETTINGS={
        'enabled': True,
        'check_interval': 1,
    },
)
@pytest.mark.experiments3(filename='active_order_experiment.json')
@pytest.mark.experiments3(filename='notification_params_experiment.json')
async def test_notify_periodic_eats_surge_resolver(
        taxi_eats_surge_notify, mockserver,
):
    @mockserver.json_handler('/eats-offers/v1/offer/match')
    def _mock_eda_eats_offers_match_(request):
        if request.json['session_id'] in OFFERS_RESPONSE:
            return mockserver.make_response(
                json=OFFERS_RESPONSE[request.json['session_id']], status=200,
            )
        return mockserver.make_response(
            status=404,
            json={'code': 'OFFER_NOT_FOUND', 'message': 'Offer not found'},
        )

    @mockserver.json_handler('/eats-offers/v1/offer/set')
    def _mock_eda_eats_offers_set_(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eda_eats_ordershistory_(request):
        return mockserver.make_response(
            json=ORDERSHISTORY_RESPONSE[request.json['eats_user_id']],
            status=200,
        )

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _mock_eda_eats_surge_resolver_(request):
        assert request.json['placeIds'][0] in SURGE_RESOLVER_RESPONSE
        return mockserver.make_response(
            json=SURGE_RESOLVER_RESPONSE[request.json['placeIds'][0]],
            status=200,
        )

    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eda_eats_notifications_(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-catalog/internal/v1/place')
    def _mock_eda_eats_catalog_(request):
        return mockserver.make_response(
            json=CATALOG_RESPONSE[request.json['slug']], status=200,
        )

    await taxi_eats_surge_notify.run_task('notify-periodic')

    expected_mock_times_called = 3
    assert (
        _mock_eda_eats_surge_resolver_.times_called
        == expected_mock_times_called
    )


@pytest.mark.pgsql('eats_surge_notify', files=['add_subscriptions.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    EATS_SURGE_NOTIFY_NOTIFY_PERIODIC_SETTINGS={
        'enabled': True,
        'check_interval': 1,
    },
)
@pytest.mark.experiments3(filename='active_order_experiment.json')
@pytest.mark.experiments3(filename='notification_params_experiment.json')
async def test_notify_periodic_eats_notifications(
        taxi_eats_surge_notify, mockserver,
):
    offer_prolong_times_called = {True: 0, False: 0}

    @mockserver.json_handler('/eats-offers/v1/offer/match')
    def _mock_eda_eats_offers_match_(request):
        if request.json['session_id'] in OFFERS_RESPONSE:
            offer_prolong_times_called[request.json['need_prolong']] += 1
            return mockserver.make_response(
                json=OFFERS_RESPONSE[request.json['session_id']], status=200,
            )
        return mockserver.make_response(
            status=404,
            json={'code': 'OFFER_NOT_FOUND', 'message': 'Offer not found'},
        )

    @mockserver.json_handler('/eats-offers/v1/offer/set')
    def _mock_eda_eats_offers_set_(request):
        return mockserver.make_response(
            json={
                'status': 'NEW_OFFER_CREATED',
                'session_id': 'session-id-1',
                'request_time': '2020-01-01T00:15:00+00:00',
                'expiration_time': '2020-01-01T00:15:00+00:00',
                'prolong_count': 0,
                'parameters': {'location': [1, 1]},
                'payload': {},
            },
            status=200,
        )

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eda_eats_ordershistory_(request):
        return mockserver.make_response(
            json=ORDERSHISTORY_RESPONSE[request.json['eats_user_id']],
            status=200,
        )

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _mock_eda_eats_surge_resolver_(request):
        return mockserver.make_response(
            json=SURGE_RESOLVER_RESPONSE[request.json['placeIds'][0]],
            status=200,
        )

    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eda_eats_notifications_(request):
        assert (
            request.headers['X-Idempotency-Token']
            in NOTIFICATION_IDEMPOTENCY_KEYS
        )
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-catalog/internal/v1/place')
    def _mock_eda_eats_catalog_(request):
        return mockserver.make_response(
            json=CATALOG_RESPONSE[request.json['slug']], status=200,
        )

    await taxi_eats_surge_notify.run_task('notify-periodic')

    expected_mock_times_called = 2
    assert (
        _mock_eda_eats_notifications_.times_called
        == expected_mock_times_called
    )

    assert offer_prolong_times_called[True] == 1
    assert _mock_eda_eats_offers_set_.times_called == 1


@pytest.mark.pgsql(
    'eats_surge_notify', files=['subscription_to_check_round.sql'],
)
@pytest.mark.now('2020-01-01T00:15:00+00:00')
@pytest.mark.config(
    EATS_SURGE_NOTIFY_NOTIFY_PERIODIC_SETTINGS={
        'enabled': True,
        'check_interval': 1,
    },
)
@pytest.mark.experiments3(filename='active_order_experiment.json')
@pytest.mark.experiments3(filename='notification_params_experiment.json')
async def test_notify_periodic_notifications_failed(
        taxi_eats_surge_notify, mockserver, pgsql,
):
    @mockserver.json_handler('/eats-offers/v1/offer/match')
    def _mock_eda_eats_offers_match_(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'OFFER_NOT_FOUND', 'message': 'Offer not found'},
        )

    @mockserver.json_handler('/eats-offers/v1/offer/set')
    def _mock_eda_eats_offers_set_(request):
        return mockserver.make_response(
            json={
                'status': 'NEW_OFFER_CREATED',
                'session_id': 'session-id-1',
                'request_time': '2020-01-01T00:15:00+00:00',
                'expiration_time': '2020-01-01T00:15:00+00:00',
                'prolong_count': 0,
                'parameters': {'location': [1, 1]},
                'payload': {},
            },
            status=200,
        )

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_eda_eats_ordershistory_(request):
        return mockserver.make_response(
            json=ORDERSHISTORY_RESPONSE[1000], status=200,
        )

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _mock_eda_eats_surge_resolver_(request):
        return mockserver.make_response(
            json=SURGE_RESOLVER_RESPONSE[49000], status=200,
        )

    @mockserver.json_handler('/eats-notifications/v1/notification')
    def _mock_eda_eats_notifications_(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'surge_notify.1000.2020-01-01T00:20:00+0000'
        )
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/eats-catalog/internal/v1/place')
    def _mock_eda_eats_catalog_(request):
        return mockserver.make_response(
            json=CATALOG_RESPONSE['slug'], status=200,
        )

    await taxi_eats_surge_notify.run_task('notify-periodic')

    cursor = pgsql['eats_surge_notify'].cursor()
    cursor.execute(
        'SELECT COUNT(*) from eats_surge_notify.subscriptions '
        'WHERE eater_id = \'1000\'',
    )
    rows_count = list(cursor)[0][0]

    assert rows_count == 0
