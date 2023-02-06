import pytest

from tests_bank_transfers import common

BUID_FPS_ON = common.TEST_BANK_UID
BUID_FPS_OFF = '7948e3a9-623c-4524-a390-9e4264d27a01'


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
    headers = common.build_headers()
    headers.pop(header)
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/settings/get', headers=headers,
    )

    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


async def test_not_in_exp(taxi_bank_transfers, bank_audit):
    headers = common.build_headers()
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/settings/get', headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {'settings': []}


@pytest.mark.experiments3(
    filename='bank_transfer_settings_feature_experiments.json',
)
async def test_buid_absent_in_core_and_userinfo_bds(
        taxi_bank_transfers, bank_audit, bank_core_faster_payments_mock,
):
    headers = common.build_headers(
        buid=common.TEST_ABSENT_IN_FPS_CORE_AND_USERINFO_BASES_BUID,
    )
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/settings/get', headers=headers,
    )
    assert response.status_code == 500


@pytest.mark.experiments3(
    filename='bank_transfer_settings_feature_experiments.json',
)
@pytest.mark.parametrize('locale', ['ru, en'])
@pytest.mark.parametrize(
    'buid, boolean_value_fps, boolean_value_pb',
    [
        (BUID_FPS_OFF, False, False),
        (BUID_FPS_ON, True, False),
        (common.TEST_YANDEX_BANK_FPS_ON_BUID, True, True),
    ],
)
async def test_ok(
        taxi_bank_transfers,
        bank_audit,
        bank_core_faster_payments_mock,
        buid,
        locale,
        boolean_value_fps,
        boolean_value_pb,
):
    headers = common.build_headers(buid=buid, language=locale)
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/settings/get', headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == common.get_settings(
        boolean_value_fps=boolean_value_fps,
        boolean_value_pb=boolean_value_pb,
        locale=locale,
    )
