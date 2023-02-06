# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_picker_payments_plugins import *  # noqa: F403 F401

BEARER = 'Bearer '


def _check_auth(request):
    assert 'Authorization' in request.headers
    assert len(request.headers['Authorization']) - len(BEARER) > 0
    assert request.headers['Authorization'].startswith(BEARER)


@pytest.fixture(
    params=[
        pytest.param(
            ['mockserver', 'tinkoff-secured'],
            marks=pytest.mark.config(EATS_PICKER_PAYMENTS_USE_STUBS=False),
        ),
        pytest.param(
            ['mockserver', 'eats-stub-tinkoff'],
            marks=pytest.mark.config(EATS_PICKER_PAYMENTS_USE_STUBS=True),
        ),
    ],
)
def tinkoff_service(mockserver, mockserver_ssl, request):
    return TinkoffMock(locals()[request.param[0]], request.param[1])


class TinkoffMock:
    def __init__(self, mockserver, service_name):
        self.card_spend_limits = {}
        self.card_spend_remains = {}
        self.card_cash_limits = {}
        self.accounts = {}

        @mockserver.json_handler(
            fr'/{service_name}/api/v1/card/(?P<cid>\d+)/limits', regex=True,
        )
        def _get_card_limits(request, cid):
            _check_auth(request)
            cid = int(cid)

            if (
                    cid not in self.card_spend_limits
                    or cid not in self.card_cash_limits
            ):
                return mockserver.make_response(status=404)
            return {
                'ucid': cid,
                'spendLimit': {
                    'limitPeriod': 'IRREGULAR',
                    'limitValue': self.card_spend_limits[cid],
                    'limitRemain': self.card_spend_remains[cid],
                },
                'cashLimit': {
                    'limitPeriod': 'IRREGULAR',
                    'limitValue': 0,
                    'limitRemain': 0,
                },
            }

        @mockserver.json_handler(
            fr'/{service_name}/api/v1/card/(?P<cid>\d+)/spend-limit',
            regex=True,
        )
        def _set_spend_limit(request, cid):
            _check_auth(request)
            cid = int(cid)

            data = request.json
            assert data['limitPeriod'] == 'IRREGULAR'

            self.card_spend_limits[cid] = data['limitValue']
            self.card_spend_remains[cid] = data['limitValue']

            return mockserver.make_response()

        @mockserver.json_handler(
            fr'/{service_name}/api/v1/card/(?P<cid>\d+)/cash-limit',
            regex=True,
        )
        # pylint: disable=W0612
        def _set_cash_limit(request, cid):
            _check_auth(request)
            cid = int(cid)

            data = request.json
            assert data['limitPeriod'] == 'IRREGULAR'
            assert data['limitValue'] == 0

            self.card_cash_limits[cid] = 0

            return mockserver.make_response()

        @mockserver.json_handler(f'/{service_name}/api/v3/bank-accounts')
        def _get_accounts(request):
            _check_auth(request)
            assert request.method == 'GET'
            json_accounts = []
            for _, account in self.accounts.items():
                json_accounts.append(account)
            return mockserver.make_response(json=json_accounts)

    def decrease_limit_remains(self, cid, amount):
        cid = int(cid)

        self.card_spend_remains[cid] -= amount

    def set_limit(self, cid, amount):
        cid = int(cid)

        self.card_spend_limits[cid] = amount
        self.card_spend_remains[cid] = amount
        self.card_cash_limits[cid] = 0

    def add_account(
            self,
            account_number='12345678901234567890',
            name='Account Name',
            currency='643',
            bank_bik='12345678',
            account_type='Current',
            activation_date='2020-06-29',
            balance=1000000,
            authorized=10000,
            pending_payments=0,
            pending_requisitions=0,
    ):
        self.accounts[name] = {
            'accountNumber': account_number,
            'name': name,
            'currency': currency,
            'bankBik': bank_bik,
            'accountType': account_type,
            'activationDate': activation_date,
            'balance': {
                'otb': balance,
                'authorized': authorized,
                'pendingPayments': pending_payments,
                'pendingRequisitions': pending_requisitions,
            },
        }
