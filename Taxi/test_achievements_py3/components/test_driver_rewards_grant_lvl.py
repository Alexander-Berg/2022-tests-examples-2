import typing

import pytest

from achievements_py3.components.controllers import admin as admin_module
from achievements_py3.generated.web import web_context as context_module


def find_unlocked_with_levels(udids, pgsql):
    joined_udids = '{' + ','.join(set(udids)) + '}'
    cursor = pgsql['achievements_pg'].cursor()
    cursor.execute(
        f"""
        SELECT
            udid, reward_code, level
        FROM achievements_pg.driver_rewards
        WHERE
            udid=ANY('{joined_udids}')
            AND unlocked_at IS NOT NULL
        ;
        """,
    )
    result: typing.Dict[str, typing.Dict[str, typing.Set[int]]] = {}
    for row in cursor.fetchall():
        udid = row[0]
        reward_code = row[1]
        level = row[2]
        rewards = result.setdefault(udid, {})
        reward_levels = rewards.setdefault(reward_code, set())
        reward_levels.add(level)
    return result


@pytest.mark.parametrize(
    ['udids', 'levels', 'reward', 'expect_error_type'],
    [
        pytest.param(
            [],
            [],
            'foobar',
            admin_module.AdminControllerError,
            id='lengths of lists are zero',
        ),
        pytest.param(
            ['udid1'],
            None,
            'foobar',
            admin_module.AdminControllerError,
            id='one list in None',
        ),
        pytest.param(
            ['udid1'],
            [],
            'foobar',
            admin_module.AdminControllerError,
            id='lengths of lists differ',
        ),
        pytest.param(
            ['udid1'],
            [1],
            'star',
            admin_module.InvalidRewardCode,
            id='star not is_leveled',
        ),
        pytest.param(
            ['udid1'],
            [1],
            'foobar',
            admin_module.InvalidRewardCode,
            id='foobar is not in database',
        ),
        pytest.param(
            ['udid1'],
            [1],
            'bad_levels',
            admin_module.InvalidRewardCode,
            id='no levels but is_leveled',
        ),
        pytest.param(
            ['udid1'],
            [300],
            'driver_years',
            admin_module.InvalidRewardCode,
            id='no 300 level in driver_years reward',
        ),
        pytest.param(
            ['udid1', 'udid2'],
            [1, 300],
            'driver_years',
            admin_module.InvalidRewardCode,
            id='no 300 level in driver_years reward mix',
        ),
    ],
)
async def test_driver_rewards_grant_lvl_fail(
        web_context: context_module.Context,
        udids,
        levels,
        reward,
        expect_error_type,
):
    admin_controller: admin_module.Component = web_context.admin_controller
    with pytest.raises(expect_error_type):
        await admin_controller.grant_many_lvl_driver_rewards(
            reward, udids, levels,
        )


@pytest.mark.parametrize(
    [
        'udids',
        'levels',
        'reward',
        'expect_updated_drivers',
        'expect_all_unlocked_rewards',
    ],
    [
        pytest.param(
            ['udid2'],
            [2],
            'driver_years',
            {'udid2'},
            {'udid2': {'driver_years': {1, 2}}},
            id='1 year was and 2 years is inserted',
        ),
        pytest.param(
            ['udid1'],
            [1],
            'driver_years',
            {'udid1'},
            {'udid1': {'star': {1}, 'driver_years': {1}}},
            id='one udid - one level',
        ),
        pytest.param(
            ['udid1'] * 3,
            [1, 2, 3],
            'driver_years',
            {'udid1'},
            {'udid1': {'star': {1}, 'driver_years': {1, 2, 3}}},
            id='one udid - many levels',
        ),
        pytest.param(
            ['udid1', 'udid2', 'udid3', 'udid3'],
            [1, 1, 1, 3],
            'driver_years',
            {'udid1', 'udid3'},  # udid2 already has that level
            {
                'udid1': {'star': {1}, 'driver_years': {1}},
                'udid2': {'driver_years': {1}},
                'udid3': {'driver_years': {1, 3}},
            },
            id="""many udids - only one with many levels.
                inserted two udids, so only 2 push""",
        ),
        pytest.param(
            ['udid1', 'udid1', 'udid2', 'udid2', 'udid3', 'udid3'],
            [1, 2, 1, 2, 1, 2],
            'driver_years',
            {'udid1', 'udid2', 'udid3'},
            {
                'udid1': {'star': {1}, 'driver_years': {1, 2}},
                'udid2': {'driver_years': {1, 2}},
                'udid3': {'driver_years': {1, 2}},
            },
            id='many udids - all with many levels',
        ),
        pytest.param(
            ['udid1'],
            [100],
            '5_stars',
            {'udid1'},
            {'udid1': {'star': {1}, '5_stars': {100}}},
            id='5_stars work test',
        ),
    ],
)
async def test_driver_rewards_grant_lvl_work(
        web_context: context_module.Context,
        pgsql,
        udids,
        levels,
        reward,
        expect_updated_drivers,
        expect_all_unlocked_rewards,
):
    admin_controller: admin_module.Component = web_context.admin_controller
    updated_drivers = await admin_controller.grant_many_lvl_driver_rewards(
        reward, udids, levels,
    )
    assert set(updated_drivers) == expect_updated_drivers

    unlocked_rewards = find_unlocked_with_levels(udids, pgsql)
    assert unlocked_rewards == expect_all_unlocked_rewards
