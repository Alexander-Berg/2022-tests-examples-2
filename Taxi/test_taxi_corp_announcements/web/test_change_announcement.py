import datetime

import pytest

from taxi_corp_announcements.api.common import announcements_helper as helper
from taxi_corp_announcements.internal import base_context


NOW = datetime.datetime.now().replace(microsecond=0)
ISO_NOW = NOW.isoformat()
MOCK_ID = '123'
X_YANDEX_UID = '12345'
X_YATAXI_API_KEY = 'test_api_key'


@pytest.mark.parametrize(
    'announcement_id, request_data, expected_data',
    [
        pytest.param(
            '12345',
            {
                'announcement_type': 'promo',
                'admin_title': 'Название в админке_new',
                'triggers_in_sf': False,
                'title': 'Заголовок_new',
                'text': 'Текст новости_new',
                'priority': 1,
                'cta_is_active': True,
                'cta_title': 'CTA button title_new',
                'cta_url': 'https://yandex.ru/new',
                'base_image_id': 'image_id_001',
                'preview_image_id': 'image_id_002',
                'display_conditions': [
                    {'condition': 'country', 'values': [{'filter': 'rus'}]},
                    {
                        'condition': 'roles',
                        'values': [
                            {'filter': 'client'},
                            {'filter': 'department_secretary'},
                        ],
                    },
                    {
                        'condition': 'payment_type',
                        'values': [{'filter': 'postpaid'}],
                    },
                    {
                        'condition': 'common_contract',
                        'values': [{'filter': 'available_enabled'}],
                    },
                ],
            },
            {
                'announcement_id': '12345',
                'announcement_type': 'promo',
                'admin_title': 'Название в админке_new',
                'title': 'Заголовок_new',
                'text': 'Текст новости_new',
                'priority': 1,
                'cta_is_active': True,
                'cta_title': 'CTA button title_new',
                'cta_url': 'https://yandex.ru/new',
                'base_image_id': 'image_id_001',
                'preview_image_id': 'image_id_002',
                'clients_filter': ['client_id1', 'client_id2'],
                'roles_filter': ['client', 'department_secretary'],
                'country_filter': ['rus'],
                'payment_type_filter': ['postpaid'],
                'common_contract_filter': ['available_enabled'],
                'created_by': int(X_YANDEX_UID),
            },
            id='change_announcement',
        ),
        pytest.param(
            '12345',
            {
                'announcement_type': 'promo',
                'admin_title': 'Название в админке_new',
                'title': 'Заголовок_new',
                'text': 'Текст новости_new',
                'priority': 1,
                'cta_is_active': True,
                'cta_title': 'CTA button title_new',
                'cta_url': 'https://yandex.ru/new',
                'base_image_id': 'image_id_001',
                'preview_image_id': 'image_id_002',
                'display_conditions': [],
                'triggers_in_sf': True,
            },
            {
                'announcement_id': '12345',
                'announcement_type': 'promo',
                'admin_title': 'Название в админке_new',
                'title': 'Заголовок_new',
                'text': 'Текст новости_new',
                'priority': 1,
                'cta_is_active': True,
                'cta_title': 'CTA button title_new',
                'cta_url': 'https://yandex.ru/new',
                'base_image_id': 'image_id_001',
                'preview_image_id': 'image_id_002',
                'clients_filter': [],
                'roles_filter': [],
                'country_filter': [],
                'payment_type_filter': [],
                'common_contract_filter': [],
                'created_by': int(X_YANDEX_UID),
            },
            id='change_announcement',
        ),
        pytest.param(
            '12345',
            {
                'announcement_type': 'promo',
                'admin_title': 'Название в админке_new',
                'triggers_in_sf': False,
                'title': 'Заголовок_new',
                'text': 'Текст новости_new',
                'priority': 2,
                'base_image_id': 'image_id_001',
                'cta_is_active': True,
                'cta_title': 'CTA button title_new',
                'cta_url': 'https://yandex.ru/new',
                'display_conditions': [
                    {'condition': 'payment_type', 'values': []},
                    {'condition': 'common_contract', 'values': []},
                ],
                'publish_at': ISO_NOW,
            },
            {
                'announcement_id': '12345',
                'announcement_type': 'promo',
                'triggers_in_sf': False,
                'admin_title': 'Название в админке_new',
                'title': 'Заголовок_new',
                'text': 'Текст новости_new',
                'priority': 2,
                'base_image_id': 'image_id_001',
                'preview_image_id': None,
                'clients_filter': ['client_id1', 'client_id2'],
                'roles_filter': ['manager', 'department_manager'],
                'country_filter': ['rus'],
                'payment_type_filter': [],
                'common_contract_filter': [],
                'publish_at': NOW,
                'created_by': int(X_YANDEX_UID),
            },
            id='change_publish_datetime_not_approved',
        ),
        pytest.param(
            '34567',
            {
                'announcement_type': 'news',
                'admin_title': 'Название в админке_new',
                'triggers_in_sf': False,
                'title': 'Заголовок_new',
                'text': 'Текст новости_new',
                'priority': 0,
                'base_image_id': 'image_id_001',
                'cta_is_active': True,
                'cta_title': 'CTA button title_new',
                'cta_url': 'https://yandex.ru/new',
                'display_conditions': [
                    {'condition': 'payment_type', 'values': []},
                    {'condition': 'common_contract', 'values': []},
                ],
                'publish_at': ISO_NOW,
            },
            {
                'announcement_id': '34567',
                'announcement_type': 'news',
                'triggers_in_sf': False,
                'admin_title': 'Название в админке_new',
                'title': 'Заголовок_new',
                'text': 'Текст новости_new',
                'priority': 0,
                'base_image_id': 'image_id_001',
                'preview_image_id': None,
                'clients_filter': ['client_id1', 'client_id2'],
                'roles_filter': ['manager', 'department_manager'],
                'country_filter': ['rus'],
                'payment_type_filter': [],
                'common_contract_filter': [],
                'publish_at': NOW,
                'created_by': int(X_YANDEX_UID),
            },
            id='change_promo',
        ),
    ],
)
@pytest.mark.pgsql('corp_announcements', files=('announcements.sql',))
@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'default_language': 'ru', 'web_ui_languages': ['ru', 'en']},
    },
)
async def test_change_announcement(
        web_app_client,
        web_context,
        monkeypatch,
        announcement_id,
        request_data,
        expected_data,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)
    response = await web_app_client.put(
        '/v1/admin/announcement/',
        json=request_data,
        params={'announcement_id': announcement_id},
        headers={
            'X-YaTaxi-Api-Key': X_YATAXI_API_KEY,
            'X-Yandex-Uid': X_YANDEX_UID,
        },
    )
    ctx = base_context.Web(web_context, 'fetch_announcement_by_id')

    assert response.status == 200
    content = await response.json()
    assert content == {}

    announcement = await helper.fetch_announcement_by_id(ctx, announcement_id)
    for key, value in expected_data.items():
        assert announcement[key] == value, key


@pytest.mark.parametrize(
    'params, request_data, expected_status, expected_error',
    [
        (
            {'announcement_id': '23456'},
            {
                'announcement_type': 'promo',
                'admin_title': 'Название в админке_new',
                'triggers_in_sf': False,
                'title': 'Заголовок_new',
                'text': 'Текст новости_new',
                'priority': 3,
                'cta_is_active': True,
                'cta_title': 'CTA button title_new',
                'cta_url': 'https://yandex.ru/new',
                'base_image_id': 'image_id_001_123123123',
                'preview_image_id': 'image_id_001',
                'display_conditions': [],
            },
            400,
            {
                'status': 'error',
                'code': 'invalid-input',
                'message': 'Invalid image ids',
                'details': {'image_id_001_123123123': 'Unknown image id'},
            },
        ),
        (
            {},
            {
                'announcement_type': 'promo',
                'admin_title': 'Название в админке_new',
                'triggers_in_sf': False,
                'title': 'Заголовок_new',
                'text': 'Текст новости_new',
                'priority': 3,
                'cta_is_active': True,
                'cta_title': 'CTA button title_new',
                'cta_url': 'https://yandex.ru/new',
                'base_image_id': 'image_id_001',
                'preview_image_id': 'image_id_001',
                'display_conditions': [],
            },
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Some parameters are invalid',
                'details': {'reason': 'announcement_id is required parameter'},
            },
        ),
        (
            {'announcement_id': 'not_exists'},
            {
                'announcement_type': 'promo',
                'admin_title': 'Название в админке_new',
                'triggers_in_sf': False,
                'title': 'Заголовок_new',
                'text': 'Текст новости_new',
                'priority': 3,
                'cta_is_active': True,
                'cta_title': 'CTA button title_new',
                'cta_url': 'https://yandex.ru/new',
                'base_image_id': 'image_id_001',
                'preview_image_id': 'image_id_001',
                'display_conditions': [],
            },
            404,
            {
                'status': 'error',
                'code': 'invalid-input',
                'message': 'announcement not found',
                'details': {},
            },
        ),
        (
            {'announcement_id': '23456'},
            {
                'announcement_type': 'promo',
                'admin_title': 'Название в админке_new',
                'triggers_in_sf': False,
                'title': 'Заголовок_new',
                'text': 'Текст новости_new',
                'priority': 3,
                'cta_is_active': True,
                'cta_title': 'CTA button title_new',
                'cta_url': 'https://yandex.ru/new',
                'base_image_id': 'image_id_001',
                'preview_image_id': 'image_id_001',
                'display_conditions': [],
                'publish_at': ISO_NOW,
            },
            400,
            {
                'status': 'error',
                'code': 'invalid-input',
                'message': 'announcement is already sent',
                'details': {},
            },
        ),
    ],
)
@pytest.mark.pgsql('corp_announcements', files=('announcements.sql',))
async def test_change_announcement_fail(
        web_app_client,
        web_context,
        params,
        request_data,
        expected_status,
        expected_error,
):
    response = await web_app_client.put(
        '/v1/admin/announcement/',
        json=request_data,
        params=params,
        headers={
            'X-YaTaxi-Api-Key': X_YATAXI_API_KEY,
            'X-Yandex-Uid': X_YANDEX_UID,
        },
    )

    assert response.status == expected_status
    content = await response.json()
    assert content == expected_error, content
