import pytest

ENDPOINT = 'fleet/fleet-orders/v1/driver/transactions/list'

TAXIMETER_BACKEND_FLEET_ORDERS = {
    'dispatcher': {
        'en': 'Dispatcher: %(dispatcher_name)s',
        'ru': 'Диспетчер: %(dispatcher_name)s',
    },
    'tech_support': {'en': 'Tech support', 'ru': 'Техническая поддержка'},
    'fleet_api': {
        'en': 'Fleet API: key %(key_id)s',
        'ru': 'Fleet API: ключ %(key_id)s',
    },
    'platform': {'en': 'Platform', 'ru': 'Платформа'},
}


def build_headers(park_id):
    headers = {
        'Accept-Language': 'tr',
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }

    return headers


@pytest.mark.translations(
    taximeter_backend_fleet_orders=TAXIMETER_BACKEND_FLEET_ORDERS,
)
@pytest.mark.pgsql('fleet_orders', files=['orders.sql'])
async def test_success(taxi_fleet_orders, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _v1_parks_list(request):
        return {
            'parks': [
                {
                    'id': 'park_id1',
                    'name': 'park_name',
                    'login': 'park_login',
                    'is_active': True,
                    'city_id': 'Москва',
                    'tz_offset': 3,
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'rus',
                    'demo_mode': False,
                    'provider_config': {
                        'clid': '111111',
                        'type': 'production',
                    },
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/transactions/list',
    )
    def _v1_parks_driver_profiles_transactions_list(request):
        assert request.json == {
            'cursor': 'asd',
            'limit': 2,
            'query': {
                'park': {
                    'driver_profile': {
                        'id': 'aab36cr7560d499f8acbe2c52a7j7n9p',
                    },
                    'id': 'park_id1',
                    'transaction': {
                        'event_at': {
                            'from': '2019-09-08T11:16:11+00:00',
                            'to': '2019-09-09T11:16:11+00:00',
                        },
                    },
                },
            },
        }

        return {
            'cursor': 'sdf',
            'limit': 2,
            'transactions': [
                {
                    'amount': '1050.5000',
                    'category_id': 'card',
                    'category_name': 'card',
                    'created_by': {'identity': 'platform'},
                    'currency_code': 'RUB',
                    'description': 'text',
                    'driver_profile_id': 'aab36cr7560d499f8acbe2c52a7j7n9p',
                    'event_at': '2019-09-09T13:15:09+03:00',
                    'id': '120932b5a48b4dtca707fa9abfh66jab',
                    'order': {
                        'id': '31a982h5846w4dfcgb07fweadfty61ab',
                        'short_id': 90149,
                    },
                    'order_id': '31a982h5846w4dfcgb07fweadfty61ab',
                },
            ],
        }

    @mockserver.json_handler('/territories/v1/countries/retrieve')
    async def _v1_countries_retrieve(request, **kwargs):
        return {'_id': 'rus_id', 'country': 'rus', 'currency': 'RUB'}

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/transactions'
        '/categories/list/by-user',
    )
    async def _list_transaction_categories(request):
        assert request.json == {'query': {'park': {'id': 'park_id1'}}}

        assert request.headers['Accept-Language'] == 'tr'
        assert request.headers['X-Ya-User-Ticket'] == 'ticket_valid1'
        assert request.headers['X-Ya-User-Ticket-Provider'] == 'yandex_team'
        assert request.headers['X-Yandex-UID'] == '1'

        return {
            'categories': [
                {
                    'group_id': 'group_id',
                    'group_name': 'group_name',
                    'id': 'card',
                    'is_affecting_driver_balance': True,
                    'is_creatable': True,
                    'is_editable': False,
                    'is_enabled': True,
                    'name': 'card',
                },
                {
                    'group_id': 'group_id',
                    'group_name': 'group_name',
                    'id': 'platform_ride_fee',
                    'is_affecting_driver_balance': True,
                    'is_creatable': True,
                    'is_editable': False,
                    'is_enabled': True,
                    'name': 'platform_ride_fee',
                },
            ],
        }

    @mockserver.json_handler('/billing-reports/v1/balances/select')
    async def _v1_balances_select(request):
        assert request.json == {
            'accounts': [
                {
                    'agreement_id': 'taxi/driver_balance',
                    'currency': 'RUB',
                    'entity_external_id': (
                        'taximeter_driver_id/park_id1/'
                        'aab36cr7560d499f8acbe2c52a7j7n9p'
                    ),
                    'sub_account': 'total',
                },
            ],
            'accrued_at': ['2019-09-09T11:16:11+00:00'],
        }

        return {
            'entries': [
                {
                    'account': {
                        'account_id': 35480196,
                        'entity_external_id': (
                            'taximeter_driver_id/park_id1/'
                            'aab36cr7560d499f8acbe2c52a7j7n9p'
                        ),
                        'agreement_id': 'taxi/driver_balance',
                        'currency': 'EUR',
                        'sub_account': 'total',
                    },
                    'balances': [
                        {
                            'balance': '300',
                            'accrued_at': '2019-09-01T00:00:00+03:00',
                            'last_created': '2019-09-01T00:00:00+03:00',
                            'last_entry_id': 113,
                        },
                    ],
                },
            ],
        }

    request = {
        'query': {
            'park': {
                'transaction': {
                    'event_at': {
                        'from': '2019-09-08T11:16:11+00:00',
                        'to': '2019-09-09T11:16:11+00:00',
                    },
                },
                'driver_profile': {'id': 'aab36cr7560d499f8acbe2c52a7j7n9p'},
            },
        },
        'limit': 2,
        'cursor': 'asd',
    }

    response = await taxi_fleet_orders.post(
        ENDPOINT, json=request, headers=build_headers('park_id1'),
    )

    assert response.json() == {
        'balance_cursor': -750.5,
        'cursor': 'sdf',
        'limit': 2,
        'transactions': [
            {
                'amount': 1050.5,
                'balance': 300.0,
                'category_id': 'card',
                'created_by': 'Platform',
                'currency_code': 'RUB',
                'description': 'text',
                'event_at': '2019-09-09T10:15:09+00:00',
                'id': '120932b5a48b4dtca707fa9abfh66jab',
                'order_id': 'order1',
                'short_order_id': 1,
            },
        ],
    }
