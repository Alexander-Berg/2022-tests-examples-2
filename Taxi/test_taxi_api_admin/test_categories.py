import os

import pytest

import test_taxi_api_admin


SCHEMES_PATH = os.path.join(
    os.path.dirname(test_taxi_api_admin.__file__), 'static', 'test_categories',
)


@pytest.fixture(name='services_schemes_path')
def _services_schemes_path():
    return f'{SCHEMES_PATH}/services_schemes/'


@pytest.fixture(name='actions_path')
def _actions_path():
    return f'{SCHEMES_PATH}/global_entities/actions.yaml'


@pytest.fixture(name='sections_path')
def _sections_path():
    return f'{SCHEMES_PATH}/global_entities/sections.yaml'


@pytest.fixture(name='categories_path')
def _categories_path():
    return f'{SCHEMES_PATH}/global_entities/categories.yaml'


@pytest.mark.parametrize(
    'actions,permissions,expected',
    [
        # без пересечений
        (
            [{'action_id': 'admin_action', 'title': 'title'}],
            {
                'categories': [
                    {
                        'id': 'admin_category',
                        'name': 'name',
                        'permissions': [
                            {
                                'action': '__custom__',
                                'comment': None,
                                'sections': ['section'],
                                'id': 'admin_permission',
                            },
                        ],
                    },
                ],
            },
            {'other_service': True, 'service': True},
        ),
        # пересечение audit_action: exist_action_id в service и admin-py2
        (
            [
                {
                    'action_id': 'exist_action_id',
                    'title': 'отличный тайтл от схемы',
                    'comment': 'просто тестовый коммент',
                },
                {'action_id': 'admin_action', 'title': 'title'},
            ],
            {
                'categories': [
                    {
                        'id': 'admin_category',
                        'name': 'name',
                        'permissions': [
                            {
                                'action': '__custom__',
                                'comment': None,
                                'sections': ['section'],
                                'id': 'admin_permission',
                            },
                        ],
                    },
                ],
            },
            {'other_service': True, 'service': False},
        ),
        # audit_action: exist_action_id(одинаковые) в service и admin-py2
        (
            [
                {
                    'action_id': 'exist_action_id',
                    'title': 'просто тестовый тайтл',
                    'comment': 'просто тестовый коммент',
                },
                {'action_id': 'admin_action', 'title': 'title'},
            ],
            {
                'categories': [
                    {
                        'id': 'admin_category',
                        'name': 'name',
                        'permissions': [
                            {
                                'action': '__custom__',
                                'comment': None,
                                'sections': ['section'],
                                'id': 'admin_permission',
                            },
                        ],
                    },
                ],
            },
            {'other_service': True, 'service': True},
        ),
        # пересечение new_category(разные имена) + объявленый пермишен
        (
            [{'action_id': 'admin_action', 'title': 'title'}],
            {
                'categories': [
                    {
                        'id': 'admin_category',
                        'name': 'name',
                        'permissions': [
                            {
                                'action': '__custom__',
                                'comment': None,
                                'sections': ['section'],
                                'id': 'admin_permission',
                            },
                        ],
                    },
                    {
                        'id': 'new_category',
                        'name': 'name',
                        'permissions': [
                            {
                                'action': '__custom__',
                                'comment': None,
                                'sections': ['section'],
                                'id': 'not_use_permission',
                            },
                        ],
                    },
                ],
            },
            {'other_service': False, 'service': False},
        ),
        # пересечение new_category(одинаковые имена)
        (
            [{'action_id': 'admin_action', 'title': 'title'}],
            {
                'categories': [
                    {
                        'id': 'admin_category',
                        'name': 'name',
                        'permissions': [
                            {
                                'action': '__custom__',
                                'comment': None,
                                'sections': ['section'],
                                'id': 'admin_permission',
                            },
                        ],
                    },
                    {
                        'id': 'new_category',
                        'name': 'first',
                        'permissions': [
                            {
                                'action': '__custom__',
                                'comment': None,
                                'sections': ['section'],
                                'id': 'not_use_permission',
                            },
                        ],
                    },
                ],
            },
            {'other_service': True, 'service': True},
        ),
        # одинаковые пермишены root_permission
        (
            [{'action_id': 'admin_action', 'title': 'title'}],
            {
                'categories': [
                    {
                        'id': 'admin_category',
                        'name': 'name',
                        'permissions': [
                            {
                                'action': '__custom__',
                                'comment': None,
                                'sections': ['section'],
                                'id': 'admin_permission',
                            },
                        ],
                    },
                    {
                        'id': 'new_category',
                        'name': 'first',
                        'permissions': [
                            {
                                'action': '__custom__',
                                'comment': 'интересный комментарий',
                                'sections': ['section'],
                                'id': 'root_permission',
                            },
                        ],
                    },
                ],
            },
            {'other_service': True, 'service': True},
        ),
        # пересечение пермишена root_permission
        (
            [{'action_id': 'admin_action', 'title': 'title'}],
            {
                'categories': [
                    {
                        'id': 'admin_category',
                        'name': 'name',
                        'permissions': [
                            {
                                'action': '__custom__',
                                'comment': None,
                                'sections': ['section'],
                                'id': 'admin_permission',
                            },
                        ],
                    },
                    {
                        'id': 'new_category',
                        'name': 'first',
                        'permissions': [
                            {
                                'action': '__custom__',
                                'comment': 'другой комментарий',
                                'sections': ['section'],
                                'id': 'root_permission',
                            },
                        ],
                    },
                ],
            },
            {'other_service': False, 'service': False},
        ),
    ],
)
async def test_intersection_categories(
        taxi_api_admin_client,
        taxi_api_admin_app,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        actions,
        permissions,
        expected,
):
    @patch_aiohttp_session(
        'https://ymsh-admin-unstable.tst.mobile.yandex-team.ru',
    )
    def _patch_admin(method, url, **kwargs):
        if 'audit/actions/list/' in url:
            return response_mock(text=str(actions), json=actions)
        return response_mock(text=str(permissions), json=permissions)

    response = await taxi_api_admin_client.get('/ping')
    assert response.status == 200

    services_schemes = taxi_api_admin_app.ctx.services_schemes
    monkeypatch.setattr(services_schemes, '_services_info', None)
    await services_schemes.on_startup()

    response = await taxi_api_admin_client.get('/ping')
    assert response.status == 200

    services_info = services_schemes.services_info.schemes_info
    for service_name, service_info in services_info.items():
        assert service_info.is_valid == expected[service_name], (
            service_info.errors,
            service_name,
        )
