import pytest

from tests_bank_userinfo import common
from tests_bank_userinfo import utils


async def test_no_session_no_bank_phone(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111118'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {
        'action': common.ACTION_BANK_REGISTRATION,
        'yandex_uid': uid,
        'product_to_open': 'WALLET',
    }
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid is None
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id is None
    assert pg_session.status == common.SESSION_STATUS_NOT_REGISTERED
    assert pg_session.old_session_uuid is None


@pytest.mark.experiments3(filename='userinfo_app_update_required.json')
async def test_no_session_existing_buid(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111111'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, phone_id=phone_id),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {'action': common.ACTION_NONE, 'yandex_uid': uid}
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid is None


async def test_no_session_candidate_buid_by_uid(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111111'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, phone_id=phone_id),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_PHONE_RECOVERY_REQUIRED
    assert pg_session.old_session_uuid is None


async def test_no_session_candidate_buid_by_phone(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111112'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, phone_id=phone_id),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_ACCOUNT_RECOVERY_REQUIRED
    assert pg_session.old_session_uuid is None


async def test_no_session_bank_phone_without_buid(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111112'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, phone_id=phone_id),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid is None
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_BANK_PHONE_WITHOUT_BUID
    assert pg_session.old_session_uuid is None


async def test_nonexistent_session_no_authorization(
        taxi_bank_userinfo, mockserver, pgsql,
):
    old_session_uuid = 'nonexistent'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(session_uuid=old_session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {'action': common.ACTION_AM_TOKEN_UPDATE}
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid is None
    assert pg_session.yandex_uid is None
    assert pg_session.phone_id is None
    assert pg_session.status == common.SESSION_STATUS_INVALID_TOKEN
    assert pg_session.old_session_uuid == old_session_uuid


async def test_nonexistent_session_no_bank_phone(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    old_session_uuid = 'nonexistent'
    uid = '111118'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, session_uuid=old_session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {
        'action': common.ACTION_BANK_REGISTRATION,
        'yandex_uid': uid,
        'product_to_open': 'WALLET',
    }
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid is None
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id is None
    assert pg_session.status == common.SESSION_STATUS_NOT_REGISTERED
    assert pg_session.old_session_uuid == old_session_uuid


@pytest.mark.experiments3(filename='userinfo_app_update_required.json')
async def test_nonexistent_session_existing_buid(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    old_session_uuid = 'nonexistent'
    uid = '111111'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, None, phone_id, old_session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {'action': common.ACTION_NONE, 'yandex_uid': uid}
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid == old_session_uuid


async def test_nonexistent_session_candidate_buid_by_uid(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    old_session_uuid = 'nonexistent'
    uid = '111111'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, None, phone_id, old_session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_PHONE_RECOVERY_REQUIRED
    assert pg_session.old_session_uuid == old_session_uuid


async def test_nonexistent_session_candidate_buid_by_phone(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    old_session_uuid = 'nonexistent'
    uid = '111112'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, None, phone_id, old_session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_ACCOUNT_RECOVERY_REQUIRED
    assert pg_session.old_session_uuid == old_session_uuid


@pytest.mark.experiments3(filename='userinfo_app_update_required.json')
async def test_nonexistent_session_bank_phone_without_buid(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    old_session_uuid = 'nonexistent'
    uid = '111112'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, None, phone_id, old_session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid is None
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_BANK_PHONE_WITHOUT_BUID
    assert pg_session.old_session_uuid == old_session_uuid


async def test_existing_session_match_no_authorization(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15bdf9'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(session_uuid=session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid is None
    assert pg_session.yandex_uid is None
    assert pg_session.phone_id is None
    assert pg_session.status == common.SESSION_STATUS_INVALID_TOKEN


@pytest.mark.experiments3(filename='userinfo_app_update_required.json')
@pytest.mark.parametrize(
    'session_uuid',
    [
        '024e7db5-9bd6-4f45-a1cd-2a442e15bdfa',
        '024e7db5-9bd6-4f45-a1cd-2a442e15bdfb',
    ],
)
async def test_existing_session_no_match_no_authorization(
        taxi_bank_userinfo, mockserver, pgsql, session_uuid, bank_applications,
):
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(session_uuid=session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {'action': common.ACTION_AM_TOKEN_UPDATE}
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid is None
    assert pg_session.yandex_uid is None
    assert pg_session.phone_id is None
    assert pg_session.status == common.SESSION_STATUS_INVALID_TOKEN
    assert pg_session.old_session_uuid == session_uuid


async def test_existing_session_match_no_phone(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    session_uuid = '6723253c-8df5-4bee-bc44-c3806d6860f6'
    uid = '111118'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, session_uuid=session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == {
        'yabank_session_uuid': session_uuid,
        'action': common.ACTION_BANK_REGISTRATION,
        'yandex_uid': uid,
        'product_to_open': 'WALLET',
    }
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid is None
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id is None
    assert pg_session.status == common.SESSION_STATUS_NOT_REGISTERED
    assert pg_session.old_session_uuid is None


@pytest.mark.parametrize(
    'session_uuid',
    [
        '024e7db5-9bd6-4f45-a1cd-2a442e15bdfd',
        '024e7db5-9bd6-4f45-a1cd-2a442e15bdfe',
        '024e7db5-9bd6-4f45-a1cd-2a442e15bdff',
    ],
)
async def test_existing_session_no_match_no_phone(
        taxi_bank_userinfo, mockserver, pgsql, session_uuid, bank_applications,
):
    uid = '111118'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, session_uuid=session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {
        'action': common.ACTION_BANK_REGISTRATION,
        'yandex_uid': uid,
        'product_to_open': 'WALLET',
    }
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid is None
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id is None
    assert pg_session.status == common.SESSION_STATUS_NOT_REGISTERED
    assert pg_session.old_session_uuid == session_uuid


@pytest.mark.experiments3(filename='userinfo_app_update_required.json')
async def test_existing_session_match_existing_buid(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be00'
    uid = '111111'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, None, phone_id, session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp == {
        'yabank_session_uuid': session_uuid,
        'action': common.ACTION_NONE,
        'yandex_uid': uid,
    }
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid is None


@pytest.mark.parametrize(
    'session_uuid',
    [
        '024e7db5-9bd6-4f45-a1cd-2a442e15be01',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be02',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be03',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be04',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be05',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be06',
    ],
)
async def test_existing_session_no_match_existing_buid(
        taxi_bank_userinfo, mockserver, pgsql, session_uuid, bank_applications,
):
    uid = '111111'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, None, phone_id, session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {'action': common.ACTION_NONE, 'yandex_uid': uid}
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid == session_uuid


async def test_existing_session_match_candidate_uid(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    old_session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be07'
    uid = '111111'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, None, phone_id, old_session_uuid),
    )
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp_session_uuid != old_session_uuid
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_PHONE_RECOVERY_REQUIRED
    assert pg_session.old_session_uuid == old_session_uuid


@pytest.mark.parametrize(
    'session_uuid',
    [
        '024e7db5-9bd6-4f45-a1cd-2a442e15be08',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be09',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be0a',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be0b',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be0c',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be0d',
    ],
)
async def test_existing_session_no_match_candidate_uid(
        taxi_bank_userinfo, mockserver, pgsql, session_uuid, bank_applications,
):
    uid = '111111'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, None, phone_id, session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp_session_uuid != session_uuid
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_PHONE_RECOVERY_REQUIRED
    assert pg_session.old_session_uuid == session_uuid


async def test_existing_session_match_candidate_phone(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    old_session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be0e'
    uid = '111112'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, None, phone_id, old_session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp_session_uuid != old_session_uuid
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_ACCOUNT_RECOVERY_REQUIRED
    assert pg_session.old_session_uuid == old_session_uuid


@pytest.mark.parametrize(
    'session_uuid',
    [
        '024e7db5-9bd6-4f45-a1cd-2a442e15be0f',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be10',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be11',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be12',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be13',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be14',
    ],
)
async def test_existing_session_no_match_candidate_phone(
        taxi_bank_userinfo, mockserver, pgsql, session_uuid, bank_applications,
):
    uid = '111112'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, None, phone_id, session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp_session_uuid != session_uuid
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_ACCOUNT_RECOVERY_REQUIRED
    assert pg_session.old_session_uuid == session_uuid


@pytest.mark.parametrize(
    'session_uuid',
    [
        '024e7db5-9bd6-4f45-a1cd-2a442e15be15',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be16',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be17',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be18',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be19',
        '024e7db5-9bd6-4f45-a1cd-2a442e15be1a',
    ],
)
async def test_existing_session_bank_phone_without_buid(
        taxi_bank_userinfo, mockserver, pgsql, session_uuid, bank_applications,
):
    uid = '111112'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, None, phone_id, session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid is None
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_BANK_PHONE_WITHOUT_BUID
    assert pg_session.old_session_uuid == session_uuid


@pytest.mark.parametrize(
    'uid,buid',
    [
        ('111114', '0543be85-4adc-4b79-88c5-42ea9e7516c1'),
        ('111116', '0d1f48c9-b5fb-4732-bbb7-09b7dc9e6dfb'),
    ],
)
async def test_phone_confirmed_no_phone_in_request(
        taxi_bank_userinfo, mockserver, pgsql, uid, buid, bank_applications,
):
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == buid
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id is None
    assert pg_session.status == common.SESSION_STATUS_PHONE_RECOVERY_REQUIRED
    assert pg_session.old_session_uuid is None


@pytest.mark.parametrize(
    'uid,phone_id,applications,status,action',
    [
        (
            '111114',
            'phone_id_4',
            [
                {
                    'type': 'REGISTRATION',
                    'application_id': '97754336-d4d1-43c1-aadb-cabd06674ea6',
                    'is_blocking': True,
                },
                {
                    'type': 'DIGITAL_CARD_ISSUE',
                    'application_id': '97754336-d4d1-43c1-aadb-cabd06674ea7',
                    'is_blocking': True,
                },
            ],
            common.SESSION_STATUS_REQUIRED_APPLICATION_IN_PROGRESS,
            common.ACTION_APPLICATION_STATUS_CHECK,
        ),
        (
            '111120',
            None,
            [
                {
                    'type': 'REGISTRATION',
                    'application_id': '97754336-d4d1-43c1-aadb-cabd06674ea6',
                    'is_blocking': True,
                },
            ],
            common.SESSION_STATUS_REQUIRED_APPLICATION_IN_PROGRESS,
            common.ACTION_APPLICATION_STATUS_CHECK,
        ),
        (
            '111120',
            None,
            [
                {
                    'type': 'SIMPLIFIED_IDENTIFICATION',
                    'application_id': '97754336-d4d1-43c1-aadb-cabd06674000',
                    'is_blocking': True,
                },
            ],
            common.SESSION_STATUS_REQUIRED_APPLICATION_IN_PROGRESS,
            common.ACTION_APPLICATION_STATUS_CHECK,
        ),
        (
            '111120',
            None,
            [
                {
                    'type': 'SIMPLIFIED_IDENTIFICATION_ESIA',
                    'application_id': '97754336-d4d1-43c1-aadb-cabd06674001',
                    'is_blocking': True,
                },
            ],
            common.SESSION_STATUS_REQUIRED_APPLICATION_IN_PROGRESS,
            common.ACTION_APPLICATION_STATUS_CHECK,
        ),
        (
            '111120',
            None,
            [
                {
                    'type': 'CHANGE_NUMBER',
                    'application_id': '97754336-d4d1-43c1-aadb-cabd06674002',
                    'is_blocking': True,
                },
            ],
            common.SESSION_STATUS_REQUIRED_APPLICATION_IN_PROGRESS,
            common.ACTION_APPLICATION_STATUS_CHECK,
        ),
        (
            '111120',
            None,
            [
                {
                    'type': 'KYC',
                    'application_id': '97754336-d4d1-43c1-aadb-cabd06674003',
                    'is_blocking': True,
                },
            ],
            common.SESSION_STATUS_REQUIRED_APPLICATION_IN_PROGRESS,
            common.ACTION_APPLICATION_STATUS_CHECK,
        ),
    ],
)
async def test_applications(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        uid,
        phone_id,
        applications,
        status,
        action,
        bank_applications,
):
    bank_applications.set_applications(applications)
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, phone_id=phone_id),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    for application in applications:
        application['required'] = application.pop('is_blocking')

    assert resp == {
        'action': action,
        'applications': applications,
        'yandex_uid': uid,
    }
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    if uid == '111114':
        assert pg_session.bank_uid == '0543be85-4adc-4b79-88c5-42ea9e7516c1'
        assert pg_session.phone_id == phone_id
    else:
        assert pg_session.bank_uid is None
        assert pg_session.phone_id is None
    assert pg_session.yandex_uid == uid
    assert pg_session.status == status
    assert pg_session.old_session_uuid is None


async def test_phone_confirmed_without_applications(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111114'
    phone_id = 'phone_id_4'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, phone_id=phone_id),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == '0543be85-4adc-4b79-88c5-42ea9e7516c1'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_BANNED
    assert pg_session.old_session_uuid is None


@pytest.mark.parametrize('applications_fail', [True, False])
async def test_new_buid_without_applications(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        applications_fail,
        bank_applications,
):
    if applications_fail:
        bank_applications.set_http_status_code(500)
    else:
        bank_applications.set_http_status_code(200)
        bank_applications.set_applications([])
    uid = '111115'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {
        'action': common.ACTION_BANK_REGISTRATION,
        'yandex_uid': uid,
        'product_to_open': 'WALLET',
    }
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == '96b35805-ff7b-4bdf-a68d-813756a3ba5c'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id is None
    assert pg_session.status == common.SESSION_STATUS_NOT_REGISTERED
    assert pg_session.old_session_uuid is None


async def test_old_session_not_auth_but_create_for_other_user(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        bank_applications,
        bank_risk,
        bank_authorization,
):
    uid = '111111'
    buid = '7948e3a9-623c-4524-a390-9e4264d27a77'
    phone_id = 'phone_id_1'
    old_session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be1c'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id, old_session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert resp_session_uuid != old_session_uuid
    assert resp == {'action': common.ACTION_NONE, 'yandex_uid': uid}
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == buid
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid == old_session_uuid
    assert pg_session.authorization_track_id is None
    assert bank_authorization.create_track_handler.times_called == 0
    assert bank_risk.risk_calculation_handler.times_called == 1


async def test_start_session_user_blocked(
        taxi_bank_userinfo, mockserver, pgsql,
):
    uid = '111111'
    buid = '7948e3a9-623c-4524-a390-9e4264d27a77'
    phone_id = 'phone_id_1'
    old_session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be1c'

    utils.update_buid_status(pgsql, buid, 'BLOCKED')
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id, old_session_uuid),
    )

    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert resp_session_uuid != old_session_uuid
    assert resp == {
        'action': common.ACTION_SUPPORT,
        'yandex_uid': uid,
        'support_url': common.SUPPORT_URL,
    }
