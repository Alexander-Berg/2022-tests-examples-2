from typing import List

import pytest

from chatterbox.api import rights
from test_chatterbox import plugins as conftest


@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': 'Первая линия', 'sort_order': 1, 'priority': 3},
        'zen': {
            'name': 'Линия Дзена',
            'sort_order': 1,
            'priority': 3,
            'profile': 'support-zen',
        },
    },
    CHATTERBOX_LINES_PERMISSIONS={},
)
async def test_available_lines_superuser(cbox: conftest.CboxWrap):
    await cbox.post('/v1/lines/available/', data={})

    assert cbox.status == 200
    assert cbox.body_data == {
        'available_lines': [
            {
                'line': 'first',
                'line_name': 'Первая линия',
                'open_chats': 1,
                'types': ['client'],
                'mode': 'offline',
                'can_take': True,
                'can_search': True,
                'logbroker_telephony': False,
            },
            {
                'line': 'zen',
                'line_name': 'Линия Дзена',
                'open_chats': 0,
                'types': ['client'],
                'mode': 'offline',
                'can_take': True,
                'can_search': True,
                'logbroker_telephony': False,
            },
        ],
    }


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': 'Первая линия', 'sort_order': 1, 'priority': 3},
    },
    CHATTERBOX_LINES_PERMISSIONS={
        'first': {
            'take': [{'permissions': [rights.CHATTERBOX_CLIENT_FIRST_LINE]}],
        },
    },
)
@pytest.mark.parametrize('is_open_chats_permitted', (True, False))
async def test_available_lines_open_chats_permissions(
        cbox: conftest.CboxWrap, patch_auth, is_open_chats_permitted: dict,
):
    groups = ['readonly', 'client_first']
    if is_open_chats_permitted:
        groups.append('get_open_chats_in_lines')
    patch_auth(superuser=False, groups=groups)
    await cbox.post('/v1/lines/available/', data={})

    assert cbox.status == 200
    if is_open_chats_permitted:
        assert cbox.body_data['available_lines'][0]['open_chats'] == 1
    else:
        assert 'open_chats' not in cbox.body_data['available_lines'][0]


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': 'Первая линия', 'sort_order': 1, 'priority': 3},
    },
    CHATTERBOX_LINES_PERMISSIONS={},
)
@pytest.mark.parametrize(
    ('line_permissions', 'is_take_permitted', 'is_search_permitted'),
    (
        # Line without permissions in config not available
        ({}, False, False),
        # Take permissions also grant search permissions
        (
            {'take': [{'permissions': [rights.CHATTERBOX_CLIENT_FIRST_LINE]}]},
            True,
            True,
        ),
        (
            {
                'search': [
                    {
                        'permissions': [
                            rights.CHATTERBOX_CLIENT_FIRST_LINE_SEARCH,
                        ],
                    },
                ],
            },
            False,
            True,
        ),
    ),
)
async def test_available_lines_with_permissions(
        cbox: conftest.CboxWrap,
        patch_auth,
        line_permissions: dict,
        is_take_permitted: bool,
        is_search_permitted: bool,
):
    patch_auth(
        superuser=False,
        groups=['readonly', 'client_first', 'client_first_search'],
    )
    cbox.app.config.CHATTERBOX_LINES_PERMISSIONS['first'] = line_permissions

    await cbox.post('/v1/lines/available/', data={})

    assert cbox.status == 200
    assert cbox.body_data == {
        'available_lines': [
            {
                'line': 'first',
                'line_name': 'Первая линия',
                'types': ['client'],
                'mode': 'offline',
                'can_take': is_take_permitted,
                'can_search': is_search_permitted,
                'logbroker_telephony': False,
            },
        ],
    }


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(
    CHATTERBOX_LINES={
        'english': {'name': 'English', 'sort_order': 1, 'priority': 3},
    },
    CHATTERBOX_LINES_PERMISSIONS={},
)
@pytest.mark.parametrize(
    ('line_permissions', 'is_take_permitted', 'is_search_permitted'),
    (
        # Take permissions also grant search permissions
        (
            {
                'take': [
                    {
                        'permissions': [
                            rights.CHATTERBOX_CLIENT_INTERNATIONAL_LINE,
                        ],
                        'countries': ['eng'],
                    },
                ],
            },
            True,
            True,
        ),
        (
            {
                'search': [
                    {
                        'permissions': [
                            rights.CHATTERBOX_CLIENT_INTERNATIONAL_LINE_SEARCH,
                        ],
                        'countries': ['eng'],
                    },
                ],
            },
            False,
            True,
        ),
        (
            {
                'take': [
                    {
                        'permissions': [
                            rights.CHATTERBOX_CLIENT_INTERNATIONAL_LINE,
                        ],
                        'countries': ['rus'],
                    },
                ],
            },
            False,
            False,
        ),
        (
            {
                'search': [
                    {
                        'permissions': [
                            rights.CHATTERBOX_CLIENT_INTERNATIONAL_LINE_SEARCH,
                        ],
                        'countries': ['rus'],
                    },
                ],
            },
            False,
            False,
        ),
    ),
)
async def test_available_lines_with_country_permissions(
        cbox: conftest.CboxWrap,
        patch_auth,
        line_permissions: dict,
        is_take_permitted: bool,
        is_search_permitted: bool,
):
    patch_auth(
        superuser=False, groups=['readonly', 'english', 'english_search'],
    )
    cbox.app.config.CHATTERBOX_LINES_PERMISSIONS['english'] = line_permissions

    await cbox.post('/v1/lines/available/', data={})

    assert cbox.status == 200
    assert cbox.body_data == {
        'available_lines': [
            {
                'line': 'english',
                'line_name': 'English',
                'types': ['client'],
                'mode': 'offline',
                'can_take': is_take_permitted,
                'can_search': is_search_permitted,
                'logbroker_telephony': False,
            },
        ],
    }


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': 'Первая линия', 'sort_order': 1, 'priority': 3},
        'zen': {
            'name': 'Линия Дзена',
            'sort_order': 1,
            'priority': 3,
            'profile': 'support-zen',
        },
    },
    CHATTERBOX_LINES_PERMISSIONS={},
)
@pytest.mark.parametrize(
    ('auth_groups', 'is_taxi_search_permitted', 'is_zen_search_permitted'),
    (
        # profile independent admin
        (('chatterbox_search_and_view_full', 'readonly'), True, True),
        # taxi readonly admin
        (('chatterbox_search_and_view_full_profile', 'readonly'), True, False),
        # zen readonly admin
        (
            (
                'chatterbox_search_and_view_full_profile',
                'chatterbox_support_zen',
                'readonly',
            ),
            False,
            True,
        ),
    ),
)
async def test_available_lines_search_permissions(
        cbox: conftest.CboxWrap,
        patch_auth,
        auth_groups,
        is_taxi_search_permitted,
        is_zen_search_permitted,
):
    patch_auth(superuser=False, groups=auth_groups)
    await cbox.post('/v1/lines/available/', data={})

    assert cbox.status == 200
    assert cbox.body_data == {
        'available_lines': [
            {
                'line': 'first',
                'line_name': 'Первая линия',
                'types': ['client'],
                'mode': 'offline',
                'can_take': False,
                'can_search': is_taxi_search_permitted,
                'logbroker_telephony': False,
            },
            {
                'line': 'zen',
                'line_name': 'Линия Дзена',
                'types': ['client'],
                'mode': 'offline',
                'can_take': False,
                'can_search': is_zen_search_permitted,
                'logbroker_telephony': False,
            },
        ],
    }


@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': '1 · DM РФ', 'priority': 3, 'sort_order': 1},
    },
    CHATTERBOX_LINES_PERMISSIONS={},
)
async def test_take_without_permissions_in_config(
        cbox: conftest.CboxWrap, patch_auth, patch_support_chat_get_history,
):
    patch_support_chat_get_history()
    patch_auth(superuser=False, groups=['basic'], login='user_without_task')
    cbox.set_user('user_without_task')

    await cbox.post('/v1/tasks/take/', data={'lines': ['first']})

    assert cbox.status == 404


@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': '1 · DM РФ', 'priority': 3, 'sort_order': 1},
    },
    CHATTERBOX_LINES_PERMISSIONS={},
)
async def test_take_with_full_take_permissions(
        cbox: conftest.CboxWrap, patch_auth, patch_support_chat_get_history,
):
    patch_support_chat_get_history()
    patch_auth(
        superuser=False,
        groups=['basic', 'chatterbox_take_full'],
        login='user_without_task',
    )
    cbox.set_user('user_without_task')

    await cbox.post('/v1/tasks/take/', data={'lines': ['first']})

    assert cbox.status == 200
    assert cbox.body_data['id'] == 'new_first_line_id'


@pytest.mark.config(CHATTERBOX_LINES_PERMISSIONS={})
async def test_take_without_permissions_assigned_task(
        cbox: conftest.CboxWrap, patch_auth, patch_support_chat_get_history,
):
    patch_support_chat_get_history()
    patch_auth(superuser=False, groups=['basic'], login='user_with_task')
    cbox.set_user('user_with_task')

    await cbox.post('/v1/tasks/take/', data={'lines': ['first', 'second']})

    assert cbox.status == 200
    assert cbox.body_data['id'] == 'urgent_task_id'


@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': '1 · DM РФ', 'priority': 3, 'sort_order': 1},
        'second': {'name': '2 · DM РФ', 'priority': 1, 'sort_order': 1},
        'english': {'name': '1 · English', 'priority': 3, 'sort_order': 1},
        'israel': {'name': '1 · Israel', 'priority': 3, 'sort_order': 1},
    },
    CHATTERBOX_LINES_PERMISSIONS={},
)
@pytest.mark.parametrize(
    (
        'chatterbox_lines_permissions',
        'groups',
        'user_login',
        'expected_chat_id',
    ),
    [
        # line with unrestricted permissions
        (
            {
                'first': {
                    'take': [
                        {'permissions': [rights.CHATTERBOX_CLIENT_FIRST_LINE]},
                    ],
                },
                'second': {
                    'take': [
                        {
                            'permissions': [
                                rights.CHATTERBOX_CLIENT_SECOND_LINE,
                            ],
                        },
                    ],
                },
            },
            ['basic', 'client_first'],
            'user_without_task',
            'new_first_line_id',
        ),
        # lines with country permissions
        (
            {
                'english': {
                    'take': [
                        {
                            'permissions': [
                                rights.CHATTERBOX_CLIENT_INTERNATIONAL_LINE,
                            ],
                            'countries': ['rus', 'eng'],
                        },
                    ],
                },
                'israel': {
                    'take': [
                        {
                            'permissions': [
                                rights.CHATTERBOX_CLIENT_INTERNATIONAL_LINE,
                            ],
                            'countries': ['rus', 'isr'],
                        },
                    ],
                },
            },
            ['basic', 'english'],
            'user_without_task',
            'new_english_line_id',
        ),
        (
            {
                'english': {
                    'take': [
                        {
                            'permissions': [
                                rights.CHATTERBOX_CLIENT_INTERNATIONAL_LINE,
                            ],
                            'countries': ['rus', 'eng'],
                        },
                    ],
                },
                'israel': {
                    'take': [
                        {
                            'permissions': [
                                rights.CHATTERBOX_CLIENT_INTERNATIONAL_LINE,
                            ],
                            'countries': ['rus', 'isr'],
                        },
                    ],
                },
            },
            ['basic', 'israel'],
            'user_without_task',
            'new_israel_line_id',
        ),
    ],
)
async def test_take(
        cbox: conftest.CboxWrap,
        patch_auth,
        patch_support_chat_get_history,
        chatterbox_lines_permissions: dict,
        groups: List[str],
        user_login: str,
        expected_chat_id: str,
):
    patch_support_chat_get_history()
    patch_auth(superuser=False, groups=groups, login=user_login)
    cbox.app.config.CHATTERBOX_LINES_PERMISSIONS = chatterbox_lines_permissions
    cbox.set_user(user_login)

    await cbox.post(
        '/v1/tasks/take/',
        data={'lines': ['first', 'second', 'english', 'israel']},
    )

    assert cbox.status == 200
    assert cbox.body_data['id'] == expected_chat_id
