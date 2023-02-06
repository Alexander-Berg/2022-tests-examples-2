import pytest

from achievements_py3.components.controllers import admin as admin_module
from achievements_py3.generated.web import web_context as context_module


def find_rewards(code, pgsql):
    cursor = pgsql['achievements_pg'].cursor()
    cursor.execute(
        """
        SELECT
            code, has_locked_state, is_leveled, levels, category, author
        FROM achievements_pg.rewards
        WHERE
            code=%(code)s
        ;
        """,
        {'code': code},
    )
    return cursor.fetchall()


@pytest.mark.parametrize(
    [
        'code',
        'has_locked_state',
        'is_leveled',
        'has_progress',
        'levels',
        'category',
        'author',
        'exists_before',
    ],
    [
        ('awesome_reward', True, False, False, [], None, None, False),
        (
            'awesome_reward',
            False,
            False,
            False,
            [],
            'heroic',
            'felixpalta',
            False,
        ),
        ('star', True, False, False, [], None, None, True),
        ('leveled_reward', True, True, False, [1, 2, 3], None, None, False),
        ('progressive_reward', True, True, True, [1, 2, 3], None, None, False),
    ],
)
async def test_rewards_create_or_update(
        web_context: context_module.Context,
        pgsql,
        code,
        has_locked_state,
        is_leveled,
        has_progress,
        levels,
        category,
        author,
        exists_before,
):

    found_rewards = find_rewards(code, pgsql)
    if exists_before:
        assert len(found_rewards) == 1
        reward_before = found_rewards[0]
        assert reward_before[0] == code
    else:
        assert found_rewards == []

    admin_controller = web_context.admin_controller
    return_code = await admin_controller.create_or_update_reward(
        code,
        has_locked_state,
        is_leveled,
        has_progress,
        levels,
        category,
        author,
    )
    if is_leveled and not levels:
        assert return_code is None
    else:
        assert code == return_code

        found_rewards = find_rewards(code, pgsql)
        assert len(found_rewards) == 1
        reward_after = found_rewards[0]
        assert reward_after == (
            code,
            has_locked_state,
            is_leveled,
            levels,
            category,
            author,
        )


@pytest.mark.parametrize(
    'code, is_leveled, has_progress, levels',
    [
        ('some_reward', False, False, [1, 2, 3]),
        ('some_reward', True, False, []),
        ('some_reward', True, False, [3, 2, 1]),
        ('some_reward', False, True, []),
    ],
)
async def test_rewards_create_or_update_errors(
        web_context: context_module.Context,
        pgsql,
        code,
        is_leveled,
        has_progress,
        levels,
):
    admin_controller = web_context.admin_controller

    with pytest.raises(admin_module.InvalidRewardCode):
        await admin_controller.create_or_update_reward(
            reward_code=code,
            has_locked_state=False,
            is_leveled=is_leveled,
            has_progress=has_progress,
            levels=levels,
            category=None,
            author=None,
        )
