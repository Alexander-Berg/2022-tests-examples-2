import pytest

from tests_bank_userinfo import common


@pytest.mark.parametrize(
    'pass_flags, action',
    [
        ('phonish', common.ACTION_PASSPORT_REGISTRATION),
        ('neophonish', common.ACTION_BANK_REGISTRATION),
        ('abc,phonish', common.ACTION_PASSPORT_REGISTRATION),
        ('phonish,abc', common.ACTION_PASSPORT_REGISTRATION),
        ('portal', common.ACTION_BANK_REGISTRATION),
        ('', common.ACTION_BANK_REGISTRATION),
    ],
)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_phonish_person(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        bank_applications,
        pass_flags,
        action,
):
    uid = 'phonish_or_not'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, pass_flags=pass_flags),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    expected_resp = {'action': action, 'yandex_uid': uid}
    if action == common.ACTION_BANK_REGISTRATION:
        expected_resp['product_to_open'] = 'WALLET'
    assert resp == expected_resp


@pytest.mark.parametrize(
    'pass_flags, action',
    [
        ('phonish', common.ACTION_NONE),
        ('portal', common.ACTION_NONE),
        ('', common.ACTION_NONE),
    ],
)
@pytest.mark.experiments3(filename='bank_access.json')
async def test_phonish_person2(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        bank_applications,
        pass_flags,
        action,
):
    uid = '111110'
    phone_id = 'phone_id_2'
    buid = '48c3d180-e14e-4e64-8de3-407b0b3b735a'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(uid, buid, phone_id, pass_flags=pass_flags),
    )
    assert response.status_code == 200
    resp = response.json()
    resp_session_uuid = resp.pop('yabank_session_uuid')
    assert len(resp_session_uuid) > 1
    assert resp == {'action': action, 'yandex_uid': uid}
