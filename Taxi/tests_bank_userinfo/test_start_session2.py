import jwt
import pytest

from tests_bank_userinfo import common
from tests_bank_userinfo import utils


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_no_session_no_authorization(
        taxi_bank_userinfo, mockserver, pgsql,
):
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(),
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
    assert pg_session.old_session_uuid is None


@pytest.mark.now('2021-06-13T14:00:00Z')
@pytest.mark.parametrize(
    'uid,phone_id,buid',
    [
        ('111111', 'phone_id_1', '7948e3a9-623c-4524-a390-9e4264d27a77'),
        (
            '111111',
            'phone_id_1',
            '0000e3a9-623c-4524-a390-9e4264d27a77',
        ),  # nonexisten
    ],
)
async def test_buid_in_params(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        uid,
        phone_id,
        buid,
        bank_applications,
):
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id),
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
    assert pg_session.old_session_uuid is None


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_valid_buid_invalid_uid_and_phone_id(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111117'
    phone_id = 'phone_id_7'
    buid = '7948e3a9-623c-4524-a390-9e4264d27a77'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id),
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
    assert pg_session.old_session_uuid is None


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_valid_uid_and_phone_id_invalid_buid(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111111'
    phone_id = 'phone_id_1'
    buid = '0000e3a9-623c-4524-a390-9e4264d27a77'  # nonexisten
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id),
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
    assert pg_session.old_session_uuid is None


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_buid_wrong_format(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111111'
    phone_id = 'phone_id_1'
    buid = 'wrong-format'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id),
    )
    assert response.status_code == 400


@pytest.mark.experiments3(filename='userinfo_app_update_required.json')
async def test_app_update_required(
        taxi_bank_userinfo, mockserver, pgsql, experiments3,
):
    headers = common.get_headers()
    headers['X-Request-Application'] = 'app_brand=UPDATE'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=headers,
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {'action': common.ACTION_APP_UPDATE}
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid is None
    assert pg_session.yandex_uid is None
    assert pg_session.phone_id is None
    assert pg_session.status == common.SESSION_STATUS_APP_UPDATE_REQUIRED
    assert pg_session.old_session_uuid is None


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_global_bank_experiment_not_found(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111110'
    phone_id = 'phone_id_2'
    buid = '0000e3a9-623c-4524-a390-9e4264d27a77'  # nonexisten
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {'action': common.ACTION_NONE, 'yandex_uid': uid}
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == '48c3d180-e14e-4e64-8de3-407b0b3b735a'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid is None


@pytest.mark.experiments3(filename='bank_access.json')
async def test_global_bank_experiment_user_not_found(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111120'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid),
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_access.json')
async def test_global_bank_experiment_user_found(
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
    assert pg_session.old_session_uuid is None


@pytest.mark.experiments3(filename='bank_access.json')
async def test_global_bank_experiment_user_not_found_have_buid(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111110'
    buid = '48c3d180-e14e-4e64-8de3-407b0b3b735a'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {'action': common.ACTION_NONE, 'yandex_uid': uid}
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == buid
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid is None


async def test_no_antifraud_info(taxi_bank_userinfo, mockserver):
    uid = '111111'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={},
        headers=common.get_headers(uid, phone_id=phone_id),
    )
    assert response.status_code == 400


async def test_no_antifraud_info_no_remote_ip(taxi_bank_userinfo, mockserver):
    uid = '111111'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={},
        headers={
            'X-Yandex-UID': uid,
            'X-YaBank-PhoneID': phone_id,
            'X-YaTaxi-Pass-Flags': '',
        },
    )
    assert response.status_code == 400
    assert 'Missing X-Remote-IP in header' in response.json()['message']


@pytest.mark.experiments3(filename='bank_access.json')
async def test_existing_session_antifraud_info_without_device_id(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = '111110'
    buid = '48c3d180-e14e-4e64-8de3-407b0b3b735a'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={'antifraud_info': {}},
        headers=common.get_headers(uid, buid, phone_id),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {'action': common.ACTION_NONE, 'yandex_uid': uid}
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == buid
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid is None


@pytest.mark.parametrize('applications_fail', [True, False])
async def test_no_buid_without_applications(
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
    uid = '111120'
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
    assert pg_session.bank_uid is None
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id is None
    assert pg_session.status == common.SESSION_STATUS_NOT_REGISTERED
    assert pg_session.old_session_uuid is None


async def test_existing_session_antifraud_info_with_additional_prop(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be00'
    uid = '111111'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={
            'antifraud_info': {
                'device_id': '12345',
                'additionalProp1': {'test_add_prop': '54321'},
            },
            'locale': 'ru',
        },
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


async def test_existing_session_antifraud_info_with_bad_additional_prop(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be00'
    uid = '111111'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={
            'antifraud_info': {
                'device_id': '12345',
                'additionalProp1': {'test_add_prop': '5432'},
            },
        },
        headers=common.get_headers(uid, None, phone_id, session_uuid),
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['yabank_session_uuid'] != session_uuid
    assert resp['action'] == common.ACTION_NONE
    assert resp['yandex_uid'] == uid

    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid is None


async def test_update_db_bank_userinfo_session(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    old_session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be00'
    uid = '111111'
    phone_id = 'phone_id_1'
    json_with_new_add_prop = {
        'antifraud_info': {
            'device_id': '12345',
            'additionalProp1': {'test_add_prop': '5432'},
        },
    }
    headers = common.get_headers(uid, None, phone_id, old_session_uuid)
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=json_with_new_add_prop,
        headers=headers,
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['yabank_session_uuid'] != old_session_uuid
    assert resp['action'] == common.ACTION_NONE
    assert resp['yandex_uid'] == uid

    session_uuid = resp['yabank_session_uuid']
    headers['X-YaBank-SessionUUID'] = session_uuid
    headers['X-Yandex-UID'] = resp['yandex_uid']

    # second response
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=json_with_new_add_prop,
        headers=headers,
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
    assert pg_session.old_session_uuid == old_session_uuid


async def test_existing_session_antifraud_info_unmatch_client_ip(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be00'
    uid = '111111'
    phone_id = 'phone_id_1'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={
            'antifraud_info': {
                'device_id': '12345',
                'additionalProp1': {'test_add_prop': '54321'},
            },
        },
        headers=common.get_headers(
            uid, None, phone_id, session_uuid, remote_ip='127.0.0.1',
        ),
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['yabank_session_uuid'] != session_uuid
    assert resp['action'] == common.ACTION_NONE
    assert resp['yandex_uid'] == uid

    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == '7948e3a9-623c-4524-a390-9e4264d27a77'
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid is None


@pytest.mark.experiments3(filename='bank_access.json')
async def test_bank_access_staff_login_ok(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = 'new_id'
    staff_login = 'staff_login'
    headers = common.get_headers(uid)
    headers['X-YaBank-Yandex-Team-Login'] = staff_login
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.experiments3(filename='bank_access.json')
async def test_bank_access_staff_login_not_in_exp(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications,
):
    uid = 'new_id'
    staff_login = 'unknown_staff_login'
    headers = common.get_headers(uid)
    headers['X-YaBank-Yandex-Team-Login'] = staff_login
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=headers,
    )
    assert response.status_code == 404


async def test_bank_risk_2fa_create_track(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        bank_applications,
        bank_risk,
        bank_authorization,
):
    bank_risk.set_response('ALLOW', ['2fa'])
    uid = '111110'
    buid = '48c3d180-e14e-4e64-8de3-407b0b3b735a'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {
        'action': common.ACTION_AUTHORIZATION,
        'yandex_uid': uid,
        'authorization_track_id': 'default_track_id',
    }
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == buid
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_NOT_AUTHORIZED
    assert pg_session.old_session_uuid is None
    assert pg_session.authorization_track_id == 'default_track_id'
    assert bank_authorization.create_track_handler.times_called == 1
    assert bank_risk.risk_calculation_handler.times_called == 1


GOOD_TOKEN = jwt.encode(
    {
        'track_id': 'default_track_id',
        'verification_result': 'OK',
        'valid_to': '2131-06-13T14:00:00Z',
    },
    common.JWT_PRIVATE_KEY,
    algorithm='PS512',
)


@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('bank_risk_allow_action', [None, '2fa'])
async def test_bank_risk_2fa_verify_token_ok(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        bank_applications,
        bank_authorization,
        bank_risk,
        bank_risk_allow_action,
):
    actions = []
    if bank_risk_allow_action:
        actions.append(bank_risk_allow_action)
    bank_risk.set_response('ALLOW', actions)
    uid = '111112'
    buid = 'ff89568b-c667-4bb0-9f92-dbaac0672728'
    phone_id = 'phone_id_3'
    old_session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be01'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(
            uid, buid, phone_id, old_session_uuid, GOOD_TOKEN,
        ),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {'action': common.ACTION_NONE, 'yandex_uid': uid}
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == buid
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid == old_session_uuid
    assert pg_session.authorization_track_id is None
    assert not bank_authorization.create_track_handler.has_calls
    assert bank_risk.risk_calculation_handler.times_called == 1


@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
async def test_bank_risk_deny_status_after_good_verify(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications, bank_risk,
):
    bank_risk.set_response('DENY', [])
    uid = '111112'
    buid = 'ff89568b-c667-4bb0-9f92-dbaac0672728'
    phone_id = 'phone_id_3'
    old_session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be01'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(
            uid, buid, phone_id, old_session_uuid, GOOD_TOKEN,
        ),
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
    assert pg_session.bank_uid == buid
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_BANK_RISK_DENY
    assert pg_session.old_session_uuid == old_session_uuid
    assert pg_session.authorization_track_id is None
    assert bank_risk.risk_calculation_handler.times_called == 1


BAD_PAYLOAD_TOKEN = jwt.encode(
    {
        'track_id': '3b197846-d0fc-4b31-9285-485b50048366',
        'verification_result': 'OK',
        'valid_to': '2131-06-13T14:00:00Z',
    },
    common.JWT_PRIVATE_KEY,
    algorithm='PS512',
)

BAD_ALGO_TOKEN = jwt.encode(
    {
        'track_id': 'default_track_id',
        'verification_result': 'OK',
        'valid_to': '2131-06-13T14:00:00Z',
    },
    common.JWT_PRIVATE_KEY,
    algorithm='HS512',
)

EXPIRED_TOKEN = jwt.encode(
    {
        'track_id': 'default_track_id',
        'verification_result': 'OK',
        'valid_to': '1970-06-13T14:00:00Z',
    },
    common.JWT_PRIVATE_KEY,
    algorithm='PS512',
)

BAD_JSON_TOKEN = jwt.encode(
    {'unexpected_field': 'some_value'},
    common.JWT_PRIVATE_KEY,
    algorithm='PS512',
)


@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize(
    'token',
    [BAD_PAYLOAD_TOKEN, BAD_ALGO_TOKEN, EXPIRED_TOKEN, BAD_JSON_TOKEN, None],
)
async def test_bank_risk_2fa_verify_token_fail(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        bank_applications,
        bank_authorization,
        bank_risk,
        token,
):
    uid = '111112'
    buid = 'ff89568b-c667-4bb0-9f92-dbaac0672728'
    phone_id = 'phone_id_3'
    session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be01'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id, session_uuid, token),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert session_uuid == resp_session_uuid

    assert len(resp_session_uuid) > 1
    assert resp == {
        'action': common.ACTION_AUTHORIZATION,
        'yandex_uid': uid,
        'authorization_track_id': 'default_track_id',
    }
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == buid
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_NOT_AUTHORIZED
    assert pg_session.old_session_uuid is None
    assert pg_session.authorization_track_id == 'default_track_id'
    assert not bank_authorization.create_track_handler.has_calls
    assert not bank_risk.risk_calculation_handler.has_calls


@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize(
    'bank_risk_response, bank_risk_action, user_action, session_status',
    [
        ('ALLOW', None, common.ACTION_NONE, common.SESSION_STATUS_OK),
        (
            'ALLOW',
            '2fa',
            common.ACTION_AUTHORIZATION,
            common.SESSION_STATUS_NOT_AUTHORIZED,
        ),
        (
            'DENY',
            None,
            common.ACTION_SUPPORT,
            common.SESSION_STATUS_BANK_RISK_DENY,
        ),
    ],
)
async def test_without_track_id_in_db(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        bank_applications,
        bank_authorization,
        bank_risk,
        bank_risk_response,
        bank_risk_action,
        user_action,
        session_status,
):
    actions = []
    if bank_risk_action:
        actions.append(bank_risk_action)
    bank_risk.set_response(bank_risk_response, actions)
    uid = '111113'
    buid = 'e0cfac83-f7a2-452e-9b8e-bfc7a3aef579'
    phone_id = 'phone_id_4'
    old_session_uuid = '024e7db5-9bd6-4f45-a1cd-2a442e15be02'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(
            uid, buid, phone_id, old_session_uuid, GOOD_TOKEN,
        ),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert old_session_uuid != resp_session_uuid

    assert len(resp_session_uuid) > 1
    assert resp['action'] == user_action
    assert resp['yandex_uid'] == uid
    if bank_risk_action == '2fa':
        assert resp['authorization_track_id'] == 'default_track_id'
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == buid
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == session_status
    assert pg_session.old_session_uuid is not None
    if bank_risk_action == '2fa':
        assert pg_session.authorization_track_id == 'default_track_id'
        assert bank_authorization.create_track_handler.times_called == 1
    else:
        assert not bank_authorization.create_track_handler.has_calls
    assert bank_risk.risk_calculation_handler.times_called == 1


@pytest.mark.parametrize('error_code, expected_tries', [(400, 1), (500, 1)])
async def test_bank_authorization_error_create_track(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        bank_applications,
        bank_authorization,
        bank_risk,
        error_code,
        expected_tries,
):
    bank_risk.set_response('ALLOW', ['2fa'])
    bank_authorization.set_http_status_code(error_code)
    uid = '111110'
    buid = '48c3d180-e14e-4e64-8de3-407b0b3b735a'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id),
    )
    assert response.status_code == 500
    assert (
        bank_authorization.create_track_handler.times_called == expected_tries
    )


async def test_bank_risk_deny_status(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications, bank_risk,
):
    bank_risk.set_response('DENY', [])
    uid = '111110'
    buid = '48c3d180-e14e-4e64-8de3-407b0b3b735a'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id),
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
    assert pg_session.bank_uid == buid
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_BANK_RISK_DENY
    assert pg_session.old_session_uuid is None
    assert bank_risk.risk_calculation_handler.times_called == 1


@pytest.mark.parametrize('error_code, expected_tries', [(400, 1), (500, 1)])
async def test_bank_risk_error(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        bank_applications,
        bank_risk,
        error_code,
        expected_tries,
):
    bank_risk.set_http_status_code(error_code)
    uid = '111110'
    buid = '48c3d180-e14e-4e64-8de3-407b0b3b735a'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {'action': common.ACTION_NONE, 'yandex_uid': uid}
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == buid
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid is None
    assert bank_risk.risk_calculation_handler.times_called == expected_tries


async def test_bank_risk_empty_device_id(
        taxi_bank_userinfo, mockserver, pgsql, bank_applications, bank_risk,
):
    uid = '111110'
    buid = '48c3d180-e14e-4e64-8de3-407b0b3b735a'
    phone_id = 'phone_id_2'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={'antifraud_info': {}},
        headers=common.get_headers(uid, buid, phone_id),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {'action': common.ACTION_NONE, 'yandex_uid': uid}
    pg_session = utils.select_session(pgsql, resp_session_uuid)

    assert pg_session.session_uuid == resp_session_uuid
    assert pg_session.bank_uid == buid
    assert pg_session.yandex_uid == uid
    assert pg_session.phone_id == phone_id
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid is None


@pytest.mark.parametrize('user_agent', ['UA', '', None])
@pytest.mark.parametrize('channel_type', ['WEB', 'MOBILE', 'SDK', None])
async def test_bank_risk_params(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        bank_applications,
        bank_authorization,
        bank_risk,
        user_agent,
        channel_type,
):
    @mockserver.json_handler('/bank-risk/risk/calculation/start_session')
    def _risk_calculation_handler(request):
        assert request.method == 'POST'
        assert request.json['user_agent'] == (user_agent or '')
        assert request.json['channel_type'] == (
            'WEB' if channel_type == 'WEB' else 'SDK'
        )
        return mockserver.make_response(
            json={
                'resolution': 'ALLOW',
                'action': [],
                'af_decision_id': 'af_decision_id',
            },
        )

    uid = '111110'
    buid = '48c3d180-e14e-4e64-8de3-407b0b3b735a'
    phone_id = 'phone_id_2'
    headers = common.get_headers(uid, buid, phone_id)
    headers['User-Agent'] = user_agent
    headers['X-YaBank-ChannelType'] = channel_type
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=headers,
    )
    assert response.status_code == 200
