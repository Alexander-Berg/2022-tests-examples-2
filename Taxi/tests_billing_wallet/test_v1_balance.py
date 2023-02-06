import copy
import datetime as dt

import pytest

_VALUE_IN_CACHE = {
    '_id': 'uid',
    'version': 1,
    'updated_at': dt.datetime(2020, 1, 1),
    'balances': [],
}
_VALUE_IN_CACHE_UID_EA = {
    '_id': 'uid-with-exists-annihilation',
    'annihilations': [
        {'amount': '100.0', 'version': 1, 'wallet_id': 'exists_wallet_id'},
    ],
    'balances': [],
    'updated_at': {'$date': '2020-01-01T00:00:00.0'},
    'version': 2,
}
_CHANGED_VALUE_IN_CACHE = {
    '_id': 'uid',
    'version': 2,
    'updated_at': dt.datetime(2020, 2, 2),
    'annihilations': [
        {'amount': '42.4200', 'version': 1, 'wallet_id': 'wallet_id'},
    ],
    'balances': [],
}
_CHANGED_VALUE_IN_CACHE_DT = {
    '_id': 'uid',
    'version': 2,
    'updated_at': dt.datetime(2020, 2, 2),
    'annihilations': [
        {
            'amount': '42.4200',
            'version': 1,
            'wallet_id': 'wallet_id',
            'at': dt.datetime(2045, 2, 1, 21, 0, 13),
        },
    ],
    'balances': [],
}
_NEW_VALUE_IN_CACHE = {
    '_id': 'uid_new',
    'version': 1,
    'updated_at': dt.datetime(2020, 2, 2),
    'annihilations': [
        {
            'amount': '42.4200',
            'version': 1,
            'wallet_id': 'wallet_id',
            'at': dt.datetime(2045, 2, 1, 21, 0, 13),
        },
    ],
    'balances': [
        {
            'wallet_id': 'wallet_id',
            'amount': '100.0000',
            'currency': 'RUB',
            'sub_account': 'deposit',
            'last_entry_id': 6000000000,
        },
    ],
}
_CHANGED_VALUE_IN_CACHE_UID_EA_DATE = {
    '_id': 'uid-with-exists-annihilation',
    'annihilations': [
        {
            'amount': '42.4200',
            'version': 2,
            'wallet_id': 'exists_wallet_id',
            'at': dt.datetime(2045, 2, 1, 21, 0, 13),
        },
    ],
    'balances': [
        {
            'wallet_id': 'exists_wallet_id',
            'amount': '100.0000',
            'currency': 'RUB',
            'sub_account': 'deposit',
            'last_entry_id': 6000000000,
        },
    ],
    'updated_at': {'$date': '2020-01-01T00:00:00.0'},
    'version': 3,
}
_CHANGED_VALUE_IN_CACHE_UID_EB_DATE = {
    '_id': 'uid-with-exists-balances',
    'annihilations': [
        {
            'amount': '42.4200',
            'version': 2,
            'wallet_id': 'exists_wallet_id',
            'at': dt.datetime(2045, 2, 1, 21, 0, 13),
        },
    ],
    'balances': [
        {
            'amount': '99.9000',
            'currency': 'RUB',
            'last_entry_id': 1,
            'sub_account': 'deposit',
            'wallet_id': 'existing',
        },
    ],
    'updated_at': {'$date': '2020-01-01T00:00:00.0'},
    'version': 3,
}
_CHANGED_VALUE_IN_CACHE_UID_EB = {
    '_id': 'uid-with-exists-balances',
    'annihilations': [
        {
            'amount': '42.4200',
            'version': 2,
            'wallet_id': 'exists_wallet_id',
            'at': dt.datetime(2045, 2, 1, 21, 0, 13),
        },
    ],
    'balances': [
        {
            'wallet_id': 'exists_wallet_id',
            'amount': '100.0000',
            'currency': 'RUB',
            'sub_account': 'deposit',
            'last_entry_id': 6000000000,
        },
    ],
    'updated_at': {'$date': '2020-01-01T00:00:00.0'},
    'version': 3,
}
_CHANGED_VALUE_IN_CACHE_UID_EA = {
    '_id': 'uid-with-exists-annihilation',
    'annihilations': [
        {'amount': '42.4200', 'version': 2, 'wallet_id': 'exists_wallet_id'},
    ],
    'balances': [
        {
            'wallet_id': 'exists_wallet_id',
            'amount': '100.0000',
            'currency': 'RUB',
            'sub_account': 'deposit',
            'last_entry_id': 6000000000,
        },
    ],
    'updated_at': {'$date': '2020-01-01T00:00:00.0'},
    'version': 3,
}

_LONG_CACHE_TTL = pytest.mark.config(
    BILLING_WALLET_BALANCES_CACHE_TTL=3600 * 24 * 365,
    BILLING_WALLET_ANNIHILATIONS_CACHE_TTL=3600 * 24 * 365,
)


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.parametrize(
    'annihilation_request, expected_status, expected_response, '
    'balances_select_request, balances_select_response, expected_cache',
    [
        (  # new record (no balance update) wc = majority
            {
                'amount': '42.42',
                'at': '2045-02-02T00:00:13+03:00',
                'yandex_uid': 'uid',
                'version': 1,
                'wallet_id': 'wallet_id',
            },
            200,
            {
                'amount': '42.4200',
                'at': '2045-02-01T21:00:13+00:00',
                'yandex_uid': 'uid',
                'version': 1,
                'wallet_id': 'wallet_id',
            },
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/uid',
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'wallet_id',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            _CHANGED_VALUE_IN_CACHE_DT,
        ),
        (  # new wallet (balance update) wc = majority
            {
                'amount': '42.42',
                'at': '2045-02-02T00:00:13+03:00',
                'yandex_uid': 'uid_new',
                'version': 1,
                'wallet_id': 'wallet_id',
            },
            200,
            {
                'amount': '42.4200',
                'at': '2045-02-01T21:00:13+00:00',
                'yandex_uid': 'uid_new',
                'version': 1,
                'wallet_id': 'wallet_id',
            },
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/uid_new',
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': 'wallet_id/uid_new',
                        'agreement_id': 'wallet_id',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            _NEW_VALUE_IN_CACHE,
        ),
        (  # new record with no at (no balance update)
            {
                'amount': '42.42',
                'yandex_uid': 'uid',
                'version': 1,
                'wallet_id': 'wallet_id',
            },
            200,
            {
                'amount': '42.4200',
                'yandex_uid': 'uid',
                'version': 1,
                'wallet_id': 'wallet_id',
            },
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/uid',
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'wallet_id',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            _CHANGED_VALUE_IN_CACHE,
        ),
        (  # fail to update (new record, but version not equal 1)
            # (no balance update)
            {
                'amount': '42.42',
                'at': '2045-02-02T00:00:13+03:00',
                'yandex_uid': 'uid',
                'version': 2,
                'wallet_id': 'wallet_id',
            },
            409,
            {
                'code': 'inconsistent_record',
                'message': 'Try to update incorrect version of annihilation',
            },
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/uid',
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'wallet_id',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            _VALUE_IN_CACHE,
        ),
        (  # update exists record (balance update) wc = majority
            {
                'amount': '42.42',
                'at': '2045-02-02T00:00:13+03:00',
                'yandex_uid': 'uid-with-exists-annihilation',
                'version': 1,
                'wallet_id': 'exists_wallet_id',
            },
            200,
            {
                'amount': '42.4200',
                'at': '2045-02-01T21:00:13+00:00',
                'yandex_uid': 'uid-with-exists-annihilation',
                'version': 2,
                'wallet_id': 'exists_wallet_id',
            },
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'wallet_id/uid-with-exists-annihilation'
                        ),
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': (
                            'wallet_id/uid-with-exists-annihilation'
                        ),
                        'agreement_id': 'exists_wallet_id',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            _CHANGED_VALUE_IN_CACHE_UID_EA_DATE,
        ),
        (  # update exists record (balance update) wc = majority
            {
                'amount': '42.42',
                'at': '2045-02-02T00:00:13+03:00',
                'yandex_uid': 'uid-with-exists-balances',
                'version': 1,
                'wallet_id': 'exists_wallet_id',
            },
            200,
            {
                'amount': '42.4200',
                'at': '2045-02-01T21:00:13+00:00',
                'yandex_uid': 'uid-with-exists-balances',
                'version': 2,
                'wallet_id': 'exists_wallet_id',
            },
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'wallet_id/uid-with-exists-balances'
                        ),
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': (
                            'wallet_id/uid-with-exists-balances'
                        ),
                        'agreement_id': 'exists_wallet_id',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            _CHANGED_VALUE_IN_CACHE_UID_EB,
        ),
        pytest.param(  # update exists record (no balance update) wc = majority
            {
                'amount': '42.42',
                'at': '2045-02-02T00:00:13+03:00',
                'yandex_uid': 'uid-with-exists-balances',
                'version': 1,
                'wallet_id': 'exists_wallet_id',
            },
            200,
            {
                'amount': '42.4200',
                'at': '2045-02-01T21:00:13+00:00',
                'yandex_uid': 'uid-with-exists-balances',
                'version': 2,
                'wallet_id': 'exists_wallet_id',
            },
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'wallet_id/uid-with-exists-balances'
                        ),
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': (
                            'wallet_id/uid-with-exists-balances'
                        ),
                        'agreement_id': 'exists_wallet_id',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            _CHANGED_VALUE_IN_CACHE_UID_EB_DATE,
            marks=[_LONG_CACHE_TTL],
        ),
        # update exists record (balance update) wc = unacknowledged
        pytest.param(
            {
                'amount': '42.42',
                'at': '2045-02-02T00:00:13+03:00',
                'yandex_uid': 'uid-with-exists-annihilation',
                'version': 1,
                'wallet_id': 'exists_wallet_id',
            },
            200,
            {
                'amount': '42.4200',
                'at': '2045-02-01T21:00:13+00:00',
                'yandex_uid': 'uid-with-exists-annihilation',
                'version': 2,
                'wallet_id': 'exists_wallet_id',
            },
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'wallet_id/uid-with-exists-annihilation'
                        ),
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': (
                            'wallet_id/uid-with-exists-annihilation'
                        ),
                        'agreement_id': 'exists_wallet_id',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            _CHANGED_VALUE_IN_CACHE_UID_EA_DATE,
            marks=[
                pytest.mark.config(
                    BILLING_WALLET_ANNIHILATIONS_CACHE_WC='unacknowledged',
                ),
            ],
        ),
        (  # could not update exists record
            {
                'amount': '42.42',
                'at': '2045-02-02T00:00:13+03:00',
                'yandex_uid': 'uid-with-exists-annihilation',
                'version': 2,
                'wallet_id': 'exists_wallet_id',
            },
            409,
            {
                'code': 'inconsistent_record',
                'message': 'Try to update incorrect version of annihilation',
            },
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'wallet_id/uid-with-exists-annihilation'
                        ),
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': (
                            'wallet_id/uid-with-exists-annihilation'
                        ),
                        'agreement_id': 'exists_wallet_id',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            _VALUE_IN_CACHE_UID_EA,
        ),
        (  # update exists record with no at
            {
                'amount': '42.42',
                'yandex_uid': 'uid-with-exists-annihilation',
                'version': 1,
                'wallet_id': 'exists_wallet_id',
            },
            200,
            {
                'amount': '42.4200',
                'yandex_uid': 'uid-with-exists-annihilation',
                'version': 2,
                'wallet_id': 'exists_wallet_id',
            },
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'wallet_id/uid-with-exists-annihilation'
                        ),
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': (
                            'wallet_id/uid-with-exists-annihilation'
                        ),
                        'agreement_id': 'exists_wallet_id',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            _CHANGED_VALUE_IN_CACHE_UID_EA,
        ),
    ],
)
async def test_v1_balance_set_annihilation(
        taxi_billing_wallet,
        annihilation_request,
        expected_status,
        expected_response,
        mockserver,
        mongodb,
        balances_select_request,
        balances_select_response,
        expected_cache,
):
    @mockserver.json_handler('/billing-accounts/v2/balances/select')
    def _balances_select(request):
        assert request.json == balances_select_request
        return balances_select_response

    response = await taxi_billing_wallet.post(
        '/v1/balance/set_pending_annihilation', json=annihilation_request,
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response

    cache = mongodb.wallet_balances.find_one(
        {'_id': annihilation_request['yandex_uid']},
    )
    assert _only_value_fields(cache) == _only_value_fields(expected_cache)


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.parametrize(
    'annihilation_request, expected_status, expected_response',
    [
        (  # no record
            {'yandex_uid': 'uid', 'wallet_id': 'wallet_id'},
            404,
            {'code': 'wallet_not_found', 'message': ''},
        ),
        (  # exists record
            {
                'yandex_uid': 'uid-with-exists-annihilation',
                'wallet_id': 'exists_wallet_id',
            },
            200,
            {'amount': '100.0000', 'version': 1},
        ),
    ],
)
async def test_v1_balance_get_annihilation(
        taxi_billing_wallet,
        annihilation_request,
        expected_status,
        expected_response,
):
    response = await taxi_billing_wallet.post(
        '/v1/balance/get_pending_annihilation', json=annihilation_request,
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response


def _only_value_fields(cache):
    if cache is None:
        return None
    result = copy.deepcopy(cache)
    del result['updated_at']
    return result
