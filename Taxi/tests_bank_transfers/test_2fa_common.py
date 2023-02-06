import datetime
import uuid

import pytest

from tests_bank_transfers import common
from tests_bank_transfers import db_helpers

PRIORITY_BANK_KEY = 'fps_priority_bank'

SET_SETTINGS_REQUEST = '/v1/transfers/v1/settings/set'
CONFIRM_REQUEST = '/v1/transfers/v2/transfer/confirm'
SIMPLIFIED_CONFIRM_REQUEST = '/v1/transfers/v1/transfer/simplified_confirm'

SUPPORT_URL = (
    'https://help-chat.bank.yandex.ru/fintech/yandex/fa/ru_ru/bank/chat'
)


BAD_PAYLOAD_TOKEN = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJQUzUxMiJ9.eyJidWlkIjoiODdlOTJhMmEtMDI5Ni00NzA'
    '4LWI4NjUtODFlMDE5N2NhOTE2IiwidHJhY2tfaWQiOiIzYjE5Nzg0Ni1kMGZjLTRiMzEtOTI'
    '4NS00ODViNTAwNDgzNjYiLCJ2ZXJpZmljYXRpb25fcmVzdWx0IjoiT0sifQ.AXS1Ib9KRU6r'
    'sqyvKJA-gXpx9D6goP_-LJQyBYzajZY_lSex1ifdsnBY2kbs2s6OTCwuwxW29-ArihPSNcoN'
    'MHlwMBSeHEdjvKUkyqKFifnMNwd4ojLP5AFcVbsMvOR2hv6A5AVe68xjZzEPVzxwdTn3AvX5'
    'YpvpBpPY9V5MUwneA0omvXAfqrvOstJhsv0wp90qzzk3FDJ4BORo_Rey7Ypnm8rsWatLAeqR'
    'njYFLSM5KNtz7ORHAc6oY0ogfvYlfzxyCTEWDntWbVVrEEZuxjcm_hcBswsp4JxkgdaAXFFM'
    'CNvCRPJD69Gw9rrwShmeMue9GtbK8ZEN9afFQqgYTQ'
)
BAD_ALGO_TOKEN = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJidWlkIjoiZmY4OTU2OGItYzY2Ny00YmI'
    'wLTlmOTItZGJhYWMwNjcyNzI4IiwidHJhY2tfaWQiOiJkZWZhdWx0X3RyYWNrX2lkIiwidmV'
    'yaWZpY2F0aW9uX3Jlc3VsdCI6Ik9LIn0.nbnLlcWEJPBl5P9xM8ysSRa_uRdBkC7QhBrLpVe'
    '-u27jSGb8vfEbD1U6fs1pEgpi1mapGJ0v44QgQ9stBWsFZg'
)


def get_set_settings_body():
    return {
        'key': PRIORITY_BANK_KEY,
        'property': {'type': 'SWITCH', 'boolean_value': True},
    }


def get_confirm_body(pgsql):
    transfer_id = db_helpers.insert_transfer(
        pgsql, amount=common.DEFAULT_OFFER_AMOUNT,
    )
    offer_id = db_helpers.create_offer(pgsql, transfer_id)
    return {
        'transfer_id': transfer_id,
        'money': {
            'amount': str(common.DEFAULT_OFFER_AMOUNT),
            'currency': 'RUB',
        },
        'offer_id': offer_id,
    }


def prepare_request(request_string, pgsql=None):
    if request_string == SET_SETTINGS_REQUEST:
        return get_set_settings_body()
    if request_string == SIMPLIFIED_CONFIRM_REQUEST:
        return common.build_simplified_confirm_params()
    return get_confirm_body(pgsql)


@pytest.mark.parametrize(
    'verification_token', [BAD_PAYLOAD_TOKEN, BAD_ALGO_TOKEN],
)
@pytest.mark.parametrize(
    'request_string',
    [SET_SETTINGS_REQUEST, CONFIRM_REQUEST, SIMPLIFIED_CONFIRM_REQUEST],
)
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.experiments3(
    filename='bank_transfer_settings_feature_experiments.json',
)
@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
async def test_2fa_with_invalid_v_t(
        taxi_bank_transfers, verification_token, request_string, pgsql,
):
    headers = common.build_headers(
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        verification_token=verification_token,
    )
    body = prepare_request(request_string, pgsql)

    response = await taxi_bank_transfers.post(
        request_string, headers=headers, json=body,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'BadRequest',
        'message': 'Bad jwt verification token',
    }


@pytest.mark.parametrize('request_string', ['/v1/transfers/v1/settings/set'])
@pytest.mark.parametrize('bank_authorization_status_code', [409, 500])
@pytest.mark.experiments3(
    filename='bank_transfer_settings_feature_experiments.json',
)
async def test_2fa_error_from_bank_authorization(
        taxi_bank_transfers,
        bank_authorization_status_code,
        bank_authorization,
        request_string,
):
    headers = common.build_headers(
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    body = prepare_request(request_string)

    bank_authorization.set_http_status_code(bank_authorization_status_code)
    response = await taxi_bank_transfers.post(
        request_string, headers=headers, json=body,
    )

    assert bank_authorization.create_track_handler.times_called == 1
    assert response.status_code == 500


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.parametrize('request_string', [CONFIRM_REQUEST])
async def test_no_vt_data_race(
        taxi_bank_transfers, request_string, testpoint, pgsql,
):
    body = prepare_request(request_string, pgsql)

    @testpoint('data_race')
    async def _data_race(data):
        db_helpers.insert_2fa(
            pgsql,
            transfer_id=body['transfer_id'],
            antifraud_resolution='AUTHORIZATION_REQUIRED',
        )

    response = await taxi_bank_transfers.post(
        request_string, headers=common.build_headers(), json=body,
    )
    assert response.status_code == 500


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
@pytest.mark.parametrize(
    'request_string', [CONFIRM_REQUEST, SIMPLIFIED_CONFIRM_REQUEST],
)
async def test_antifraud_deny(
        taxi_bank_transfers,
        request_string,
        bank_risk,
        pgsql,
        bank_authorization,
):
    body = prepare_request(request_string, pgsql)
    bank_risk.set_response(resolution='DENY')

    response = await taxi_bank_transfers.post(
        request_string,
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=body,
    )
    assert response.status_code == 200
    assert bank_authorization.create_track_handler.times_called == 0
    assert response.json() == {
        'fail_data': {
            'support_url': 'https://help-chat.bank.yandex.ru/fintech/yandex/fa/ru_ru/bank/chat',
        },
        'result_status': 'DENIED',
    }


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
@pytest.mark.parametrize(
    'request_string', [CONFIRM_REQUEST, SIMPLIFIED_CONFIRM_REQUEST],
)
async def test_antifraud_authorization_required(
        taxi_bank_transfers,
        request_string,
        bank_risk,
        pgsql,
        bank_authorization,
):
    body = prepare_request(request_string, pgsql)
    bank_risk.set_response(resolution='ALLOW', actions=['2fa'])

    response = await taxi_bank_transfers.post(
        request_string,
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=body,
    )
    assert bank_authorization.create_track_handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'authorization_info': {'authorization_track_id': 'default_track_id'},
        'result_status': 'AUTHORIZATION_REQUIRED',
    }


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.parametrize('request_string', [CONFIRM_REQUEST])
async def test_antifraud_allowed(
        taxi_bank_transfers,
        request_string,
        bank_risk,
        pgsql,
        bank_authorization,
):
    body = prepare_request(request_string, pgsql)
    bank_risk.set_response(resolution='ALLOW')

    response = await taxi_bank_transfers.post(
        request_string, headers=common.build_headers(), json=body,
    )
    assert bank_authorization.create_track_handler.times_called == 0
    assert response.status_code == 200
    authorization_info = db_helpers.select_authorization_info(
        pgsql, body['transfer_id'],
    )
    assert authorization_info.antifraud_resolution == 'ALLOWED'
    assert response.json() == {
        'result_status': 'ALLOWED',
        'success_data': {
            'description': (
                '100,05\xa0₽ на +7 912 345-67-89\n' 'Иван А в Тинькофф'
            ),
            'message': 'Перевод в обработке',
            'status': 'PROCESSING',
        },
    }


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('af_decision', ['ALLOWED', 'AUTHORIZATION_REQUIRED'])
@pytest.mark.parametrize(
    'request_string', [CONFIRM_REQUEST, SIMPLIFIED_CONFIRM_REQUEST],
)
async def test_request_after_2fa_ok(
        taxi_bank_transfers,
        request_string,
        pgsql,
        bank_authorization,
        af_decision,
):
    body = prepare_request(request_string, pgsql)
    transfer_id = ''
    if request_string == CONFIRM_REQUEST:
        transfer_id = body['transfer_id']
    elif request_string == SIMPLIFIED_CONFIRM_REQUEST:
        transfer_id = db_helpers.insert_transfer(
            pgsql,
            transfer_type='ME2ME',
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
            amount=str(common.DEFAULT_OFFER_AMOUNT),
        )
    db_helpers.insert_2fa(pgsql, transfer_id, antifraud_resolution=af_decision)

    headers = common.build_headers(
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        verification_token=common.GOOD_TOKEN,
    )
    if af_decision == 'ALLOWED':
        headers.pop('X-YaBank-Verification-Token')
    response = await taxi_bank_transfers.post(
        request_string, headers=headers, json=body,
    )
    assert bank_authorization.create_track_handler.times_called == 0
    assert response.status_code == 200
    authorization_info = db_helpers.select_authorization_info(
        pgsql, transfer_id,
    )
    assert authorization_info.antifraud_resolution == af_decision
    expected_response = {
        'result_status': 'ALLOWED',
        'success_data': {
            'description': (
                '100,05\xa0₽ на +7 912 345-67-89\n' 'Иван А в Тинькофф'
            ),
            'message': 'Перевод в обработке',
            'status': 'PROCESSING',
        },
    }
    if request_string == SIMPLIFIED_CONFIRM_REQUEST:
        expected_response['success_data']['transfer_id'] = transfer_id
    assert response.json() == expected_response


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('request_string', [CONFIRM_REQUEST])
# tr_id = transfer_id
async def test_tr_id_from_request_differs_tr_id_from_track(
        taxi_bank_transfers, request_string, pgsql, bank_authorization,
):
    body = prepare_request(request_string, pgsql)
    db_helpers.insert_2fa(pgsql, body['transfer_id'])
    body['transfer_id'] = db_helpers.insert_transfer(
        pgsql, amount=common.DEFAULT_OFFER_AMOUNT,
    )

    headers = common.build_headers(verification_token=common.GOOD_TOKEN)
    response = await taxi_bank_transfers.post(
        request_string, headers=headers, json=body,
    )
    assert bank_authorization.create_track_handler.times_called == 0
    assert response.status_code == 400


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('request_string', [CONFIRM_REQUEST])
async def test_old_vt_token(
        taxi_bank_transfers,
        request_string,
        pgsql,
        mocked_time,
        bank_authorization,
):
    mocked_time.set(
        datetime.datetime.strptime('2022-04-01 14:35:11', '%Y-%m-%d %H:%M:%S'),
    )
    body = prepare_request(request_string, pgsql)
    db_helpers.insert_2fa(pgsql, body['transfer_id'])

    headers = common.build_headers(verification_token=common.GOOD_OLD_TOKEN)
    response = await taxi_bank_transfers.post(
        request_string, headers=headers, json=body,
    )
    assert bank_authorization.create_track_handler.times_called == 0
    assert response.status_code == 400
    assert response.json() == {
        'code': 'BadRequest',
        'message': 'Bad jwt verification token',
    }


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('request_string', [CONFIRM_REQUEST])
async def test_bad_params(
        taxi_bank_transfers,
        request_string,
        pgsql,
        mocked_time,
        bank_authorization,
):
    mocked_time.set(
        datetime.datetime.strptime('2022-04-01 14:35:11', '%Y-%m-%d %H:%M:%S'),
    )
    body = prepare_request(request_string, pgsql)
    db_helpers.insert_2fa(
        pgsql, body['transfer_id'], transfer_params='bad_params',
    )

    headers = common.build_headers(verification_token=common.GOOD_OLD_TOKEN)
    response = await taxi_bank_transfers.post(
        request_string, headers=headers, json=body,
    )
    assert bank_authorization.create_track_handler.times_called == 0
    assert response.status_code == 409
    assert response.json() == {
        'code': 'Conflict',
        'message': (
            'Transfer params have been changed since last confirm request'
        ),
    }


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('request_string', [CONFIRM_REQUEST])
async def test_no_transfer(
        taxi_bank_transfers, request_string, pgsql, bank_authorization,
):
    body = prepare_request(request_string, pgsql)
    db_helpers.insert_2fa(pgsql, body['transfer_id'])
    body['transfer_id'] = str(uuid.uuid4())

    headers = common.build_headers(verification_token=common.GOOD_TOKEN)
    response = await taxi_bank_transfers.post(
        request_string, headers=headers, json=body,
    )
    assert bank_authorization.create_track_handler.times_called == 0
    assert response.status_code == 404
