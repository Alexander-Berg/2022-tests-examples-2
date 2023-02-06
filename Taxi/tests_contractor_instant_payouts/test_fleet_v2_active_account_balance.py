import pytest

from tests_contractor_instant_payouts import utils

ENDPOINT = '/fleet/instant-payouts/v2/active-account/balance'
MODULBANK_MOCK_URL = (
    '/contractor-instant-payouts-modulbank/api/accounts/'
    'a0000000-0000-0000-0000-000000000001'
)
MOZEN_MOCK_URL = (
    '/contractor-instant-payouts-mozen/api/public/payout/credentials'
)

INTERPAY_MOCK_URL = '/interpay/v1/emoney/contracts/agent/balance'


OK_PARAMS = [
    ('PARK-01', '123.45'),
    ('PARK-02', '543.21'),
    ('PARK-03', '333.33'),
]


@pytest.mark.parametrize('park_id, expected_balance', OK_PARAMS)
async def test_ok(
        taxi_contractor_instant_payouts, mockserver, park_id, expected_balance,
):
    @mockserver.json_handler(MODULBANK_MOCK_URL)
    def _modulbank_handler(request):
        return {
            'status': 'success',
            'data': {
                'id': 'a0000000-0000-0000-0000-000000000001',
                'status': 'enabled',
                'balance': 123.45,
            },
        }

    @mockserver.json_handler(MOZEN_MOCK_URL)
    def _mozen_handler(request):
        return {'balance': {'amount': 54321, 'currency': 'RUB'}}

    @mockserver.json_handler(INTERPAY_MOCK_URL)
    def _interpay_handler(request):
        return {
            'id': 1,
            'ref_id': 123,
            'currency': 398,
            'balance': '333.3333',
            'stated_at': '2022-01-01T00:00:00+00:00',
        }

    response = await taxi_contractor_instant_payouts.get(
        ENDPOINT, headers=utils.build_headers(park_id=park_id),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'balance': expected_balance}


@pytest.mark.parametrize('park_id', ['PARK-01', 'PARK-02', 'PARK-99'])
async def test_does_not_exists(
        taxi_contractor_instant_payouts, mockserver, park_id,
):
    @mockserver.json_handler(MODULBANK_MOCK_URL)
    def _modulbank_handler(request):
        return {
            'status': 'success',
            'data': {
                'id': 'a0000000-0000-0000-0000-000000000001',
                'status': 'none',
                'balance': 123.45,
            },
        }

    @mockserver.json_handler(MOZEN_MOCK_URL)
    def _mozen_handler(request):
        return {}

    response = await taxi_contractor_instant_payouts.get(
        ENDPOINT, headers=utils.build_headers(park_id=park_id),
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'does_not_exist',
        'message': 'The requested account does not exist.',
    }
