import copy
import hashlib

import pytest

from tests_grocery_p13n import common
from tests_grocery_p13n import depot
from tests_grocery_p13n import experiments
from tests_grocery_p13n import headers


async def test_lavka_cashback_info_experiment_disabled(taxi_grocery_p13n):
    """ /cashback-info should return 404 if experiment is disabled """
    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/cashback-info',
        headers=headers.DEFAULT_HEADERS,
        json={'depot': depot.DEPOT},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'DISABLED_BY_EXPERIMENT'


async def test_lavka_cashback_info_unathorised(taxi_grocery_p13n):
    """ /cashback-info should return 401 for unathorised request """
    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/cashback-info', json={'depot': depot.DEPOT},
    )
    assert response.status_code == 401


@experiments.CASHBACK_EXPERIMENT_RUSSIA
@experiments.CASHBACK_CHARGE_ENABLED
@pytest.mark.config(GROCERY_P13N_CASHBACK_COMPLEMENT_PAYMENT_TYPES=['card'])
async def test_lavka_cashback_info_200(taxi_grocery_p13n, billing_wallet):
    """ /cashback-info should return cashback info if everything is ok """

    yandex_uid = headers.DEFAULT_HEADERS['X-Yandex-UID']
    billing_wallet.check_balances(yandex_uid=yandex_uid)

    wallet_id = 'wallet-id-123'

    balance_ceil = 150
    balance_double = 0.91
    balance = str(balance_ceil + balance_double)

    billing_wallet.mock_balances(
        balances=[
            {'wallet_id': wallet_id, 'amount': balance, 'currency': 'RUB'},
        ],
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/cashback-info',
        headers=headers.DEFAULT_HEADERS,
        json={'depot': depot.DEPOT},
    )
    assert response.status_code == 200

    assert response.json() == {
        'balance': str(balance_ceil),
        'complement_payment_types': ['card'],
        'wallet_id': wallet_id,
    }

    assert billing_wallet.times_balances_called() == 1


@experiments.CASHBACK_EXPERIMENT_RUSSIA
@experiments.CASHBACK_CHARGE_DISABLED
async def test_cashback_info_cashback_charge_disabled(
        taxi_grocery_p13n, billing_wallet,
):
    """ Test cashback-info when charge disabled"""

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/cashback-info',
        headers=headers.DEFAULT_HEADERS,
        json={'depot': depot.DEPOT},
    )

    assert response.status_code == 200
    assert billing_wallet.times_balances_called() == 1

    assert response.json()['unavailability'] == {
        'charge_disabled_code': 'charge_disabled',
    }


@experiments.CASHBACK_EXPERIMENT_RUSSIA
@experiments.CASHBACK_CHARGE_ENABLED
async def test_get_balance_with_correct_currency(
        taxi_grocery_p13n, billing_wallet,
):
    """ Test case when billing-wallet returned several wallets """

    wallet_id = 'wallet-id-123'
    balance = '150'

    billing_wallet.mock_balances(
        balances=[
            {
                'wallet_id': wallet_id + '1111',
                'amount': balance + '999',
                'currency': 'ILS',
            },
            {'wallet_id': wallet_id, 'amount': balance, 'currency': 'RUB'},
        ],
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/cashback-info',
        headers=headers.DEFAULT_HEADERS,
        json={'depot': depot.DEPOT},
    )
    assert response.status_code == 200

    assert response.json() == {
        'balance': balance,
        'complement_payment_types': [],
        'wallet_id': wallet_id,
    }

    assert billing_wallet.times_balances_called() == 1


@experiments.CASHBACK_EXPERIMENT_RUSSIA
async def test_500_from_billing_wallet(taxi_grocery_p13n, billing_wallet):
    billing_wallet.set_error_code(500)

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/cashback-info',
        headers=headers.DEFAULT_HEADERS,
        json={'depot': depot.DEPOT},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'UNAVAILABLE_NOW'


@experiments.CASHBACK_EXPERIMENT_RUSSIA
async def test_country_iso3_experiment(taxi_grocery_p13n, billing_wallet):
    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/cashback-info',
        headers=headers.DEFAULT_HEADERS,
        json={'depot': depot.DEPOT_ISR},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'DISABLED_BY_EXPERIMENT'


@experiments.CASHBACK_EXPERIMENT_RUSSIA
@experiments.CASHBACK_CHARGE_ENABLED
async def test_no_balances(taxi_grocery_p13n, billing_wallet):
    billing_wallet.mock_balances(balances=[])

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/cashback-info',
        headers=headers.DEFAULT_HEADERS,
        json={'depot': depot.DEPOT},
    )

    # Implementation of generation z-wallet-id (got from userver library
    # z-wallet).
    yandex_uid = headers.DEFAULT_HEADERS['X-Yandex-UID']
    currency = depot.DEPOT['currency']
    wallet_id = hashlib.md5(
        (yandex_uid + '/' + currency).encode('utf-8'),
    ).hexdigest()
    wallet_id = 'z' + wallet_id[1:]

    assert response.status_code == 200
    assert response.json() == {
        'balance': '0',
        'complement_payment_types': [],
        'wallet_id': wallet_id,
    }


@experiments.CASHBACK_EXPERIMENT_RUSSIA
@experiments.CASHBACK_CHARGE_ENABLED
@pytest.mark.parametrize(
    'pass_flag, charge_error', [('ya-plus', None), ('', 'buy_plus')],
)
async def test_buy_plus(
        taxi_grocery_p13n, billing_wallet, pass_flag, charge_error,
):
    billing_wallet.mock_balances(balances=[])

    pass_flags = 'portal,credentials=token-bearer'
    pass_flags += ',' + pass_flag

    request_headers = copy.deepcopy(headers.DEFAULT_HEADERS)
    request_headers['X-YaTaxi-Pass-Flags'] = pass_flags

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/cashback-info',
        headers=request_headers,
        json={'depot': depot.DEPOT},
    )

    assert response.status_code == 200

    if charge_error is not None:
        assert response.json()['unavailability'] == {
            'charge_disabled_code': charge_error,
        }
    else:
        assert 'unavailability' not in response.json()


# ручка annihilation возвращает несколько кошельков
# фильтрация происходит по wallet_id
@experiments.CASHBACK_EXPERIMENT_RUSSIA
async def test_annihilation_date(
        taxi_grocery_p13n, billing_wallet, mock_annihilation,
):
    annihilation_date = '2017-01-01T00:00:00+00:00'
    balance_to_annihilate = '42'

    wallet_id = common.DEFAULT_ACCOUNT_ID
    billing_wallet.mock_balances(
        balances=[
            {'wallet_id': wallet_id, 'amount': '1000', 'currency': 'RUB'},
        ],
    )

    mock_annihilation.add_annihilation(
        wallet_id='AnotherWalletId',
        balance_to_annihilate='1000',
        currency='RUB',
        annihilation_date='2021-07-20T13:20:00+00:00',
    )

    mock_annihilation.add_annihilation(
        wallet_id=wallet_id,
        balance_to_annihilate=balance_to_annihilate,
        currency='RUB',
        annihilation_date=annihilation_date,
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/cashback-info',
        headers=headers.DEFAULT_HEADERS,
        json={'depot': depot.DEPOT},
    )

    assert response.status_code == 200
    assert response.json()['annihilation_info'] == {
        'annihilation_date': annihilation_date,
        'balance_to_annihilate': balance_to_annihilate,
    }


@experiments.CASHBACK_EXPERIMENT_RUSSIA
async def test_cashback_info_annihilation_info_500(
        taxi_grocery_p13n, billing_wallet, mockserver,
):
    wallet_id = common.DEFAULT_ACCOUNT_ID
    billing_wallet.mock_balances(
        balances=[
            {'wallet_id': wallet_id, 'amount': '1000', 'currency': 'RUB'},
        ],
    )

    @mockserver.json_handler('/cashback-annihilator/v1/annihilation/info')
    def _mock_v1_get_annihilation(request):
        return mockserver.make_response(json={}, status=500)

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/cashback-info',
        headers=headers.DEFAULT_HEADERS,
        json={'depot': depot.DEPOT},
    )

    assert response.status_code == 200


@pytest.mark.experiments3(
    name='grocery_cashback',
    consumers=['grocery-p13n/discounts', 'grocery-p13n/cashback-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'init': {
                    'predicate': {
                        'init': {
                            'value': 'ru',
                            'arg_name': 'country_iso2_by_ip',
                            'arg_type': 'string',
                        },
                        'type': 'eq',
                    },
                },
                'type': 'not',
            },
            'value': {'enabled': False},
        },
    ],
    default_value={'enabled': True},
)
@experiments.CASHBACK_CHARGE_ENABLED
@pytest.mark.config(GROCERY_P13N_CASHBACK_COMPLEMENT_PAYMENT_TYPES=['card'])
@pytest.mark.parametrize(
    'ip_address, country_iso2_by_ip',
    [('95.220.20.20', 'ru'), ('2.55.77.77', 'il')],
)
async def test_disabling_cashback_by_ip(
        taxi_grocery_p13n, billing_wallet, ip_address, country_iso2_by_ip,
):
    """ /cashback-info should return 404
    if experiment is disabled by ip address """

    wallet_id = 'some-wallet-id'
    balance = '100'

    yandex_uid = headers.DEFAULT_HEADERS['X-Yandex-UID']
    billing_wallet.check_balances(yandex_uid=yandex_uid)
    billing_wallet.mock_balances(
        balances=[
            {'wallet_id': wallet_id, 'amount': balance, 'currency': 'RUB'},
        ],
    )

    request_body = {'depot': depot.DEPOT}
    request_headers = {'X-Remote-IP': ip_address, **headers.DEFAULT_HEADERS}
    response = await taxi_grocery_p13n.post(
        path='/internal/v1/p13n/v1/cashback-info',
        json=request_body,
        headers=request_headers,
    )
    response_data = response.json()

    assert country_iso2_by_ip in ['ru', 'il']
    if country_iso2_by_ip == 'ru':
        assert response.status_code == 200
        assert response_data == {
            'balance': balance,
            'complement_payment_types': ['card'],
            'wallet_id': wallet_id,
        }
    else:
        assert response.status_code == 404
        assert response_data['code'] == 'DISABLED_BY_EXPERIMENT'
