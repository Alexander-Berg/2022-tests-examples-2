import pytest

ENDPOINT = '/fleet/transactions/v1/metrics'


def build_headers(park_id):
    headers = {
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }
    return headers


async def test_success(taxi_fleet_transactions_api, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_v1_parks_list(request):
        return {
            'parks': [
                {
                    'city_id': 'Берлин',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'id': '8601e1f8e094424aa70c81b61ffdf01f',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'login',
                    'name': 'name',
                },
            ],
        }

    @mockserver.json_handler('/billing-reports/v1/balances/select')
    async def _mock_billing_reports(request):
        return {
            'entries': [
                {
                    'account': {
                        'account_id': 33260029,
                        'agreement_id': 'taxi/yandex_ride',
                        'currency': 'EUR',
                        'entity_external_id': 'taximeter_park_id/park_id1',
                        'sub_account': 'payment/cash',
                    },
                    'balances': [
                        {
                            'accrued_at': '2022-01-01T00:00:00Z',
                            'balance': '100',
                            'last_created': '2021-01-01T00:00:00Z',
                            'last_entry_id': 12345678,
                        },
                        {
                            'accrued_at': '2023-01-01T00:00:00Z',
                            'balance': '200',
                            'last_created': '2021-01-01T00:00:00Z',
                            'last_entry_id': 12345678,
                        },
                    ],
                },
                {
                    'account': {
                        'account_id': 33260029,
                        'agreement_id': 'taxi/yandex_ride',
                        'currency': 'EUR',
                        'entity_external_id': 'taximeter_park_id/park_id1',
                        'sub_account': 'payment/card',
                    },
                    'balances': [
                        {
                            'accrued_at': '2022-01-01T00:00:00Z',
                            'balance': '150',
                            'last_created': '2021-01-01T00:00:00Z',
                            'last_entry_id': 12345678,
                        },
                        {
                            'accrued_at': '2023-01-01T00:00:00Z',
                            'balance': '300',
                            'last_created': '2021-01-01T00:00:00Z',
                            'last_entry_id': 12345678,
                        },
                    ],
                },
            ],
        }

    response = await taxi_fleet_transactions_api.post(
        ENDPOINT,
        headers=build_headers('park_id1'),
        json={
            'interval': {
                'from': '2022-01-01T00:00:00Z',
                'to': '2023-01-01T00:00:00Z',
            },
        },
    )

    assert response.status == 200
    assert response.json() == {'revenue': '250'}


@pytest.mark.parametrize(
    ['params', 'message'],
    [
        (
            {
                'interval': {
                    'from': '2022-01-01T00:00:00Z',
                    'to': '2022-01-01T00:00:00Z',
                },
            },
            'interval.from must be less than interval.to',
        ),
        (
            {
                'interval': {
                    'from': '2018-01-01T00:00:00Z',
                    'to': '2018-01-20T12:07:00Z',
                },
            },
            'interval must contain dates truncated to '
            'hours for dates older than 168 hours before now',
        ),
    ],
)
async def test_error(
        taxi_fleet_transactions_api, mock_fleet_parks_list, params, message,
):
    response = await taxi_fleet_transactions_api.post(
        ENDPOINT, headers=build_headers('7ad35b'), json=params,
    )

    assert response.status == 400
    assert response.json()['code'] == 'incorrect_interval'
    assert response.json()['message'] == message
