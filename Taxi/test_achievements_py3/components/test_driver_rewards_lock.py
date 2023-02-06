import pytest

from achievements_py3.components.controllers import admin as admin_module
from achievements_py3.generated.web import web_context as context_module

# returns dict, where for each udid there is a list of locked reward codes
def find_locked_many(udids, pgsql):
    joined_udids = '{' + ','.join(udids) + '}'
    cursor = pgsql['achievements_pg'].cursor()
    cursor.execute(
        f"""
        SELECT
            udid, array_agg(reward_code)
        FROM achievements_pg.driver_rewards
        WHERE
            udid=ANY('{joined_udids}')
            AND level = 0
            AND unlocked_at IS NULL
        GROUP BY udid
        ;
        """,
    )
    return {row[0]: set(row[1]) for row in cursor.fetchall()}


@pytest.mark.parametrize(
    'udids, reward, expect_error_type, '
    'expect_updated_drivers, expect_all_locked_rewards',
    [
        ([], 'covid_hero', None, set(), {}),
        (['udid1'], 'express', None, set(), {'udid1': {'express'}}),
        (
            ['udid1'],
            'covid_hero',
            None,
            {'udid1'},
            {'udid1': {'covid_hero', 'express'}},
        ),
        (['udid1'], 'star', None, {'udid1'}, {'udid1': {'express', 'star'}}),
        (['udid1'], 'foobar', admin_module.InvalidRewardCode, None, None),
        (
            ['udid1', 'udid1'],
            'covid_hero',
            admin_module.AdminControllerError,
            None,
            None,
        ),
        (['udid1'], None, admin_module.InvalidRewardCode, None, None),
        (
            ['udid1', 'udid2', 'udid3'],
            'covid_hero',
            None,
            {'udid1', 'udid2', 'udid3'},
            {
                'udid1': {'express', 'covid_hero'},
                'udid2': {'covid_hero'},
                'udid3': {'covid_hero'},
            },
        ),
        pytest.param(
            ['udid1', 'udid2', 'udid3'],
            'express',
            None,
            {'udid2', 'udid3'},
            {
                'udid1': {'express'},  # unchanged
                'udid2': {'express'},
                'udid3': {'express'},
            },
            id='only udid2 and udid3 are updated, '
            'because udid1 already has these rewards',
        ),
    ],
)
async def test_driver_rewards_lock_many(
        web_context: context_module.Context,
        pgsql,
        udids,
        reward,
        expect_error_type,
        expect_updated_drivers,
        expect_all_locked_rewards,
):
    admin_controller: admin_module.Component = web_context.admin_controller
    if expect_error_type:
        with pytest.raises(expect_error_type):
            await admin_controller.lock_many_driver_rewards(udids, reward)
    else:
        updated_drivers = await admin_controller.lock_many_driver_rewards(
            udids, reward,
        )
        assert set(updated_drivers) == expect_updated_drivers

        locked_rewards = find_locked_many(udids, pgsql)
        assert locked_rewards == expect_all_locked_rewards
