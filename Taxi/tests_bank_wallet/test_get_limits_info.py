# flake8: noqa
# pylint: disable=import-error,wildcard-import
from bank_wallet_plugins.generated_tests import *

import pytest

from tests_bank_wallet import common


def check_all_handlers(
        bank_applications_mock,
        bank_core_client_mock,
        bank_core_statement_mock,
):
    assert bank_applications_mock.get_applications_handler.has_calls
    assert bank_core_client_mock.get_user_status_handler.has_calls
    assert bank_core_statement_mock.wallet_id_get_handler.has_calls
    assert bank_core_statement_mock.wallets_balance_handler.has_calls
    assert bank_core_statement_mock.transaction_list_handler.has_calls


@pytest.mark.parametrize(
    'header',
    [
        'X-Yandex-BUID',
        'X-Yandex-UID',
        'X-YaBank-PhoneID',
        'X-YaBank-SessionUUID',
    ],
)
async def test_get_limits_info_no_one_of_required_headers(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
        header,
):
    headers = common.get_headers()
    headers.pop(header)

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=headers, json={},
    )

    assert resp.status_code == 401


async def test_get_limits_info_bank_applications_400(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
):
    bank_applications_mock.needed_error_code = 400

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    assert bank_applications_mock.get_applications_handler.has_calls
    assert resp.status_code == 500


async def test_get_limits_info_user_info_status_not_found(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
):

    bank_core_client_mock.needed_error_code = 404

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    assert bank_applications_mock.get_applications_handler.has_calls
    assert bank_core_client_mock.get_user_status_handler.has_calls
    assert resp.status_code == 404


async def test_get_limits_info_wallet_ids_not_found(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
):

    bank_core_client_mock.user_status = 'ANONYMOUS'
    bank_core_statement_mock.needed_error_code = 404

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    assert bank_applications_mock.get_applications_handler.has_calls
    assert bank_core_client_mock.get_user_status_handler.has_calls
    assert bank_core_statement_mock.wallet_id_get_handler.has_calls
    assert resp.status_code == 404


async def test_get_limits_info_wallet_ids_more_than_one(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
):

    bank_core_client_mock.user_status = 'ANONYMOUS'
    bank_core_statement_mock.wallet_ids_count = 2

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    assert bank_applications_mock.get_applications_handler.has_calls
    assert bank_core_client_mock.get_user_status_handler.has_calls
    assert bank_core_statement_mock.wallet_id_get_handler.has_calls
    assert resp.status_code == 500


async def test_get_limits_info_wallet_balance_invalid_currency(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
):

    bank_core_client_mock.user_status = 'ANONYMOUS'
    bank_core_statement_mock.wallet_ids_count = 1
    bank_core_statement_mock.balance_currency = 'USD'

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    assert bank_applications_mock.get_applications_handler.has_calls
    assert bank_core_client_mock.get_user_status_handler.has_calls
    assert bank_core_statement_mock.wallet_id_get_handler.has_calls
    assert bank_core_statement_mock.wallets_balance_handler.has_calls
    assert resp.status_code == 500


@pytest.mark.parametrize('auth_level', ['KYC', 'KYC_EDS', 'IDENTIFIED'])
async def test_get_limits_info_wallet_applications_check(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
        auth_level,
):
    application = {
        'application_id': '11111111-1111-1111-1111-111111111111',
        'type': 'SIMPLIFIED_IDENTIFICATION',
        'status': 'SUCCESS',
        'operation_type': 'INSERT',
        'operation_at': '2021-07-31T09:39:34.340633Z',
    }
    bank_applications_mock.applications = {'applications': [application]}
    bank_core_client_mock.user_status = auth_level
    bank_core_statement_mock.wallet_ids_count = 1

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    check_all_handlers(
        bank_applications_mock,
        bank_core_client_mock,
        bank_core_statement_mock,
    )
    assert resp.status_code == 200
    assert resp.json()['user_status'] == auth_level
    applications = resp.json()['applications']
    assert len(applications) == 1
    assert applications[0] == {
        'application_id': application['application_id'],
        'type': application['type'],
        'status': application['status'],
    }


async def test_get_limits_info_wallet_app_status_created(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
):
    application_created = {
        'application_id': '11111111-1111-1111-1111-111111111111',
        'type': 'SIMPLIFIED_IDENTIFICATION',
        'status': 'CREATED',
        'operation_type': 'INSERT',
        'operation_at': '2021-07-31T09:39:34.340633Z',
    }
    bank_applications_mock.applications = {
        'applications': [application_created],
    }
    bank_core_client_mock.user_status = 'KYC'
    bank_core_statement_mock.wallet_ids_count = 1

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    check_all_handlers(
        bank_applications_mock,
        bank_core_client_mock,
        bank_core_statement_mock,
    )
    assert resp.status_code == 200
    assert resp.json()['user_status'] == 'KYC'
    applications = resp.json()['applications']
    assert not applications


async def test_get_limits_info_balance_amount_check(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
):
    balance_amount = '5000'
    remaining_amount = '12000'
    bank_wallet_max_anonymous_limit = '15000'

    bank_core_client_mock.user_status = 'ANONYMOUS'
    bank_core_statement_mock.wallet_ids_count = 1
    bank_core_statement_mock.balance_amount = balance_amount
    bank_core_statement_mock.remaining_amount = remaining_amount
    bank_core_statement_mock.threshold_amount = bank_wallet_max_anonymous_limit

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    check_all_handlers(
        bank_applications_mock,
        bank_core_client_mock,
        bank_core_statement_mock,
    )
    assert resp.status_code == 200
    resp_json = resp.json()
    assert resp_json['user_status'] == 'ANONYMOUS'
    assert resp_json['balance']['currency'] == 'RUB'
    assert resp_json['balance']['amount'] == balance_amount


async def test_get_limits_info_spend_limit_amount_check(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
):
    balance_amount = '5000'
    remaining_amount = '12000'
    bank_wallet_max_anonymous_limit = '15000'

    bank_core_client_mock.user_status = 'ANONYMOUS'
    bank_core_statement_mock.wallet_ids_count = 1
    bank_core_statement_mock.balance_amount = balance_amount
    bank_core_statement_mock.remaining_amount = remaining_amount
    bank_core_statement_mock.threshold_amount = bank_wallet_max_anonymous_limit

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    check_all_handlers(
        bank_applications_mock,
        bank_core_client_mock,
        bank_core_statement_mock,
    )
    assert resp.status_code == 200
    resp_json = resp.json()
    assert resp_json['user_status'] == 'ANONYMOUS'
    assert resp_json['balance']['currency'] == 'RUB'
    assert resp_json['spend_limit']['amount'] == remaining_amount


@pytest.mark.parametrize('limit_type', ['spend_limit', 'topup_limit'])
@pytest.mark.parametrize('second_period', ['MONTH', 'DAY'])
async def test_get_limits_info_two_spend_or_topup_limits(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
        second_period,
        limit_type,
):
    first_remaining = '12000'
    second_remaining = '11000'

    first_limit = common.build_limit(
        threshold='15000',
        currency='RUB',
        remaining=first_remaining,
        period='MONTH',
    )
    second_limit = common.build_limit(
        threshold='15000',
        currency='RUB',
        remaining=second_remaining,
        period=second_period,
    )
    bank_core_statement_mock.explicit_wallets_specification = [
        common.build_wallet(
            'f0180a66-a339-497e-9572-130f440cc338',
            common.build_balance('5000', 'RUB'),
            [first_limit, second_limit],
            [first_limit, second_limit],
        ),
    ]
    bank_core_statement_mock.wallet_ids_count = 1
    bank_core_client_mock.user_status = 'ANONYMOUS'

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    check_all_handlers(
        bank_applications_mock,
        bank_core_client_mock,
        bank_core_statement_mock,
    )
    assert resp.status_code == 200
    resp_json = resp.json()
    assert resp_json['user_status'] == 'ANONYMOUS'
    assert resp_json['balance']['currency'] == 'RUB'
    if limit_type == 'spend_limit':
        if second_period == 'MONTH':
            assert (
                abs(
                    float(resp_json['spend_limit']['amount'])
                    - min(float(first_remaining), float(second_remaining)),
                )
                < 1e-9
            )
        else:
            assert resp_json['spend_limit']['amount'] == first_remaining
    elif limit_type == 'topup_limit':
        assert (
            abs(
                float(resp_json['topup_limit']['amount'])
                - min(float(first_remaining), float(second_remaining)),
            )
            < 1e-9
        )


async def test_get_limits_info_spend_limit_empty_limits_list(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
):
    bank_core_statement_mock.explicit_wallets_specification = [
        common.build_wallet(
            'f0180a66-a339-497e-9572-130f440cc338',
            common.build_balance('5000', 'RUB'),
            [],
            [
                common.build_limit(
                    threshold='15000',
                    currency='RUB',
                    remaining='11000',
                    period='MONTH',
                ),
            ],
        ),
    ]
    bank_core_statement_mock.wallet_ids_count = 1
    bank_core_client_mock.user_status = 'ANONYMOUS'

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    assert resp.status_code == 500


async def test_get_limits_info_spend_limit_no_period(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
):
    limit = common.build_limit(
        threshold='15000', currency='RUB', remaining='11000', period='MONTH',
    )
    limit.pop('period')
    bank_core_statement_mock.explicit_wallets_specification = [
        common.build_wallet(
            'f0180a66-a339-497e-9572-130f440cc338',
            common.build_balance('5000', 'RUB'),
            [limit],
            [limit],
        ),
    ]
    bank_core_statement_mock.wallet_ids_count = 1
    bank_core_client_mock.user_status = 'ANONYMOUS'

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    assert resp.status_code == 500


async def test_get_limits_info_spend_limit_period_id_day(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
):
    balance_amount = '5000'
    remaining_amount = '12000'
    bank_wallet_max_anonymous_limit = '15000'

    bank_core_client_mock.user_status = 'ANONYMOUS'
    bank_core_statement_mock.wallet_ids_count = 1
    bank_core_statement_mock.balance_amount = balance_amount
    bank_core_statement_mock.remaining_amount = remaining_amount
    bank_core_statement_mock.threshold_amount = bank_wallet_max_anonymous_limit
    bank_core_statement_mock.wallet_period = 'DAY'

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    assert resp.status_code == 500


async def test_get_limits_info_topup_amount_check(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
):
    balance_amount = '5000'
    remaining_amount = '12000'
    bank_wallet_max_anonymous_limit = '15000'

    bank_core_client_mock.user_status = 'ANONYMOUS'
    bank_core_statement_mock.wallet_ids_count = 1
    bank_core_statement_mock.balance_amount = balance_amount
    bank_core_statement_mock.remaining_amount = remaining_amount
    bank_core_statement_mock.threshold_amount = bank_wallet_max_anonymous_limit

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    check_all_handlers(
        bank_applications_mock,
        bank_core_client_mock,
        bank_core_statement_mock,
    )
    assert resp.status_code == 200
    resp_json = resp.json()
    assert resp_json['user_status'] == 'ANONYMOUS'
    assert resp_json['balance']['currency'] == 'RUB'
    assert resp_json['topup_limit']['amount'] == remaining_amount


@pytest.mark.parametrize('transactions_cnt', [0, 1])
async def test_get_limits_info_user_has_transactions_check(
        taxi_bank_wallet,
        bank_core_client_mock,
        bank_applications_mock,
        bank_core_statement_mock,
        transactions_cnt,
):

    bank_core_client_mock.user_status = 'ANONYMOUS'
    bank_core_statement_mock.wallet_ids_count = 1
    bank_core_statement_mock.transactions_count = transactions_cnt

    resp = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_limits_info', headers=common.get_headers(), json={},
    )

    check_all_handlers(
        bank_applications_mock,
        bank_core_client_mock,
        bank_core_statement_mock,
    )
    assert resp.status_code == 200
    assert resp.json()['user_status'] == 'ANONYMOUS'
    assert resp.json()['user_has_transactions'] == bool(transactions_cnt)
