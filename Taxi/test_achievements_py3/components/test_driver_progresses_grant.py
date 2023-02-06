import typing

import pytest

from achievements_py3.components.controllers import admin as admin_module
from achievements_py3.generated.web import web_context as context_module


def find_progresses(udids, pgsql):
    joined_udids = '{' + ','.join(set(udids)) + '}'
    cursor = pgsql['achievements_pg'].cursor()
    cursor.execute(
        f"""
        SELECT
            udid, reward_code, progress
        FROM achievements_pg.progresses
        WHERE
            udid=ANY('{joined_udids}')
        ;
        """,
    )
    result: typing.Dict[str, typing.Set[typing.Tuple[str, int]]] = {}
    for row in cursor.fetchall():
        udid = row[0]
        reward_code = row[1]
        progress = row[2]
        reward_progress = result.setdefault(udid, set())
        reward_progress.add((reward_code, progress))
    return result


@pytest.mark.parametrize(
    ['udids', 'progresses', 'reward', 'expect_error_type'],
    [
        pytest.param(
            ['udid1'],
            [1],
            'foobar',
            admin_module.InvalidRewardCode,
            id='no foobar in database',
        ),
        pytest.param(
            ['udid1'],
            [1],
            'star',
            admin_module.InvalidRewardCode,
            id='star is not leveled',
        ),
        pytest.param(
            [],
            [],
            'star',
            admin_module.AdminControllerError,
            id='empty lists',
        ),
        pytest.param(
            ['udid1'],
            None,
            'star',
            admin_module.AdminControllerError,
            id='one list is None',
        ),
        pytest.param(
            ['udid1'],
            [],
            'star',
            admin_module.AdminControllerError,
            id='lists lengths missmatch',
        ),
        pytest.param(
            ['udid1'],
            [1],
            'bad_levels',
            admin_module.InvalidRewardCode,
            id='leveled but no levels',
        ),
        pytest.param(
            ['udid1'],
            [1],
            'driver_years',
            admin_module.InvalidRewardCode,
            id='not has_progress',
        ),
        pytest.param(
            ['udid1', 'udid2', 'udid3', 'udid3'],
            [1, 2, 3, 4],
            '5_stars',
            admin_module.AdminControllerError,
            id='not unique udids',
        ),
    ],
)
async def test_driver_progresses_grant_fail(
        web_context: context_module.Context,
        udids,
        progresses,
        reward,
        expect_error_type,
):
    admin_controller: admin_module.Component = web_context.admin_controller
    with pytest.raises(expect_error_type):
        await admin_controller.grant_driver_progresses_batch(
            reward, udids, progresses,
        )


@pytest.mark.parametrize(
    ['udids', 'progresses', 'reward', 'expected_progresses'],
    [
        pytest.param(
            ['udid1'],
            [0],
            '5_stars',
            {'udid1': {('5_stars', 0), ('express', 0), ('star', 1)}},
            id='simple work',
        ),
        pytest.param(
            ['udid1', 'udid2', 'udid3'],
            [1, 2, 10],
            '5_stars',
            {
                'udid1': {('5_stars', 1), ('express', 0), ('star', 1)},
                'udid2': {('5_stars', 2), ('driver_years', 1)},
                'udid3': {('5_stars', 10)},
            },
            id='insert and upsert work',
        ),
    ],
)
async def test_driver_progresses_grant_work(
        web_context: context_module.Context,
        pgsql,
        udids,
        progresses,
        reward,
        expected_progresses,
):
    admin_controller: admin_module.Component = web_context.admin_controller
    await admin_controller.grant_driver_progresses_batch(
        reward, udids, progresses,
    )
    progresses = find_progresses(udids, pgsql)
    assert progresses == expected_progresses
