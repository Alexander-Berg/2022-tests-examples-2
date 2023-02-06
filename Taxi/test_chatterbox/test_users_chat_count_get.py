import typing as tp

import pytest

from testsuite.databases.pgsql import control

from test_chatterbox import plugins as conftest


@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'mode': 'online'},
        'second': {'mode': 'offline'},
        'corp': {'mode': 'online'},
    },
    CHATTERBOX_USE_COMPENDIUM_MAX_CHATS=True,
)
@pytest.mark.parametrize(
    ('lines', 'expected_status', 'expected_result'),
    (
        (
            [],
            200,
            {
                'users': [
                    {
                        'login': 'user_1',
                        'lines': ['first', 'second'],
                        'chat_count': 2,
                        'is_chat_max_count_set': True,
                        'chat_max_count': 10,
                    },
                    {
                        'login': 'user_3',
                        'lines': ['first', 'corp'],
                        'chat_count': 1,
                        'is_chat_max_count_set': True,
                        'chat_max_count': 2,
                    },
                    {
                        'login': 'user_4',
                        'lines': ['corp'],
                        'chat_count': 0,
                        'is_chat_max_count_set': False,
                    },
                ],
            },
        ),
        (
            ['first'],
            200,
            {
                'users': [
                    {
                        'login': 'user_1',
                        'lines': ['first', 'second'],
                        'chat_count': 2,
                        'is_chat_max_count_set': True,
                        'chat_max_count': 10,
                    },
                    {
                        'login': 'user_3',
                        'lines': ['first', 'corp'],
                        'chat_count': 1,
                        'is_chat_max_count_set': True,
                        'chat_max_count': 2,
                    },
                ],
            },
        ),
        (
            ['first', 'corp'],
            200,
            {
                'users': [
                    {
                        'login': 'user_1',
                        'lines': ['first', 'second'],
                        'chat_count': 2,
                        'is_chat_max_count_set': True,
                        'chat_max_count': 10,
                    },
                    {
                        'login': 'user_3',
                        'lines': ['first', 'corp'],
                        'chat_count': 1,
                        'is_chat_max_count_set': True,
                        'chat_max_count': 2,
                    },
                    {
                        'login': 'user_4',
                        'lines': ['corp'],
                        'chat_count': 0,
                        'is_chat_max_count_set': False,
                    },
                ],
            },
        ),
        (
            ['second'],
            400,
            {
                'code': 'bad_request',
                'message': 'Next lines are not online: second',
                'status': 'error',
            },
        ),
    ),
)
async def test_get_users_chat_count(
        cbox: conftest.CboxWrap,
        pgsql: tp.Dict[str, control.PgDatabaseWrapper],
        lines: tp.List[str],
        expected_status: int,
        expected_result: tp.Dict,
):
    params = [('lines', line) for line in lines]

    await cbox.query('/v1/users/chat_count', params=params)
    assert cbox.status == expected_status
    assert cbox.body_data == expected_result


@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'mode': 'online'},
        'second': {'mode': 'offline'},
        'corp': {'mode': 'online'},
    },
    CHATTERBOX_USE_COMPENDIUM_MAX_CHATS=False,
)
@pytest.mark.parametrize(
    ('lines', 'expected_result'),
    (
        (
            [],
            {
                'users': [
                    {
                        'login': 'user_1',
                        'lines': ['first', 'second'],
                        'chat_count': 2,
                        'is_chat_max_count_set': False,
                    },
                    {
                        'login': 'user_3',
                        'lines': ['first', 'corp'],
                        'chat_count': 1,
                        'is_chat_max_count_set': False,
                    },
                    {
                        'login': 'user_4',
                        'lines': ['corp'],
                        'chat_count': 0,
                        'is_chat_max_count_set': False,
                    },
                ],
            },
        ),
    ),
)
async def test_get_users_chat_count_without_using_compendium(
        cbox: conftest.CboxWrap,
        pgsql: tp.Dict[str, control.PgDatabaseWrapper],
        lines: tp.List[str],
        expected_result: tp.Dict,
):
    params = [('lines', line) for line in lines]

    await cbox.query('/v1/users/chat_count', params=params)
    assert cbox.status == 200
    assert cbox.body_data == expected_result
