import pytest

ENDPOINT = '/v1/balances'


def _make_params(contractor_profile_id):
    return {
        'park_id': 'park_with_offer',
        'contractor_profile_id': contractor_profile_id,
    }


@pytest.fixture(name='mock_driver_retrieve')
def _mock_driver_retrieve(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_retrieve(request):
        driver_id = request.json['id_in_set'][0]
        return {
            'park_with_offer_driver1': {
                'profiles': [
                    {
                        'park_driver_profile_id': 'park_with_offer_driver1',
                        'data': {'balance_limit': '1000.000000'},
                    },
                ],
            },
        }[driver_id]


@pytest.fixture(name='mock_fta_balances_list')
def _mock_fta_balances_list(mockserver):
    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _fta_balances_list(request):
        return {
            'driver_profiles': [
                {
                    'driver_profile_id': '123',
                    'balances': [
                        {
                            'accrued_at': request.json['query']['balance'][
                                'accrued_ats'
                            ][0],
                            'total_balance': '1050.5000',
                        },
                    ],
                },
            ],
        }


async def test_balance_ok(
        taxi_gas_stations_api,
        mock_driver_retrieve,
        mock_fta_balances_list,
        gas_stations,
):
    response = await taxi_gas_stations_api.get(
        ENDPOINT, params=_make_params('driver1'),
    )
    assert response.status_code == 200
    assert response.json() == {'balance': '1050.5000', 'balance_limit': '1000'}


async def test_404(taxi_gas_stations_api, mockserver, gas_stations):
    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    async def _mock_fta_client(request):
        return mockserver.make_response(status=400)

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _mock_driver_profiles(request):
        return {
            'profiles': [
                {'park_driver_profile_id': 'park_with_offer_driver1'},
            ],
        }

    response = await taxi_gas_stations_api.get(
        ENDPOINT, params=_make_params('driver1'),
    )
    assert response.status_code == 404
    assert _mock_driver_profiles.has_calls


async def test_429(
        taxi_gas_stations_api, mockserver, mock_driver_retrieve, gas_stations,
):
    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    async def _mock_fta_client(request):
        return mockserver.make_response(status=429)

    response = await taxi_gas_stations_api.get(
        ENDPOINT, params=_make_params('driver1'),
    )
    assert response.status_code == 429
    assert _mock_fta_client.has_calls
