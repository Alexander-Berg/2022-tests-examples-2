import pytest

from chatterbox.crontasks import check_forgotten_tasks


@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': '1', 'types': ['client']},
        'second': {
            'name': '2',
            'types': ['client'],
            'tags': ['Корпоративный_пользователь', 'Корп_пользователь'],
            'fields': {},
            'priority': 2,
            'sort_order': 1,
            'title_tanker': 'lines.corp',
        },
        'third': {
            'name': '3',
            'types': ['client'],
            'tags': [],
            'fields': {},
            'priority': 4,
            'sort_order': 1,
            'autoreply': True,
        },
    },
)
async def test_check_forgotten_tasks_success(cbox_context, loop):

    await check_forgotten_tasks.do_stuff(cbox_context, loop)


@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': '1', 'types': ['client']},
        'second': {
            'name': '2',
            'types': ['client'],
            'tags': ['Корпоративный_пользователь', 'Корп_пользователь'],
            'fields': {},
            'priority': 2,
            'sort_order': 1,
            'title_tanker': 'lines.corp',
        },
    },
)
async def test_check_forgotten_tasks_error(cbox_context, loop):

    with pytest.raises(check_forgotten_tasks.ForgottenTaskError) as exc:
        await check_forgotten_tasks.do_stuff(cbox_context, loop)

    assert str(exc.value) == (
        'Found 1 chatterbox task(s) in wrong line(s): '
        'task 5b2cae5cb5682a976914c2a3 in wrong line third'
    )
