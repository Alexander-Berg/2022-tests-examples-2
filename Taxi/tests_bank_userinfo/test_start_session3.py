import pytest

from tests_bank_userinfo import common
from tests_bank_userinfo import utils

BUID = '7948e3a9-623c-4524-a390-9e4264d27a77'
YUID = '111111'
PHONE_ID = 'phone_id_1'
USER_AGENT_TO_PRODUCT = {'__default__': 'WALLET', 'taximeter': 'PRO'}


def insert_product(pgsql, buid, product, agreement_id):
    cursor = pgsql['bank_userinfo'].cursor()
    cursor.execute(
        'INSERT INTO bank_userinfo.user_products(buid, product, agreement_id) '
        'VALUES (%s, %s, %s) '
        'RETURNING id',
        [buid, product, agreement_id],
    )


@pytest.mark.now('2021-06-13T14:00:00Z')
@pytest.mark.config(BANK_USERINFO_USER_AGENT_TO_PRODUCT=USER_AGENT_TO_PRODUCT)
@pytest.mark.config(BANK_USERINFO_CHECK_WALLET_EXISTANCE=True)
@pytest.mark.parametrize('user_product', ['WALLET', 'PRO'])
async def test_sessions_has_products(
        taxi_bank_userinfo, pgsql, user_product, bank_applications,
):
    app_name = 'taximeter' if user_product == 'PRO' else 'sdk_example'
    insert_product(pgsql, BUID, user_product, '1')
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(YUID, BUID, PHONE_ID, app_name=app_name),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {'action': common.ACTION_NONE, 'yandex_uid': YUID}
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == BUID
    assert pg_session.yandex_uid == YUID
    assert pg_session.phone_id == PHONE_ID
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid is None


@pytest.mark.now('2021-06-13T14:00:00Z')
@pytest.mark.config(BANK_USERINFO_USER_AGENT_TO_PRODUCT=USER_AGENT_TO_PRODUCT)
@pytest.mark.config(BANK_USERINFO_CHECK_WALLET_EXISTANCE=False)
@pytest.mark.parametrize('user_product', ['WALLET', 'PRO'])
async def test_sessions_no_products_config_off(
        taxi_bank_userinfo, pgsql, user_product, bank_applications,
):
    app_name = 'taximeter' if user_product == 'PRO' else 'sdk_example'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(YUID, BUID, PHONE_ID, app_name=app_name),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {'action': common.ACTION_NONE, 'yandex_uid': YUID}
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == BUID
    assert pg_session.yandex_uid == YUID
    assert pg_session.phone_id == PHONE_ID
    assert pg_session.status == common.SESSION_STATUS_OK
    assert pg_session.old_session_uuid is None


@pytest.mark.now('2021-06-13T14:00:00Z')
@pytest.mark.experiments3(filename='registration_landing_url.json')
@pytest.mark.config(BANK_USERINFO_USER_AGENT_TO_PRODUCT=USER_AGENT_TO_PRODUCT)
@pytest.mark.config(BANK_USERINFO_CHECK_WALLET_EXISTANCE=True)
@pytest.mark.parametrize(
    'user_product, expected_url',
    [('WALLET', 'no_plus.com'), ('PRO', 'driver.com')],
)
async def test_sessions_no_products_config_on(
        taxi_bank_userinfo,
        pgsql,
        user_product,
        expected_url,
        bank_applications,
):
    app_name = 'taximeter' if user_product == 'PRO' else 'sdk_example'
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=common.get_headers(YUID, BUID, PHONE_ID, app_name=app_name),
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp.pop('yabank_session_uuid')
    assert len(session_uuid) > 1
    assert resp == {
        'action': common.ACTION_OPEN_PRODUCT,
        'product_to_open': user_product,
        'yandex_uid': YUID,
        'landing_url': expected_url,
    }
    pg_session = utils.select_session(pgsql, session_uuid)

    assert pg_session.session_uuid == session_uuid
    assert pg_session.bank_uid == BUID
    assert pg_session.yandex_uid == YUID
    assert pg_session.phone_id == PHONE_ID
    assert pg_session.status == common.SESSION_STATUS_NO_PRODUCT
    assert pg_session.old_session_uuid is None


@pytest.mark.parametrize(
    'taxi_pass_flags,expected_url',
    [(None, 'no_plus.com'), ('', 'no_plus.com'), ('ya-plus', 'has_plus.com')],
)
@pytest.mark.experiments3(filename='registration_landing_url.json')
async def test_bank_registration_landing_url(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        bank_applications,
        taxi_pass_flags,
        expected_url,
):
    uid = '111118'
    headers = common.get_headers(uid)
    headers['X-YaTaxi-Pass-Flags'] = taxi_pass_flags
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=headers,
    )
    assert response.status_code == 200
    resp = response.json()
    resp.pop('yabank_session_uuid')
    assert resp == {
        'action': common.ACTION_BANK_REGISTRATION,
        'yandex_uid': uid,
        'landing_url': expected_url,
        'product_to_open': 'WALLET',
    }


@pytest.mark.parametrize('taxi_pass_flags', [None, '', 'ya-plus'])
async def test_bank_registration_landing_url_no_exp(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        bank_applications,
        taxi_pass_flags,
):
    uid = '111118'
    headers = common.get_headers(uid)
    headers['X-YaTaxi-Pass-Flags'] = taxi_pass_flags
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json=common.START_SESSION_REQUIRED_JSON,
        headers=headers,
    )
    assert response.status_code == 200
    assert 'landing_url' not in response.json()
