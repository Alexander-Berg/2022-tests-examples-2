import pytest


URL = '/driver/v1/driver-money/v1/on-demand-payouts/modes/selected'
HEADERS = {
    'User-Agent': 'Taximeter 9.17 (228)',
    'Accept-Language': 'ru',
    'X-Request-Application-Version': '9.17',
    'X-YaTaxi-Park-Id': 'park0',
    'X-YaTaxi-Driver-Profile-Id': 'driver0',
}
FP_STATUS_URL = '/fleet-payouts/internal/on-demand-payouts/v1/change-mode'
EXPERIMENT = dict(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_on_demand_payouts',
    consumers=['driver-money/context'],
    default_value={'enabled': True},
    is_config=True,
)
PROFILES_LIST = {
    'driver_profiles': [
        {
            'accounts': [
                {'balance': '2444216.6162', 'currency': 'RUB', 'id': 'driver'},
            ],
            'driver_profile': {
                'id': 'driver0',
                'created_date': '2020-12-12T22:22:00.1231Z',
            },
        },
    ],
    'offset': 0,
    'parks': [
        {
            'id': 'park_id_0',
            'country_id': 'rus',
            'city': 'Москва',
            'tz': 3,
            'driver_partner_source': 'yandex',
            'provider_config': {'yandex': {'clid': 'clid_0'}},
        },
    ],
    'total': 1,
    'limit': 1,
}


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.experiments3(**EXPERIMENT)
@pytest.mark.parametrize('payout_mode', ['on_demand', 'regular'])
async def test_modes_info(payout_mode, taxi_driver_money, mockserver):
    @mockserver.json_handler(FP_STATUS_URL)
    def _mock_fleet_payouts(request):
        return {'payout_mode': payout_mode}

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_profiles_list(request):
        return PROFILES_LIST

    response = await taxi_driver_money.put(
        URL, json={'mode_id': payout_mode}, headers=HEADERS,
    )

    assert response.status_code == 200
