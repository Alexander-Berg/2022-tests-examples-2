import pytest


ENDPOINT = 'fleet/fleet-orders/v1/driver/transactions/order/list'

HEADERS = {
    'Accept-Language': 'en',
    'X-Ya-User-Ticket': 'ticket_valid1',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Yandex-UID': '1',
    'X-Park-ID': 'park_id',
}

FTA_TRANSACTIONS = [
    {
        'amount': '1060.5000',
        'category_id': 'card',
        'category_name': 'card',
        'created_by': {'identity': 'platform'},
        'currency_code': 'RUB',
        'description': 'text',
        'driver_profile_id': 'another_driver_id',
        'event_at': '2019-09-09T15:40:13+03:00',
        'id': 'transaction_id0',
        'order': {'id': 'alias_order_id', 'short_id': 1},
        'order_id': 'alias_order_id',
    },
    {
        'amount': '1050.5000',
        'category_id': 'card',
        'category_name': 'card',
        'created_by': {'identity': 'platform'},
        'currency_code': 'RUB',
        'description': 'text',
        'driver_profile_id': 'driver_id',
        'event_at': '2019-09-09T13:15:09+03:00',
        'id': 'transaction_id',
        'order': {'id': 'alias_order_id', 'short_id': 1},
        'order_id': 'alias_order_id',
    },
    {
        'amount': '1060.5000',
        'category_id': 'card',
        'category_name': 'card',
        'created_by': {'identity': 'platform'},
        'currency_code': 'RUB',
        'description': 'text',
        'driver_profile_id': 'another_driver_id',
        'event_at': '2019-09-09T15:40:13+03:00',
        'id': 'transaction_id3',
        'order': {'id': 'alias_order_id', 'short_id': 1},
        'order_id': 'alias_order_id',
    },
    {
        'amount': '1060.5000',
        'category_id': 'card',
        'category_name': 'card',
        'created_by': {'identity': 'platform'},
        'currency_code': 'RUB',
        'description': 'text',
        'driver_profile_id': 'driver_id',
        'event_at': '2019-09-09T15:40:13+03:00',
        'id': 'transaction_id1',
        'order': {'id': 'alias_order_id', 'short_id': 1},
        'order_id': 'alias_order_id',
    },
    {
        'amount': '1060.5000',
        'category_id': 'card',
        'category_name': 'card',
        'created_by': {'identity': 'platform'},
        'currency_code': 'RUB',
        'description': 'text',
        'driver_profile_id': 'another_driver_id',
        'event_at': '2019-09-09T15:40:13+03:00',
        'id': 'transaction_id2',
        'order': {'id': 'alias_order_id', 'short_id': 1},
        'order_id': 'alias_order_id',
    },
]

TRANSACTIONS = [
    {
        'amount': 1050.5,
        'category_id': 'card',
        'created_by': 'Platform',
        'currency_code': 'RUB',
        'description': 'text',
        'driver_id': 'driver_id',
        'event_at': '2019-09-09T10:15:09+00:00',
        'id': 'transaction_id',
        'order_id': 'order_id',
        'short_order_id': 1,
    },
    {
        'amount': 1060.5,
        'category_id': 'card',
        'created_by': 'Platform',
        'currency_code': 'RUB',
        'description': 'text',
        'driver_id': 'driver_id',
        'event_at': '2019-09-09T12:40:13+00:00',
        'id': 'transaction_id1',
        'order_id': 'order_id',
        'short_order_id': 1,
    },
]

TAXIMETER_BACKEND_FLEET_ORDERS = {
    'dispatcher': {'en': 'Dispatcher: %(dispatcher_name)s'},
    'tech_support': {'en': 'Tech support'},
    'fleet_api': {'en': 'Fleet API: key %(key_id)s'},
    'platform': {'en': 'Platform'},
}


@pytest.mark.translations(
    taximeter_backend_fleet_orders=TAXIMETER_BACKEND_FLEET_ORDERS,
)
@pytest.mark.parametrize(
    'request_transaction, fta_transactions, transactions',
    [
        (None, FTA_TRANSACTIONS, TRANSACTIONS),
        ({}, FTA_TRANSACTIONS, TRANSACTIONS),
        (
            {
                'event_at': {
                    'from': '2019-09-08T21:00:00+00:00',
                    'to': '2019-09-08T21:00:00+00:00',
                },
            },
            FTA_TRANSACTIONS,
            TRANSACTIONS,
        ),
        ({}, [], []),
    ],
)
@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_success(
        taxi_fleet_orders,
        mockserver,
        request_transaction,
        fta_transactions,
        transactions,
):
    driver_id = 'driver_id'
    order_id = 'order_id'
    order_alias_id = 'order_alias_id'

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/orders/transactions/list',
    )
    def _v1_parks_orders_transactions_list(request):
        assert request.json['query']['park']['id'] == 'park_id'
        assert request.json['query']['park']['order']['ids'] == [
            order_alias_id,
        ]
        if request_transaction not in [None, {}]:
            assert (
                request.json['query']['park']['transaction']
                == request_transaction
            )

        return {'transactions': fta_transactions}

    request = {
        'query': {
            'park': {
                'order': {'id': order_id},
                'driver_profile': {'id': driver_id},
                'transaction': request_transaction,
            },
        },
    }

    response = await taxi_fleet_orders.post(
        ENDPOINT, json=request, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {'transactions': transactions}


@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_success_null_order_alias_id(taxi_fleet_orders, mockserver):
    request = {
        'query': {
            'park': {
                'order': {'id': 'order_id_null_alias_id'},
                'driver_profile': {'id': 'driver_id'},
            },
        },
    }

    response = await taxi_fleet_orders.post(
        ENDPOINT, json=request, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {'transactions': []}


@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_failed_404_order_not_found(taxi_fleet_orders, mockserver):
    request = {
        'query': {
            'park': {
                'order': {'id': 'non_existing_order_id'},
                'driver_profile': {'id': 'driver_id'},
            },
        },
    }

    response = await taxi_fleet_orders.post(
        ENDPOINT, json=request, headers=HEADERS,
    )

    assert response.status_code == 404


@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_failed_fta_400_bad_request(taxi_fleet_orders, mockserver):
    driver_id = 'driver_id'
    order_id = 'order_id'
    order_alias_id = 'order_alias_id'

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/orders/transactions/list',
    )
    def _v1_parks_orders_transactions_list(request):
        assert request.json['query']['park']['id'] == 'park_id'
        assert request.json['query']['park']['order']['ids'] == [
            order_alias_id,
        ]

        return mockserver.make_response(
            json={'code': 'bad_request', 'message': 'bad request'}, status=400,
        )

    request = {
        'query': {
            'park': {
                'order': {'id': order_id},
                'driver_profile': {'id': driver_id},
            },
        },
    }

    response = await taxi_fleet_orders.post(
        ENDPOINT, json=request, headers=HEADERS,
    )

    assert response.status_code == 400
    assert response.json() == {'code': 'bad_request', 'message': 'bad request'}


@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_failed_fta_429_too_many_requests(taxi_fleet_orders, mockserver):
    driver_id = 'driver_id'
    order_id = 'order_id'
    order_alias_id = 'order_alias_id'

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/orders/transactions/list',
    )
    def _v1_parks_orders_transactions_list(request):
        assert request.json['query']['park']['id'] == 'park_id'
        assert request.json['query']['park']['order']['ids'] == [
            order_alias_id,
        ]

        return mockserver.make_response(status=429)

    request = {
        'query': {
            'park': {
                'order': {'id': order_id},
                'driver_profile': {'id': driver_id},
            },
        },
    }

    response = await taxi_fleet_orders.post(
        ENDPOINT, json=request, headers=HEADERS,
    )

    assert response.status_code == 429
