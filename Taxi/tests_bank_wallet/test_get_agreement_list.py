import pytest

from tests_bank_wallet import common


def make_agreements():
    return [
        {
            'agreement_id': '1',
            'currency': 'RUB',
            'buid': '1',
            'public_agreement_id': 'pub_1',
            'product': 'WALLET',
            'created_at': '2020-08-02T00:00:00+00:00',
        },
        {
            'agreement_id': '2',
            'currency': 'RUB',
            'buid': '1',
            'public_agreement_id': 'pub_2',
            'product': 'KYC',
            'created_at': '2020-08-01T00:00:00+00:00',
        },
    ]


def make_cards():
    return [
        {
            'public_card_id': '1',
            'cardholder_name': 'MASTER ACCOUNT',
            'bin': '1',
            'last_pan_digits': '1',
            'exp_month': 10,
            'exp_year': 2022,
            'payment_system': 'VISA',
            'status': 'ACTIVE',
            'tokens': [],
            'public_agreement_id': 'pub_1',
        },
        {
            'public_card_id': '2',
            'cardholder_name': 'JOHN DOE',
            'bin': '2',
            'last_pan_digits': '2',
            'exp_month': 10,
            'exp_year': 2022,
            'payment_system': 'MASTERCARD',
            'status': 'ACTIVE',
            'tokens': [],
            'public_agreement_id': 'pub_2',
        },
    ]


async def test_ok(taxi_bank_wallet, core_agreement_mock, core_card_mock):
    core_agreement_mock.set_agreements(make_agreements())
    core_card_mock.set_cards(make_cards())
    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_agreement_list',
        headers=common.get_headers(),
        json={},
    )

    assert resp.status_code == 200
    assert resp.json() == {
        'agreements': [
            {
                'accessors': [{'accessor_id': '1'}],
                'agreement_id': 'pub_1',
                'product': 'WALLET',
            },
            {
                'accessors': [{'accessor_id': '2'}],
                'agreement_id': 'pub_2',
                'product': 'KYC',
            },
        ],
    }


async def test_empty_agreements(
        taxi_bank_wallet, core_agreement_mock, core_card_mock,
):
    core_card_mock.set_cards(make_cards())
    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_agreement_list',
        headers=common.get_headers(),
        json={},
    )

    assert resp.status_code == 200
    assert resp.json() == {'agreements': []}


async def test_empty_cards(
        taxi_bank_wallet, core_agreement_mock, core_card_mock,
):
    core_agreement_mock.set_agreements(make_agreements())
    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_agreement_list',
        headers=common.get_headers(),
        json={},
    )

    assert resp.status_code == 200
    assert resp.json() == {
        'agreements': [
            {'accessors': [], 'agreement_id': 'pub_1', 'product': 'WALLET'},
            {'accessors': [], 'agreement_id': 'pub_2', 'product': 'KYC'},
        ],
    }


async def test_sort_agreements_by_date(
        taxi_bank_wallet, core_agreement_mock, core_card_mock,
):
    agreements = make_agreements()
    agreements[1]['product'] = 'WALLET'
    agreements[0], agreements[1] = agreements[1], agreements[0]
    core_agreement_mock.set_agreements(agreements)
    core_card_mock.set_cards(make_cards())
    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_agreement_list',
        headers=common.get_headers(),
        json={},
    )

    assert resp.status_code == 200
    assert resp.json() == {
        'agreements': [
            {
                'accessors': [{'accessor_id': '1'}],
                'agreement_id': 'pub_1',
                'product': 'WALLET',
            },
            {
                'accessors': [{'accessor_id': '2'}],
                'agreement_id': 'pub_2',
                'product': 'WALLET',
            },
        ],
    }


@pytest.mark.config(
    BANK_WALLET_APP_TO_PRODUCT_MAPPING={
        '__default__': 'WALLET',
        'kyc_app': 'KYC',
    },
)
async def test_sort_agreements_by_product(
        taxi_bank_wallet, core_agreement_mock, core_card_mock,
):
    core_agreement_mock.set_agreements(make_agreements())
    core_card_mock.set_cards(make_cards())
    headers = common.get_headers()
    headers.update({'X-Request-Application': 'app_name=kyc_app'})
    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_agreement_list', headers=headers, json={},
    )

    assert resp.status_code == 200
    assert resp.json() == {
        'agreements': [
            {
                'accessors': [{'accessor_id': '2'}],
                'agreement_id': 'pub_2',
                'product': 'KYC',
            },
            {
                'accessors': [{'accessor_id': '1'}],
                'agreement_id': 'pub_1',
                'product': 'WALLET',
            },
        ],
    }


async def test_core_card_500(
        taxi_bank_wallet, core_agreement_mock, core_card_mock,
):
    core_card_mock.set_response_code(500)
    core_agreement_mock.set_agreements(make_agreements())
    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_agreement_list',
        headers=common.get_headers(),
        json={},
    )

    assert resp.status_code == 500
    assert core_card_mock.card_list_handler.has_calls
    assert core_agreement_mock.agreements_list_handler.has_calls


async def test_core_agreement_500(
        taxi_bank_wallet, core_agreement_mock, core_card_mock,
):
    core_agreement_mock.set_response_code(500)
    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_agreement_list',
        headers=common.get_headers(),
        json={},
    )

    assert resp.status_code == 500
    assert core_card_mock.card_list_handler.has_calls
    assert core_agreement_mock.agreements_list_handler.has_calls


async def test_fallback_without_date(
        taxi_bank_wallet, core_agreement_mock, core_card_mock,
):
    agreements = make_agreements()
    agreements[0].pop('created_at')
    agreements[1].pop('created_at')
    core_agreement_mock.set_agreements(agreements)
    core_card_mock.set_cards(make_cards())
    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_agreement_list',
        headers=common.get_headers(),
        json={},
    )

    assert resp.status_code == 200
    assert resp.json() == {
        'agreements': [
            {
                'accessors': [{'accessor_id': '1'}],
                'agreement_id': 'pub_1',
                'product': 'WALLET',
            },
            {
                'accessors': [{'accessor_id': '2'}],
                'agreement_id': 'pub_2',
                'product': 'KYC',
            },
        ],
    }


async def test_fallback_without_card_agreement(
        taxi_bank_wallet, core_agreement_mock, core_card_mock,
):
    core_agreement_mock.set_agreements(make_agreements())
    cards = make_cards()
    cards[0].pop('public_agreement_id')
    cards[1].pop('public_agreement_id')
    core_card_mock.set_cards(cards)
    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_agreement_list',
        headers=common.get_headers(),
        json={},
    )

    assert resp.status_code == 200
    assert resp.json() == {
        'agreements': [
            {
                'accessors': [{'accessor_id': '1'}, {'accessor_id': '2'}],
                'agreement_id': 'pub_1',
                'product': 'WALLET',
            },
            {'accessors': [], 'agreement_id': 'pub_2', 'product': 'KYC'},
        ],
    }
