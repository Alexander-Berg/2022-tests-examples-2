import datetime

import pytest

from taxi_corp_announcements.api.common import announcements_helper as helper
from taxi_corp_announcements.internal import base_context

NOW = datetime.datetime.now().replace(microsecond=0)
ISO_NOW = NOW.isoformat()
MOCK_ID = '123'
X_YANDEX_UID = '12345'


@pytest.mark.parametrize(
    'request_data, expected_data',
    [
        pytest.param(
            {
                'announcement_type': 'news',
                'admin_title': 'Название в админке',
                'title': 'Заголовок',
                'text': 'Текст новости',
                'priority': 0,
                'cta_is_active': True,
                'cta_title': 'CTA button title',
                'cta_url': 'https://yandex.ru',
                'display_conditions': [
                    {'condition': 'country', 'values': [{'filter': 'rus'}]},
                    {
                        'condition': 'clients',
                        'values': [
                            {'filter': 'client_id1'},
                            {'filter': 'client_id2'},
                        ],
                    },
                    {
                        'condition': 'roles',
                        'values': [
                            {'filter': 'manager'},
                            {'filter': 'department_manager'},
                        ],
                    },
                    {
                        'condition': 'payment_type',
                        'values': [{'filter': 'prepaid'}],
                    },
                    {
                        'condition': 'common_contract',
                        'values': [{'filter': 'available_enabled'}],
                    },
                ],
                'publish_at': ISO_NOW,
                'comment': 'some comment',
                'triggers_in_sf': True,
            },
            {
                'announcement_id': MOCK_ID,
                'announcement_type': 'news',
                'admin_title': 'Название в админке',
                'title': 'Заголовок',
                'text': 'Текст новости',
                'priority': 0,
                'cta_is_active': True,
                'cta_title': 'CTA button title',
                'cta_url': 'https://yandex.ru',
                'base_image_id': None,
                'preview_image_id': None,
                'clients_filter': ['client_id1', 'client_id2'],
                'roles_filter': ['manager', 'department_manager'],
                'country_filter': ['rus'],
                'payment_type_filter': ['prepaid'],
                'common_contract_filter': ['available_enabled'],
                'vat_filter': ['with_vat'],
                'publish_at': NOW,
                'comment': 'some comment',
                'created_by': int(X_YANDEX_UID),
            },
            id='create_announcement',
        ),
        pytest.param(
            {
                'announcement_type': 'news',
                'admin_title': 'Название в админке',
                'title': 'Заголовок',
                'text': 'Текст новости',
                'priority': 0,
                'cta_is_active': True,
                'cta_title': 'CTA button title',
                'cta_url': 'https://yandex.ru',
                'display_conditions': [],
                'publish_at': ISO_NOW,
                'comment': 'some comment',
                'triggers_in_sf': True,
            },
            {
                'announcement_id': MOCK_ID,
                'announcement_type': 'news',
                'admin_title': 'Название в админке',
                'title': 'Заголовок',
                'text': 'Текст новости',
                'priority': 0,
                'cta_is_active': True,
                'cta_title': 'CTA button title',
                'cta_url': 'https://yandex.ru',
                'base_image_id': None,
                'preview_image_id': None,
                'clients_filter': [],
                'roles_filter': [],
                'country_filter': [],
                'payment_type_filter': [],
                'common_contract_filter': [],
                'vat_filter': ['with_vat'],
                'publish_at': NOW,
                'comment': 'some comment',
                'created_by': int(X_YANDEX_UID),
            },
            id='create_announcement',
        ),
        pytest.param(
            {
                'announcement_type': 'news',
                'admin_title': 'Название в админке',
                'title': 'Заголовок',
                'text': 'Текст новости',
                'priority': 0,
                'cta_is_active': False,
                'cta_title': '',
                'cta_url': '',
                'base_image_id': 'image_id_001',
                'preview_image_id': 'image_id_002',
                'display_conditions': [
                    {'condition': 'country', 'values': [{'filter': 'rus'}]},
                    {
                        'condition': 'clients',
                        'values': [
                            {'filter': 'client_id1'},
                            {'filter': 'client_id2'},
                        ],
                    },
                    {
                        'condition': 'roles',
                        'values': [
                            {'filter': 'manager'},
                            {'filter': 'department_manager'},
                        ],
                    },
                    {
                        'condition': 'payment_type',
                        'values': [{'filter': 'prepaid'}],
                    },
                    {
                        'condition': 'common_contract',
                        'values': [{'filter': 'available_disabled'}],
                    },
                    {
                        'condition': 'vat',
                        'values': [{'filter': 'without_vat'}],
                    },
                ],
                'publish_at': ISO_NOW,
                'comment': 'some comment',
                'triggers_in_sf': True,
            },
            {
                'announcement_id': MOCK_ID,
                'announcement_type': 'news',
                'admin_title': 'Название в админке',
                'title': 'Заголовок',
                'text': 'Текст новости',
                'priority': 0,
                'cta_is_active': False,
                'cta_title': '',
                'cta_url': '',
                'base_image_id': 'image_id_001',
                'preview_image_id': 'image_id_002',
                'clients_filter': ['client_id1', 'client_id2'],
                'roles_filter': ['manager', 'department_manager'],
                'country_filter': ['rus'],
                'payment_type_filter': ['prepaid'],
                'common_contract_filter': ['available_disabled'],
                'vat_filter': ['without_vat'],
                'publish_at': NOW,
                'comment': 'some comment',
                'created_by': int(X_YANDEX_UID),
            },
            id='create_announcement_with_image',
        ),
        pytest.param(
            {
                'announcement_type': 'promo',
                'admin_title': 'Название в админке',
                'title': 'Заголовок',
                'text': 'Текст новости',
                'priority': 1,
                'cta_is_active': False,
                'cta_title': '',
                'cta_url': '',
                'base_image_id': 'image_id_001',
                'preview_image_id': 'image_id_002',
                'display_conditions': [
                    {'condition': 'country', 'values': [{'filter': 'rus'}]},
                    {
                        'condition': 'clients',
                        'values': [
                            {'filter': 'client_id1'},
                            {'filter': 'client_id2'},
                        ],
                    },
                    {
                        'condition': 'roles',
                        'values': [
                            {'filter': 'manager'},
                            {'filter': 'department_manager'},
                        ],
                    },
                    {
                        'condition': 'payment_type',
                        'values': [{'filter': 'prepaid'}],
                    },
                    {
                        'condition': 'common_contract',
                        'values': [{'filter': 'available_disabled'}],
                    },
                    {
                        'condition': 'vat',
                        'values': [
                            {'filter': 'with_vat'},
                            {'filter': 'without_vat'},
                        ],
                    },
                ],
                'publish_at': ISO_NOW,
                'comment': 'some comment',
                'triggers_in_sf': True,
            },
            {
                'announcement_id': MOCK_ID,
                'announcement_type': 'promo',
                'admin_title': 'Название в админке',
                'title': 'Заголовок',
                'text': 'Текст новости',
                'priority': 1,
                'cta_is_active': False,
                'cta_title': '',
                'cta_url': '',
                'base_image_id': 'image_id_001',
                'preview_image_id': 'image_id_002',
                'clients_filter': ['client_id1', 'client_id2'],
                'roles_filter': ['manager', 'department_manager'],
                'country_filter': ['rus'],
                'payment_type_filter': ['prepaid'],
                'common_contract_filter': ['available_disabled'],
                'vat_filter': ['with_vat', 'without_vat'],
                'publish_at': NOW,
                'comment': 'some comment',
                'created_by': int(X_YANDEX_UID),
            },
            id='create_promo_announcement',
        ),
    ],
)
@pytest.mark.pgsql('corp_announcements', files=('images.sql',))
@pytest.mark.now(ISO_NOW)
async def test_create_announcement(
        web_app_client,
        web_context,
        monkeypatch,
        mockserver,
        request_data,
        expected_data,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    response = await web_app_client.post(
        '/v1/admin/announcements/',
        json=request_data,
        headers={'X-Yandex-Uid': X_YANDEX_UID},
    )
    ctx = base_context.Web(web_context, 'fetch_announcement_by_id')
    announcement = await helper.fetch_announcement_by_id(ctx, MOCK_ID)

    assert response.status == 200
    content = await response.json()
    assert content == {'announcement_id': MOCK_ID}

    for key, value in expected_data.items():
        assert announcement[key] == value, key


async def test_create_without_creator(web_app_client):
    request_data = {
        'announcement_type': 'news',
        'admin_title': 'Название в админке',
        'title': 'Заголовок_new',
        'text': 'Текст новости_new',
        'priority': 0,
        'cta_is_active': False,
        'cta_title': '',
        'cta_url': '',
        'base_image_id': None,
        'preview_image_id': None,
        'display_conditions': [
            {'condition': 'payment_type', 'values': [{'filter': 'prepaid'}]},
        ],
        'publish_at': ISO_NOW,
    }
    response = await web_app_client.post(
        '/v1/admin/announcements/', json=request_data, headers={},
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'details': {'reason': 'X-Yandex-Uid is required parameter'},
        'message': 'Some parameters are invalid',
    }


@pytest.mark.parametrize(
    'display_conditions, expected_error',
    [
        pytest.param(
            [{'condition': 'payment_type', 'values': [{'filter': 'wrong'}]}],
            {'payment_type': ['wrong']},
            id='wrong_payment_filters',
        ),
        pytest.param(
            [{'condition': 'roles', 'values': [{'filter': 'clients'}]}],
            {'roles': ['clients']},
            id='wrong_roles_filters',
        ),
        pytest.param(
            [{'condition': 'country', 'values': [{'filter': 'test'}]}],
            {'country': ['test']},
            id='wrong_country_filters',
        ),
        pytest.param(
            [
                {
                    'condition': 'common_contract',
                    'values': [{'filter': 'incorrect'}],
                },
            ],
            {'common_contract': ['incorrect']},
            id='wrong_common_contract_filters',
        ),
    ],
)
async def test_create_wrong_filters(
        web_app_client, monkeypatch, display_conditions, expected_error,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    request_data = {
        'announcement_type': 'news',
        'admin_title': 'Название в админке',
        'title': 'Заголовок_new',
        'text': 'Текст новости_new',
        'priority': 0,
        'cta_is_active': False,
        'cta_title': '',
        'cta_url': '',
        'display_conditions': display_conditions,
        'publish_at': ISO_NOW,
        'triggers_in_sf': True,
    }
    response = await web_app_client.post(
        '/v1/admin/announcements/',
        json=request_data,
        headers={'X-Yandex-Uid': X_YANDEX_UID},
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'status': 'error',
        'code': 'invalid-input',
        'message': 'Invalid filters provided',
        'details': expected_error,
    }


@pytest.mark.parametrize(
    'patch_data',
    [
        pytest.param({'comment': 123}, id='create_announcement'),
        pytest.param({'text': None}, id='create_announcement_text_null'),
        pytest.param(
            {'base_image_id': 'unknown_image_id_001'},
            id='create_announcement_unknown_image',
        ),
    ],
)
@pytest.mark.pgsql('corp_announcements', files=('images.sql',))
@pytest.mark.now(ISO_NOW)
async def test_create_announcement_error(
        web_app_client, web_context, monkeypatch, mockserver, patch_data,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    base_request = {
        'announcement_type': 'news',
        'admin_title': 'Название в админке',
        'title': 'Заголовок',
        'text': 'Текст новости',
        'priority': 0,
        'cta_is_active': False,
        'cta_title': '',
        'cta_url': '',
        'display_conditions': [
            {'condition': 'country', 'values': [{'filter': 'rus'}]},
            {
                'condition': 'clients',
                'values': [{'filter': 'client_id1'}, {'filter': 'client_id2'}],
            },
            {
                'condition': 'roles',
                'values': [
                    {'filter': 'manager'},
                    {'filter': 'department_manager'},
                ],
            },
            {'condition': 'payment_type', 'values': [{'filter': 'prepaid'}]},
            {
                'condition': 'common_contract',
                'values': [{'filter': 'available_disabled'}],
            },
        ],
        'publish_at': ISO_NOW,
        'comment': 'some comment',
    }
    request_data = dict(base_request, **patch_data)
    response = await web_app_client.post(
        '/v1/admin/announcements/',
        json=request_data,
        headers={'X-Yandex-Uid': X_YANDEX_UID},
    )
    content = await response.json()
    assert response.status == 400, content
