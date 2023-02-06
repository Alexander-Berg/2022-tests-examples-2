import pytest

from achievements_py3.generated.web import web_context as context_module


def count_driver_rewards(udids, pgsql):
    joined_udids = '{' + ','.join(udids) + '}'
    cursor = pgsql['achievements_pg'].cursor()
    cursor.execute(
        f"""
        SELECT
            COUNT(*)
        FROM achievements_pg.driver_rewards
        WHERE
            udid=ANY('{joined_udids}')
        ;
        """,
    )
    return cursor.fetchall()[0][0]


def count_driver_rewards_by_code(reward_codes, pgsql):
    cursor = pgsql['achievements_pg'].cursor()
    joined_codes = '{' + ','.join(reward_codes) + '}'
    cursor.execute(
        f"""
        SELECT
            udid
        FROM achievements_pg.driver_rewards
        WHERE
            reward_code=ANY('{joined_codes}')
        GROUP BY udid
        ;
        """,
    )
    rows = cursor.fetchall()
    return len(rows) if rows else 0


@pytest.mark.parametrize(
    'udids, expect_dropped',
    [
        (['udid1'], 1),
        (['udid2'], 1),
        (['udid1', 'udid2'], 2),
        (['bad_udid'], 0),
    ],
)
async def test_driver_rewards_drop_from_many(
        web_context: context_module.Context, pgsql, udids, expect_dropped,
):
    admin_controller = web_context.admin_controller
    dropped = await admin_controller.drop_all_rewards_from_many(udids)
    assert dropped == expect_dropped

    assert count_driver_rewards(udids, pgsql) == 0


@pytest.mark.parametrize(
    'reward_codes, expect_count',
    [
        (['star'], 1),
        (['top_delivery'], 0),
        (['not_exists'], 0),
        (['express', 'star'], 1),
        (['express', 'star', 'covid_hero'], 2),
        (['express', 'star', 'covid_hero', '1000_5star_rides'], 2),
        (
            [
                'express',
                'star',
                'covid_hero',
                '1000_5star_rides',
                'top_delivery',
            ],
            2,
        ),
    ],
)
async def test_driver_rewards_drop_from_all(
        web_context: context_module.Context, pgsql, reward_codes, expect_count,
):
    assert count_driver_rewards_by_code(reward_codes, pgsql) == expect_count

    admin_controller = web_context.admin_controller
    count = await admin_controller.drop_rewards_from_all_drivers(reward_codes)
    assert count == expect_count

    assert count_driver_rewards_by_code(reward_codes, pgsql) == 0
