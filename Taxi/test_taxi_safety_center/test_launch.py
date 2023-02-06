import pytest

from taxi_safety_center import models
from taxi_safety_center.repositories import contacts as contacts_repository
from test_taxi_safety_center import data_generators


MAX_CONTACTS = 5

EMERGENCY_NUMBERS = {'rus': '112', 'sgs': '999', '__default__': '000'}

UI_TYPE = {'frauder': 'button', '__default__': 'enabled_checkbox'}

LAUNCH_PATH = '/4.0/safety_center/v1/launch'

YANDEX_UID = 'yandex_uid'
USER_ID = 'user_id'
ORDER_ID = '4321'

DEFAULT_HEADERS = {
    'X-Yandex-UID': YANDEX_UID,
    'Accept-Language': 'ru-RU',
    'X-YaTaxi-UserId': USER_ID,
}

ZONE_NAME = 'Москва'

SHARING_STUB = {
    # 'button' if user is frauder
    # 'enabled_checkbox|disabled_checkbox|button'
    'ui_type': 'enabled_checkbox',
    'contacts': [data_generators.significant_contact(0)],
    'max_contacts': MAX_CONTACTS,
}

CORRECT_BODY = {
    'sharing': SHARING_STUB,
    'emergency_number': '112',
    'country': 'rus',
}


@pytest.fixture(name='new_contact')
async def _new_contact(web_app):
    contacts = models.Phones(
        [
            models.Phone(
                name='Важный контакт 0',
                number='+79876543210',
                personal_phone_id='+79876543210_id',
            ),
        ],
    )
    await contacts_repository.insert_contacts(
        uid=YANDEX_UID,
        contacts=contacts,
        context=web_app['context'],
        log_extra={},
    )


@pytest.mark.config(
    SAFETY_CENTER_MAX_CONTACTS=MAX_CONTACTS,
    SAFETY_CENTER_EMERGENCY_NUMBERS=EMERGENCY_NUMBERS,
    SAFETY_CENTER_UI_TYPE=UI_TYPE,
    SAFETY_CENTER_PERSONAL_ENABLED=False,
)
@pytest.mark.parametrize('order_id', [None, ORDER_ID])
async def test_launch_200(
        web_app_client,
        mock_archive_response,
        mock_personal_response,
        new_contact,
        order_id,
):
    mock_personal_response(
        contact['phone_number'] for contact in SHARING_STUB['contacts']
    )
    mock_archive_response(
        {'nz': ZONE_NAME, 'user_id': USER_ID, 'yandex_uid': YANDEX_UID},
        {'nearest_zone': ZONE_NAME, 'id': order_id},
    )
    path = LAUNCH_PATH + ('' if order_id is None else '?order_id=' + order_id)
    response = await web_app_client.get(path, headers=DEFAULT_HEADERS)
    assert response.status == 200
    assert await response.json() == CORRECT_BODY


UNAUTHORIZED_BODY = {'code': 'unauthorized_order_access'}
CORRECT_ID = None


@pytest.mark.config(
    SAFETY_CENTER_MAX_CONTACTS=MAX_CONTACTS,
    SAFETY_CENTER_EMERGENCY_NUMBERS=EMERGENCY_NUMBERS,
    SAFETY_CENTER_UI_TYPE=UI_TYPE,
    SAFETY_CENTER_PERSONAL_ENABLED=True,
)
@pytest.mark.parametrize(
    'crossdevice_enabled,user_id,yandex_uid,resp_status,resp_body',
    [
        (False, 'wrong_user_id', CORRECT_ID, 403, UNAUTHORIZED_BODY),
        (True, 'wrong_user_id', 'wrong_yandex_uid', 403, UNAUTHORIZED_BODY),
        (True, 'wrong_user_id', CORRECT_ID, 200, CORRECT_BODY),
    ],
)
async def test_launch_authorization(
        web_app,
        web_app_client,
        mock_archive_response,
        mock_personal_response,
        new_contact,
        crossdevice_enabled,
        user_id,
        yandex_uid,
        resp_status,
        resp_body,
):
    web_app['context'].config.CROSSDEVICE_ENABLED = crossdevice_enabled
    headers = DEFAULT_HEADERS.copy()
    if user_id != CORRECT_ID:
        headers['X-YaTaxi-UserId'] = user_id
    if yandex_uid != CORRECT_ID:
        headers['X-Yandex-UID'] = yandex_uid

    mock_personal_response(
        [contact['phone_number'] for contact in SHARING_STUB['contacts']],
    )
    mock_archive_response(
        {'nz': ZONE_NAME, 'user_id': USER_ID, 'user_uid': YANDEX_UID},
        {'nearest_zone': ZONE_NAME, 'order_id': ORDER_ID},
    )
    path = LAUNCH_PATH + '?order_id=' + ORDER_ID
    response = await web_app_client.get(path, headers=headers)
    assert response.status == resp_status
    assert resp_body == await response.json()
