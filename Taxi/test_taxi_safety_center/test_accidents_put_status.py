import datetime

import pytest

from taxi_safety_center.repositories import accidents

DEFAULT_HEADER = {
    'X-Yandex-UID': '9876',
    'Accept-Language': 'ru',
    'X-YaTaxi-UserId': '9876',
}

PATH = '/4.0/safety_center/v1/accidents/status'


@pytest.mark.parametrize('accident_happened', [True, False])
async def test_put_accident_status(
        web_app, web_app_client, accident_happened, new_accident,
):
    accident_in_db = new_accident
    header = DEFAULT_HEADER.copy()
    header['X-YaTaxi-UserId'] = accident_in_db.user_id
    put_response = await web_app_client.put(
        PATH,
        json={'accident_happened': accident_happened},
        params={'accident_id': accident_in_db.accident_id},
        headers=header,
    )
    assert put_response.status == 200
    assert await put_response.json() == {}
    patched_accident = await accidents.get_accident(
        accident_in_db.accident_id, context=web_app['context'], log_extra={},
    )
    assert patched_accident.confirmed == accident_happened
    assert isinstance(patched_accident.updated_at, datetime.datetime)


async def test_put_nonexistent_accident_status(web_app, web_app_client):
    put_response = await web_app_client.put(
        PATH,
        json={'accident_happened': True},
        params={'accident_id': 'DUMMY'},
        headers=DEFAULT_HEADER,
    )
    assert put_response.status == 404
    assert await put_response.json() == {'code': 'not_found_error'}


UNAUTHORIZED_BODY = {'code': 'unauthorized_accident_access'}
CORRECT_ID = None  # no id patch => correct id will be used


@pytest.mark.parametrize(
    'crossdevice_enabled,user_id,yandex_uid,resp_code,resp_body',
    [
        (False, CORRECT_ID, CORRECT_ID, 200, {}),
        (False, 'wrong_user_id', CORRECT_ID, 403, UNAUTHORIZED_BODY),
        (True, 'wrong_user_id', CORRECT_ID, 200, {}),
        (True, 'wrong_user_id', '', 403, UNAUTHORIZED_BODY),  # empty uid
        (True, 'wrong_user_id', 'wrong_yandex_uid', 403, UNAUTHORIZED_BODY),
    ],
)
async def test_put_unauthorized_accident_status(
        web_app,
        web_app_client,
        new_accident,
        crossdevice_enabled,
        user_id,
        yandex_uid,
        resp_code,
        resp_body,
):
    web_app['context'].config.CROSSDEVICE_ENABLED = crossdevice_enabled
    user_id = user_id or new_accident.user_id
    yandex_uid = (
        yandex_uid if yandex_uid is not None else new_accident.yandex_uid
    )
    headers = DEFAULT_HEADER.copy()
    headers['X-YaTaxi-UserId'] = user_id
    headers['X-Yandex-UID'] = yandex_uid
    put_response = await web_app_client.put(
        PATH,
        json={'accident_happened': True},
        params={'accident_id': new_accident.accident_id},
        headers=headers,
    )
    assert put_response.status == resp_code
    assert await put_response.json() == resp_body
