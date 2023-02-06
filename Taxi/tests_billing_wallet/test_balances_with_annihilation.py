# pylint: disable=too-many-lines
import copy
import datetime as dt

import pytest

_CACHE_ENABLED = pytest.mark.config(BILLING_WALLET_BALANCES_CACHE=1.0)
_ANNIHILATION_ENABLED = pytest.mark.config(
    CASHBACK_START_ANNIHILATION_DATE={
        'enabled': True,
        'general_annihilation_date': '2020-01-01T00:00:00Z',
    },
)
_CACHE_UPDATE_ENABLED = pytest.mark.config(
    BILLING_WALLET_BALANCES_CACHE_UPDATE_PROB=1.0,
)
_SMALL_CACHE_TTL = pytest.mark.config(
    BILLING_WALLET_BALANCES_CACHE_TTL=2764800,
)
_FALLBACK_ENABLED = pytest.mark.config(
    BILLING_WALLET_ENABLE_BALANCES_CACHE_FALLBACK=True,
)
_VALUE_IN_CACHE = {
    '_id': 'uid',
    'version': 1,
    'updated_at': dt.datetime(2020, 1, 1),
    'balances': [
        {
            'wallet_id': 'existing',
            'amount': '100.0',
            'currency': 'RUB',
            'sub_account': 'deposit',
            'last_entry_id': 1,
        },
    ],
    'annihilations': [
        {'amount': '100.0', 'version': 1, 'wallet_id': 'existing'},
    ],
}
_CHANGED_VALUE_IN_CACHE = {
    '_id': 'uid',
    'version': 2,
    'updated_at': dt.datetime(2020, 2, 2),
    'balances': [
        {
            'wallet_id': 'existing',
            'amount': '120.0000',
            'currency': 'RUB',
            'sub_account': 'deposit',
            'last_entry_id': 90001,
        },
    ],
    'annihilations': [
        {'amount': '100.0', 'version': 1, 'wallet_id': 'existing'},
    ],
}
_CHANGED_AGAIN_VALUE_IN_CACHE = {
    '_id': 'uid-with-rarely-updated-balance',
    'version': 3,
    'updated_at': dt.datetime(2020, 2, 2),
    'balances': [
        {
            'wallet_id': 'rarely-updated',
            'amount': '120.0000',
            'currency': 'RUB',
            'sub_account': 'deposit',
            'last_entry_id': 90001,
        },
    ],
    'annihilations': [
        {
            'amount': '200.0',
            'version': 1,
            'wallet_id': 'existing',
            'at': dt.datetime(2022, 1, 1),
        },
    ],
}

_NEW_VALUE_IN_CACHE = {
    '_id': 'not_cached_uid',
    'version': 1,
    'updated_at': dt.datetime(2020, 1, 1),
    'balances': [
        {
            'wallet_id': 'existing',
            'amount': '100.0000',
            'currency': 'RUB',
            'sub_account': 'deposit',
            'last_entry_id': 6000000000,
        },
    ],
}


_EMPTY_VALUE_IN_CACHE = {
    '_id': 'not_cached_uid',
    'version': 1,
    'updated_at': dt.datetime(2020, 1, 1),
    'balances': [],
}


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.config(
    BILLING_WALLET_BALANCES_CACHE_SECONDARY_PARAMS={'max_staleness': 3600},
    BILLING_WALLET_BALANCES_CACHE_TTL=2851200,
)
@pytest.mark.servicetest
@pytest.mark.parametrize(
    'balance_request, balances_select_request, balances_select_response,'
    'cache_side_effect, expected_response, expected_cache',
    [
        pytest.param(
            {'wallet_id': 'non-existing', 'yandex_uid': 'uid'},
            {
                'accounts': [
                    {
                        'agreement_id': 'non-existing',
                        'entity_external_id': 'wallet_id/uid',
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [],
            None,
            {'balances': []},
            _VALUE_IN_CACHE,
            marks=[_ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'uid'},
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
                        'agreement_id': 'existing',
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
                {
                    'account': {
                        'account_id': 5000000001,
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'wallet/yataxi',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '200.0',
                            'last_entry_id': 7000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '0.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _VALUE_IN_CACHE,
            marks=[_ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'not_cached_uid'},
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/not_cached_uid',
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
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'agreement_id': 'existing',
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
                {
                    'account': {
                        'account_id': 5000000001,
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'agreement_id': 'wallet/yataxi',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '200.0',
                            'last_entry_id': 7000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '100.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _NEW_VALUE_IN_CACHE,
            marks=[_CACHE_ENABLED, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'not_cached_uid', 'wallet_id': 'non-existing'},
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'sub_account': 'deposit',
                        'agreement_id': 'non-existing',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'agreement_id': 'existing',
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
                {
                    'account': {
                        'account_id': 5000000001,
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'agreement_id': 'wallet/yataxi',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '200.0',
                            'last_entry_id': 7000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '100.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            None,
            marks=[_CACHE_ENABLED, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'not_cached_uid'},
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/not_cached_uid',
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
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'agreement_id': 'existing',
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
                {
                    'account': {
                        'account_id': 5000000001,
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'agreement_id': 'wallet/yataxi',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '200.0',
                            'last_entry_id': 7000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            'insert',
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '100.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _NEW_VALUE_IN_CACHE,
            marks=[_CACHE_ENABLED, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'not_cached_uid'},
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [],
            None,
            {'balances': []},
            _EMPTY_VALUE_IN_CACHE,
            marks=[_CACHE_ENABLED, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'uid'},
            None,
            None,
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '0.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _VALUE_IN_CACHE,
            marks=[_CACHE_ENABLED, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'uid', 'wallet_id': 'existing'},
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'existing',
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
                        'agreement_id': 'existing',
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
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '0.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _VALUE_IN_CACHE,
            marks=[_ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'not_cached_uid'},
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/not_cached_uid',
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
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'agreement_id': 'existing',
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
                {
                    'account': {
                        'account_id': 5000000001,
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'agreement_id': 'wallet/yataxi',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '200.0',
                            'last_entry_id': 7000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '100.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _NEW_VALUE_IN_CACHE,
            id=(
                'Cache is updated when cache update is enabled but cache '
                'usage is disabled'
            ),
            marks=[_CACHE_UPDATE_ENABLED, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'not_cached_uid'},
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/not_cached_uid',
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
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'agreement_id': 'existing',
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
                {
                    'account': {
                        'account_id': 5000000001,
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'agreement_id': 'wallet/yataxi',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '200.0',
                            'last_entry_id': 7000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            'insert',
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '100.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _NEW_VALUE_IN_CACHE,
            id=(
                'Duplicate key error is handled when cache update is enabled '
                'but cache fetch is disabled'
            ),
            marks=[_CACHE_UPDATE_ENABLED, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'uid', 'wallet_id': 'existing'},
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'existing',
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
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '300.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '200.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _VALUE_IN_CACHE,
            marks=[_CACHE_ENABLED, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'uid'},
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
                        'agreement_id': 'existing',
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
                {
                    'account': {
                        'account_id': 5000000001,
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'wallet/yataxi',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '200.0',
                            'last_entry_id': 7000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '0.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _VALUE_IN_CACHE,
            id='Only comparison is enabled, return value from accounts',
            marks=[_CACHE_UPDATE_ENABLED, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'uid'},
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
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 1,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
                {
                    'account': {
                        'account_id': 5000000001,
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'wallet/yataxi',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '201.0',
                            'last_entry_id': 1,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '0.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _VALUE_IN_CACHE,
            id='Only comparison is enabled, return value from accounts',
            marks=[_CACHE_UPDATE_ENABLED, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'uid'},
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
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '120.0000',
                            'last_entry_id': 90001,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '20.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _CHANGED_VALUE_IN_CACHE,
            id=(
                'Usage is disabled, writing to cache is enabled. Cached value '
                'is old, update it and return result from accounts'
            ),
            marks=[
                _CACHE_UPDATE_ENABLED,
                _SMALL_CACHE_TTL,
                _ANNIHILATION_ENABLED,
            ],
        ),
        pytest.param(
            {'yandex_uid': 'uid'},
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
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '120.0000',
                            'last_entry_id': 90001,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '20.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _CHANGED_VALUE_IN_CACHE,
            id=(
                'Usage is enabled but cached value is old, update it and '
                'return result from accounts'
            ),
            marks=[_CACHE_ENABLED, _SMALL_CACHE_TTL, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'uid-with-rarely-updated-balance'},
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'wallet_id/uid-with-rarely-updated-balance'
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
                            'wallet_id/uid-with-rarely-updated-balance'
                        ),
                        'agreement_id': 'rarely-updated',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '120.0000',
                            'last_entry_id': 90001,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'rarely-updated',
                        'amount': '120.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _CHANGED_AGAIN_VALUE_IN_CACHE,
            id=(
                'Usage is enabled but cached value is old, update it and '
                'return result from accounts. Use version from DB for update'
            ),
            marks=[_CACHE_ENABLED, _SMALL_CACHE_TTL, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'uid'},
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
            None,
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '0.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _VALUE_IN_CACHE,
            id=(
                'Usage is enabled but cached value is old. Return cached '
                'value anyway and don\'t update it, because fallback is '
                'enabled'
            ),
            marks=[
                _CACHE_ENABLED,
                _SMALL_CACHE_TTL,
                _FALLBACK_ENABLED,
                _ANNIHILATION_ENABLED,
            ],
        ),
        pytest.param(
            {'yandex_uid': 'not_cached_uid'},
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            None,
            None,
            {'balances': []},
            None,
            id=(
                'Usage is enabled, cache is empty. Since fallback is enabled, '
                'return empty balances and don\'t update cache'
            ),
            marks=[_CACHE_ENABLED, _FALLBACK_ENABLED, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'uid'},
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
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '120.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '20.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _VALUE_IN_CACHE,
            id=(
                'Test that fallback config is ignored when both usage and '
                'cache update are disabled. We won\'t read from cache & '
                'won\'t update it'
            ),
            marks=[_FALLBACK_ENABLED, _ANNIHILATION_ENABLED],
        ),
        pytest.param(
            {'yandex_uid': 'not_cached_uid'},
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/not_cached_uid',
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
                        'entity_external_id': 'wallet_id/not_cached_uid',
                        'agreement_id': 'existing',
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
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '100.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _NEW_VALUE_IN_CACHE,
            id=(
                'Test that fallback config is ignored when usage is disabled '
                'and cache update is enabled. We will read from cache & '
                'update it, but will return value from accounts'
            ),
            marks=[
                _CACHE_UPDATE_ENABLED,
                _FALLBACK_ENABLED,
                _ANNIHILATION_ENABLED,
            ],
        ),
        pytest.param(
            {'yandex_uid': 'uid', 'wallet_id': 'existing'},
            {
                'accounts': [
                    {
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'existing',
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
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-02T00:00:00+00:00',
                            'balance': '42.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            None,
            {
                'balances': [
                    {
                        'wallet_id': 'existing',
                        'amount': '0.0000',
                        'currency': 'RUB',
                    },
                ],
            },
            _VALUE_IN_CACHE,
            id='Test that cache update disabled when wallet_id specified',
            marks=[
                _CACHE_ENABLED,
                _CACHE_UPDATE_ENABLED,
                _SMALL_CACHE_TTL,
                _ANNIHILATION_ENABLED,
            ],
        ),
    ],
)
async def test_balances(
        taxi_billing_wallet,
        mockserver,
        mongodb,
        balance_request,
        balances_select_request,
        balances_select_response,
        cache_side_effect,
        expected_response,
        expected_cache,
):
    @mockserver.json_handler('/billing-accounts/v2/balances/select')
    def _balances_select(request):
        assert request.json == balances_select_request
        if cache_side_effect == 'insert':
            mongodb.wallet_balances.insert(_NEW_VALUE_IN_CACHE)
        return balances_select_response

    response = await taxi_billing_wallet.post('balances', json=balance_request)
    if balances_select_response is None:
        assert not _balances_select.has_calls
    else:
        assert _balances_select.has_calls
    assert response.json() == expected_response
    cache = mongodb.wallet_balances.find_one(
        {'_id': balance_request['yandex_uid']},
    )
    assert _only_value_fields(cache) == _only_value_fields(expected_cache)


def _only_value_fields(cache):
    if cache is None:
        return None
    result = copy.deepcopy(cache)
    del result['updated_at']
    return result
