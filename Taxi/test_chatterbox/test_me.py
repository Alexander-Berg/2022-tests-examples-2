from typing import List

import pytest

from test_chatterbox import plugins as conftest


@pytest.mark.now('2018-06-28T14:45:00+0300')
async def test_me(cbox: conftest.CboxWrap):
    cbox.set_user('some_user')
    await cbox.post('/me', data={})
    assert cbox.status == 200
    assert cbox.body_data == {
        'csrf_token': 'd8d54e26397ed5ab615d204d7ffba1b39815ae33:1530175500',
        'uid': '0',
        'login': 'superuser',
        'display_name': 'superuser',
        'default_avatar_id': '0/0-0',
        'incoming_calls_allowed': True,
    }


@pytest.mark.now('2018-06-28T14:45:00+0300')
@pytest.mark.parametrize(
    ('is_superuser', 'groups', 'is_permitted'),
    (
        (True, [], True),
        (False, ['incoming_calls_permitted'], True),
        (False, [], False),
    ),
)
async def test_me_incoming_calls_allowed(
        cbox: conftest.CboxWrap,
        patch_auth,
        is_superuser: bool,
        groups: List[str],
        is_permitted: bool,
):
    cbox.set_user('some_user')
    patch_auth(superuser=is_superuser, groups=groups)
    await cbox.post('/me', data={})
    assert cbox.status == 200
    assert cbox.body_data == {
        'csrf_token': 'd8d54e26397ed5ab615d204d7ffba1b39815ae33:1530175500',
        'uid': '0',
        'login': 'superuser',
        'display_name': 'superuser',
        'default_avatar_id': '0/0-0',
        'incoming_calls_allowed': is_permitted,
    }
