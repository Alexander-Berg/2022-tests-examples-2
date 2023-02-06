import uuid

import pytest

from tests_bank_transfers import common
from tests_bank_transfers import db_helpers


async def test_not_in_transfer_exp(taxi_bank_transfers):
    params = {'agreement_id': common.TEST_AGREEMENT_ID}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=common.build_headers(),
        json=params,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'User not in experiment',
    }


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
async def test_not_in_me2me_transfer_exp(taxi_bank_transfers):
    params = {
        'agreement_id': common.TEST_AGREEMENT_ID,
        'transfer_type': 'ME2ME',
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=common.build_headers(),
        json=params,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'User not in me2me experiment',
    }


@pytest.mark.parametrize(
    'headers',
    [
        ({}),
        (
            {
                'X-YaBank-SessionUUID': common.TEST_SESSION_UUID,
                'X-Yandex-UID': common.TEST_YANDEX_UID,
                'X-YaBank-PhoneID': common.TEST_PHONE_ID,
                'X-Request-Language': common.TEST_LOCALE,
            }
        ),
    ],
)
@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
async def test_not_authorized(taxi_bank_transfers, headers):
    params = {'agreement_id': common.TEST_AGREEMENT_ID}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=headers,
        json=params,
    )
    assert response.status_code == 401


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.parametrize('params', [({}), ({'extra_field': 'extra_data'})])
async def test_no_agreement_id(taxi_bank_transfers, params):
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=common.build_headers(),
        params=params,
    )
    assert response.status_code == 400


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
async def test_agreement_id_not_found(taxi_bank_transfers):
    params = {'agreement_id': '51a14770-8a69-4c22-9e82-6fa145cc7d6b'}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
async def test_core_statement_error(taxi_bank_transfers, mockserver):
    @mockserver.json_handler('/bank-core-statement/v1/agreements/balance/get')
    def _mock_get_transaction(request):
        return mockserver.make_response(status=500)

    params = {'agreement_id': common.TEST_AGREEMENT_ID}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 500


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
@pytest.mark.parametrize('transfer_type', ['C2C', 'ME2ME', None])
async def test_ok(taxi_bank_transfers, pgsql, transfer_type):
    params = {'agreement_id': common.TEST_AGREEMENT_ID}
    if transfer_type:
        params['transfer_type'] = transfer_type
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    test_max_limit = str(min(common.AGREEMENT_BALANCE, *common.DEBIT_LIMITS))
    assert response.json()['max_limit']['money']['amount'] == test_max_limit
    transfer = db_helpers.select_transfer(
        pgsql, response.json()['transfer_id'],
    )
    assert transfer.bank_uid == common.TEST_BANK_UID
    assert transfer.agreement_id == common.TEST_AGREEMENT_ID
    assert transfer.status == 'CREATED'
    assert transfer.max_limit == test_max_limit
    excepted_transfer_type = (
        transfer_type if transfer_type is not None else 'C2C'
    )
    assert transfer.transfer_type == excepted_transfer_type
    if transfer_type == 'ME2ME':
        assert transfer.receiver_phone == common.RECEIVER_PHONE_1
    else:
        assert not transfer.receiver_phone
    transfer_history = db_helpers.select_transfer_history(
        pgsql, response.json()['transfer_id'],
    )
    assert len(transfer_history) == 1
    assert transfer_history[0].transfer_type == excepted_transfer_type


@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.parametrize(
    'buid',
    [
        common.TEST_BANK_UID,
        str(uuid.uuid4()),
        common.TEST_ABSENT_IN_USERINFO_BUID,
    ],
)
async def test_fps(taxi_bank_transfers, buid):
    params = {'agreement_id': common.TEST_AGREEMENT_ID}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=common.build_headers(buid=buid),
        json=params,
    )
    assert response.status_code == 200
    assert response.json()['fps_on'] == (buid == common.TEST_BANK_UID)


@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.parametrize(
    'min_limit, description',
    [
        ('balance', 'Недостаточно средств на счёте'),
        (
            'transaction',
            'Нельзя переводить более 500\xa0\u20BD за одну операцию',
        ),
        ('month', 'Больше возможного в этом месяце'),
        ('no_code', 'Больше возможного в этом месяце'),
    ],
)
async def test_max_limit_text(
        taxi_bank_transfers,
        bank_core_statement_mock,
        pgsql,
        min_limit,
        description,
):
    if min_limit == 'balance':
        bank_core_statement_mock.set_balance(500)
    elif min_limit == 'transaction':
        bank_core_statement_mock.set_transaction_limit(500)
    elif min_limit == 'month':
        bank_core_statement_mock.set_month_limit(500)
    else:
        bank_core_statement_mock.set_limit_without_code(500)

    params = {'agreement_id': common.TEST_AGREEMENT_ID}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    test_max_limit = str(
        min(
            bank_core_statement_mock.balance,
            *bank_core_statement_mock.debit_limits,
        ),
    )
    assert response.json()['max_limit']['money']['amount'] == test_max_limit
    assert response.json()['max_limit']['description'] == description
    transfer = db_helpers.select_transfer(
        pgsql, response.json()['transfer_id'],
    )
    assert transfer.bank_uid == common.TEST_BANK_UID
    assert transfer.agreement_id == common.TEST_AGREEMENT_ID
    assert transfer.status == 'CREATED'
    assert transfer.max_limit == test_max_limit


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.parametrize('transfer_type', ['C2C', 'ME2ME', None])
async def test_not_core_info_for_buid(taxi_bank_transfers, transfer_type):
    params = {'agreement_id': common.TEST_AGREEMENT_ID}
    if transfer_type:
        params['transfer_type'] = transfer_type
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=common.build_headers(buid='bad_buid'),
        json=params,
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.parametrize('transfer_type', ['C2C', 'ME2ME', None])
async def test_anonymous(
        taxi_bank_transfers, transfer_type, bank_core_client_mock,
):
    params = {'agreement_id': common.TEST_AGREEMENT_ID}
    bank_core_client_mock.set_auth_level('ANONYMOUS')
    if transfer_type:
        params['transfer_type'] = transfer_type
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
async def test_pass_type_instead_transfer_type(taxi_bank_transfers, pgsql):
    params = {'agreement_id': common.TEST_AGREEMENT_ID, 'type': 'кириллица'}
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 200
    transfer = db_helpers.select_transfer(
        pgsql, response.json()['transfer_id'],
    )
    assert transfer.transfer_type == 'C2C'
