import pytest

from achievements_py3.generated.web import web_context as context_module


def count_rewards(code, pgsql):
    cursor = pgsql['achievements_pg'].cursor()
    cursor.execute(
        """
        SELECT
            COUNT(*)
        FROM achievements_pg.rewards
        WHERE
            code=%(code)s
        ;
        """,
        {'code': code},
    )
    return cursor.fetchall()[0][0]


@pytest.mark.parametrize(
    'code, exists_before, delete_success',
    [
        ('awesome_reward', False, True),
        ('top_delivery', True, True),
        ('star', True, False),
    ],
)
async def test_rewards_delete(
        web_context: context_module.Context,
        pgsql,
        code,
        exists_before,
        delete_success,
):
    found_rewards = count_rewards(code, pgsql)
    assert found_rewards == (1 if exists_before else 0)

    admin_controller = web_context.admin_controller
    success = await admin_controller.delete_reward(code)
    assert success is delete_success

    found_rewards = count_rewards(code, pgsql)
    assert found_rewards == (0 if delete_success else 1)
