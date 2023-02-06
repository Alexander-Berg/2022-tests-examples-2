import copy

import pytest

from test_iiko_integration import stubs

QR_OBJECT_REQUIRED = {
    'id': 'restaurant01',
    'name_tanker_key': 'maximum.kek',
    'position': [37.618423, 55.751244],
    'phone_number': '+70000047448',
    'address_en': 'address_en',
    'address_ru': 'address_ru',
    'geosearch_id': '1400568734',
    'type': 'restaurant',
}
QR_OBJECT_FULL = dict(
    **QR_OBJECT_REQUIRED,
    cashback='30% кэшбека',
    card_image_url='image.jpg',
    work_hours_en='00.00-24.00',
    work_hours_ru='круглосуточно',
)
QR_OBJECT_NO_CASHBACK_TEMPLATE = dict(**QR_OBJECT_REQUIRED, cashback='30%')


def _get_no_cashback_group_info() -> dict:
    group_info = copy.deepcopy(stubs.CONFIG_RESTAURANT_GROUP_INFO)
    group_info['restaurant_group_01']['cashback'] = 0
    return group_info


def _get_full_restorant_config() -> dict:
    restorant_info = copy.deepcopy(stubs.CONFIG_RESTAURANT_INFO)
    restorant_info['restaurant01']['card_image_url'] = 'image.jpg'
    restorant_info['restaurant01']['work_hours_en'] = '00.00-24.00'
    restorant_info['restaurant01']['work_hours_ru'] = 'круглосуточно'
    return restorant_info


@pytest.mark.config(
    IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=stubs.CONFIG_RESTAURANT_GROUP_INFO,
    IIKO_INTEGRATION_RESTAURANT_INFO=stubs.CONFIG_RESTAURANT_INFO,
    IIKO_INTEGRATION_QR_OBJECTS_SETTINGS={
        'cashback_template': '{cashback}% кэшбека',
    },
    IIKO_INTEGRATION_SERVICE_AVAILABLE=True,
)
@pytest.mark.parametrize(
    ('expected_qr_objects', 'service_available'),
    (
        pytest.param(
            [QR_OBJECT_FULL],
            True,
            id='Success',
            marks=pytest.mark.config(
                IIKO_INTEGRATION_RESTAURANT_INFO=_get_full_restorant_config(),
            ),
        ),
        pytest.param(
            [],
            False,
            id='Service unavailable',
            marks=pytest.mark.config(IIKO_INTEGRATION_SERVICE_AVAILABLE=False),
        ),
        pytest.param(
            [],
            True,
            id='No group config',
            marks=pytest.mark.config(
                IIKO_INTEGRATION_RESTAURANT_GROUP_INFO={},
            ),
        ),
        pytest.param(
            [QR_OBJECT_NO_CASHBACK_TEMPLATE],
            True,
            id='No cashback template',
            marks=pytest.mark.config(IIKO_INTEGRATION_QR_OBJECTS_SETTINGS={}),
        ),
        pytest.param(
            [QR_OBJECT_NO_CASHBACK_TEMPLATE],
            True,
            id='Wrong cashback template',
            marks=pytest.mark.config(
                IIKO_INTEGRATION_QR_OBJECTS_SETTINGS={
                    'cashback_template': '{cat}% кэшбека',
                },
            ),
        ),
        pytest.param(
            [QR_OBJECT_REQUIRED],
            True,
            id='No cashback restaurant',
            marks=pytest.mark.config(
                IIKO_INTEGRATION_RESTAURANT_GROUP_INFO=(
                    _get_no_cashback_group_info()
                ),
            ),
        ),
    ),
)
async def test(
        web_app_client, expected_qr_objects: list, service_available: bool,
):
    response = await web_app_client.get('/internal/v1/qr-objects')
    assert response.status == 200
    content = await response.json()
    assert content['qr_objects'] == expected_qr_objects
    assert content['service_available'] == service_available
