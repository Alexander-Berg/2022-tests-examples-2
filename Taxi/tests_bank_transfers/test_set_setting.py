import pytest

from tests_bank_transfers import common

BUID_FPS_ON = common.TEST_BANK_UID
BUID_FPS_OFF = '7948e3a9-623c-4524-a390-9e4264d27a01'

FASTER_PAYMENTS_SYSTEM_KEY = 'faster_payments_system'
PRIORITY_BANK_KEY = 'fps_priority_bank'


def get_body(key=FASTER_PAYMENTS_SYSTEM_KEY, boolean_value=True):
    return {
        'key': key,
        'property': {'type': 'SWITCH', 'boolean_value': boolean_value},
    }


@pytest.mark.parametrize(
    'header',
    [
        'X-Yandex-BUID',
        'X-Yandex-UID',
        'X-YaBank-SessionUUID',
        'X-YaBank-PhoneID',
    ],
)
async def test_unauthorized(taxi_bank_transfers, bank_audit, header):
    headers = common.build_headers(
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    headers.pop(header)
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/settings/set', headers=headers, json=get_body(),
    )

    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


async def test_not_in_exp(taxi_bank_transfers, bank_audit):
    headers = common.build_headers(
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/settings/set', headers=headers, json=get_body(),
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'User not in experiment',
    }


@pytest.mark.experiments3(
    filename='bank_transfer_settings_feature_experiments.json',
)
@pytest.mark.parametrize('key', ['', 'abc', '1'])
async def test_invalid_key(
        taxi_bank_transfers, bank_audit, key, bank_core_faster_payments_mock,
):
    headers = common.build_headers(
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/settings/set',
        headers=headers,
        json=get_body(key=key),
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'Setting key not found',
    }


@pytest.mark.experiments3(
    filename='bank_transfer_settings_feature_experiments.json',
)
async def test_buid_absent_in_core_and_userinfo_bds(
        taxi_bank_transfers, bank_audit, bank_core_faster_payments_mock,
):
    headers = common.build_headers(
        common.TEST_ABSENT_IN_FPS_CORE_AND_USERINFO_BASES_BUID,
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/settings/set', headers=headers, json=get_body(),
    )
    assert response.status_code == 500


@pytest.mark.experiments3(
    filename='bank_transfer_settings_feature_experiments.json',
)
@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.parametrize(
    'buid, boolean_value_pb',
    [
        (BUID_FPS_OFF, False),
        (BUID_FPS_ON, False),
        (common.TEST_YANDEX_BANK_FPS_ON_BUID, True),
    ],
)
@pytest.mark.parametrize('boolean_value', [False, True])
async def test_set_faster_payments_system(
        taxi_bank_transfers,
        bank_audit,
        bank_core_faster_payments_mock,
        buid,
        locale,
        boolean_value,
        boolean_value_pb,
):
    headers = common.build_headers(
        buid=buid,
        language=locale,
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/settings/set',
        headers=headers,
        json=get_body(boolean_value=boolean_value),
    )

    assert response.status_code == 200
    assert response.json()['success_data'] == common.get_settings(
        boolean_value_fps=boolean_value,
        boolean_value_pb=(boolean_value_pb and boolean_value),
        locale=locale,
    )
    assert response.json()['result_status'] == 'ALLOWED'


@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.experiments3(
    filename='bank_transfer_settings_feature_experiments.json',
)
@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.parametrize(
    'buid', [BUID_FPS_ON, (common.TEST_YANDEX_BANK_FPS_ON_BUID)],
)
async def test_set_priority_bank_ok(
        taxi_bank_transfers, bank_audit, bank_authorization, buid, locale,
):
    headers = common.build_headers(
        buid=buid,
        language=locale,
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        verification_token=common.GOOD_TOKEN,
    )

    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/settings/set',
        headers=headers,
        json=get_body(boolean_value=True, key=PRIORITY_BANK_KEY),
    )

    assert response.status_code == 200
    assert response.json()['success_data'] == common.get_settings(
        boolean_value_fps=True, boolean_value_pb=True, locale=locale,
    )
    assert response.json()['result_status'] == 'ALLOWED'
    assert 'authorization_info' not in response.json()
    assert 'fail_data' not in response.json()
    assert (
        bank_authorization.create_track_handler.times_called == 0
        if buid == BUID_FPS_ON
        else 1
    )


@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.experiments3(
    filename='bank_transfer_settings_feature_experiments.json',
)
async def test_set_priority_bank_needed_authorization(
        taxi_bank_transfers, bank_audit, bank_authorization,
):
    headers = common.build_headers(
        buid=BUID_FPS_ON, idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/settings/set',
        headers=headers,
        json=get_body(boolean_value=True, key=PRIORITY_BANK_KEY),
    )

    assert response.status_code == 200
    assert 'success_data' not in response.json()
    assert response.json()['result_status'] == 'AUTHORIZATION_REQUIRED'
    assert response.json()['authorization_info'] == {
        'authorization_track_id': 'default_track_id',
    }
    assert bank_authorization.create_track_handler.times_called == 1
