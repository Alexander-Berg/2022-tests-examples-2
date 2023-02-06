# pylint: disable=redefined-outer-name,unused-variable,global-statement
import pytest

from selfemployed.db import dbmain
from selfemployed.generated.cron import run_cron


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, from_park_id, from_driver_id, park_id, driver_id, step,
                created_at, modified_at)
        VALUES
            ('smz1', 'inn1', 'old_p1', 'old_d1', 'p1', 'd1', 'requisites',
                NOW(), NOW()),
            ('smz2', 'inn2', 'old_p2', 'old_d2', 'p2', 'd2', 'requisites',
                NOW(), NOW()),
            ('smz3', NULL, 'old_p3', 'old_d3', NULL, NULL, 'permission',
                NOW(), NOW()),
            ('smz4', 'inn4', 'old_p4', 'old_d4', 'p4', 'd4', 'requisites',
                NOW(), NOW())
        """,
        """
        INSERT INTO referrals
            (park_id, driver_id, promocode, reg_promocode)
        VALUES
            ('p2', 'd2', NULL, 'PROMO1'),
            ('p4', 'd4', 'PROMO4', NULL)
        """,
    ],
)
async def test_promocode_generator(se_cron_context, patch):
    await run_cron.main(
        ['selfemployed.crontasks.promocode_generator', '-t', '0'],
    )

    postgres = se_cron_context.pg

    assert await dbmain.get_driver_promocode(postgres, 'p1', 'd1')
    assert await dbmain.get_driver_promocode(postgres, 'p2', 'd2')
    assert not await dbmain.get_driver_promocode(postgres, 'p3', 'd3')
    assert await dbmain.get_driver_promocode(postgres, 'p4', 'd4') == 'PROMO4'
