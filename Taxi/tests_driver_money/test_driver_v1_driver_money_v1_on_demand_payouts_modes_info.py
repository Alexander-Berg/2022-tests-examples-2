import pytest


URL = '/driver/v1/driver-money/v1/on-demand-payouts/modes/info'
PARAMS = {'tz': 'Moscow/Europe'}
HEADERS = {
    'User-Agent': 'Taximeter 9.17 (228)',
    'Accept-Language': 'ru',
    'X-Request-Application-Version': '9.17',
    'X-YaTaxi-Park-Id': 'park0',
    'X-YaTaxi-Driver-Profile-Id': 'driver0',
}
ITEMS = [
    {
        'id': 'regular',
        'title': 'Ежедневный',
        'subtitle': (
            'Деньги будут автоматически выводиться'
            ' на вашу карту раз в день в 23:59'
        ),
        'details_text': 'Подробнее',
        'details_payload': {'type': 'navigate_url', 'url': '/', 'title': ''},
    },
    {
        'id': 'on_demand',
        'title': 'По запросу',
        'subtitle': (
            'Деньги копятся на счёте Про и вы'
            ' сами решаете когда вывести их на карту'
        ),
        'details_text': 'Подробнее',
        'details_payload': {'type': 'navigate_url', 'url': '/', 'title': ''},
    },
]
FP_STATUS_URL = '/fleet-payouts/internal/on-demand-payouts/v1/status'
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
@pytest.mark.parametrize(
    'expected_payout_mode,is_order_available, override_pending_payment',
    [
        ('on_demand', True, {}),
        ('regular', False, {}),
        ('on_demand', False, {'status': 'pending'}),
    ],
)
async def test_modes_info(
        expected_payout_mode,
        is_order_available,
        override_pending_payment,
        taxi_driver_money,
        mockserver,
):
    @mockserver.json_handler(FP_STATUS_URL)
    def _mock_fleet_payouts(request):
        return {
            'payout_mode': expected_payout_mode,
            'pending_payment': {
                'status': 'completed',
                'amount': '100',
                'currency': 'RUB',
                **override_pending_payment,
            },
            'payout_scheduled_at': '2021-01-31T07:00:00+00:00',
            'on_demand_available': is_order_available,
        }

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_profiles_list(request):
        return PROFILES_LIST

    response = await taxi_driver_money.get(URL, params=PARAMS, headers=HEADERS)

    assert response.status_code == 200
    if response.status_code == 200:
        expected_response = {
            'items': ITEMS,
            'selected_id': expected_payout_mode,
            'is_order_available': is_order_available,
            'pending_payment': {
                'status': 'completed',
                'amount': '100',
                'currency': 'RUB',
                **override_pending_payment,
            },
        }
        assert response.json() == expected_response


@pytest.mark.now('2020-01-16T21:30:00+0300')
async def test_modes_info_400(taxi_driver_money, mockserver):
    @mockserver.json_handler(FP_STATUS_URL)
    def _mock_fleet_payouts(request):
        return mockserver.make_response(
            status=400,
            # json={},
        )

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_profiles_list(request):
        return PROFILES_LIST

    response = await taxi_driver_money.get(URL, params=PARAMS, headers=HEADERS)

    assert response.status_code == 400
