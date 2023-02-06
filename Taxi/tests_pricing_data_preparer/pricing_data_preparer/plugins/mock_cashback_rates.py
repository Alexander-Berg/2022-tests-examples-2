# pylint: disable=redefined-outer-name, import-error
import json

from pricing_extended import mocking_base
import pytest

RATES = [
    {
        'sponsor': 'fintech',
        'rate': 0.4,
        'max_value': 100,
        'rule_ids': ['rule_1', 'rule_2'],
    },
    {'sponsor': 'portal', 'rate': 0.05},
]


class CashbackRatesContext(mocking_base.BasicMock):
    def __init__(self):
        super().__init__()
        self.response = {
            'rates': {
                'econom': {
                    'rates': RATES,
                    'transaction_payload': {'rule_ids': ['1', '2']},
                },
                'business': {
                    'rates': [{'sponsor': 'mastercard', 'rate': 0.2}],
                },
            },
        }

    def set_response_rate(self, category, value):
        self.response['rates'][category] = value

    def check_request(self, request):
        data = json.loads(request.get_data())

        assert data['zone'] == 'moscow'
        assert 'user_info' in data
        assert data['user_info']['yandex_uid'] == 'YANDEX_UID'
        assert data['user_info']['phone_id'] == 'PHONE_ID'
        assert data['user_info']['personal_phone_id'] == 'PERSONAL_PHONE_ID'
        assert 'payment_info' in data
        if 'complements' in data['payment_info']:
            personal_wallet = data['payment_info']['complements'][
                'personal_wallet'
            ]
            self.response['rates']['econom']['rates'] = RATES + [
                {
                    'sponsor': personal_wallet['method_id'],
                    'rate': 0.1,
                    'max_value': personal_wallet['balance'],
                },
            ]


@pytest.fixture
def cashback_rates_fixture():
    return CashbackRatesContext()


@pytest.fixture
def mock_cashback_rates(mockserver, cashback_rates_fixture):
    @mockserver.json_handler('/cashback-rates/v2/rates')
    def cashback_rates_check_handler(request):
        cashback_rates_fixture.check_request(request)
        return cashback_rates_fixture.process(mockserver)

    return cashback_rates_check_handler
