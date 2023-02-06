import pytest
import datetime

import tests_bank_userinfo.utils as utils
from tests_bank_userinfo import common


SESSION_UUID = '024e7db5-9bd6-4f45-a1cd-2a442e15be00'
UID = '111111'
PHONE_ID = 'phone_id_1'
BANK_UID = '7948e3a9-623c-4524-a390-9e4264d27a77'
HEADERS = common.get_headers(UID, BANK_UID, PHONE_ID, SESSION_UUID)

EXPECTED_RESPONSE = {
    'yabank_session_uuid': SESSION_UUID,
    'action': common.ACTION_NONE,
    'yandex_uid': UID,
}


def assert_pg_session_validity(pg_session):
    assert pg_session.session_uuid == SESSION_UUID
    assert pg_session.bank_uid == BANK_UID
    assert pg_session.yandex_uid == UID
    assert pg_session.phone_id == PHONE_ID
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid is None


@pytest.mark.now('2022-06-04T16:10:00+03:00')
async def test_update_default(taxi_bank_userinfo, pgsql, bank_applications):
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=HEADERS,
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == EXPECTED_RESPONSE

    pg_session = utils.select_session(pgsql, SESSION_UUID)
    assert_pg_session_validity(pg_session)
    assert pg_session.updated_at != datetime.datetime.fromisoformat(
        '2022-06-04T16:00:00+03:00',
    )


@pytest.mark.now('2022-06-04T16:10:00+03:00')
@pytest.mark.config(
    BANK_USERINFO_SESSIONS_LIFETIME={'age_for_update_minutes': 5},
)
async def test_update_with_config(
        taxi_bank_userinfo, pgsql, bank_applications,
):
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=HEADERS,
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == EXPECTED_RESPONSE

    pg_session = utils.select_session(pgsql, SESSION_UUID)
    assert_pg_session_validity(pg_session)
    assert pg_session.updated_at != datetime.datetime.fromisoformat(
        '2022-06-04T16:00:00+03:00',
    )


@pytest.mark.now('2022-06-04T16:10:00+03:00')
@pytest.mark.config(
    BANK_USERINFO_SESSIONS_LIFETIME={'age_for_update_minutes': 15},
)
async def test_no_update_with_config(
        taxi_bank_userinfo, pgsql, bank_applications,
):
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=HEADERS,
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == EXPECTED_RESPONSE

    pg_session = utils.select_session(pgsql, SESSION_UUID)
    assert_pg_session_validity(pg_session)
    assert pg_session.updated_at == datetime.datetime.fromisoformat(
        '2022-06-04T16:00:00+03:00',
    )
