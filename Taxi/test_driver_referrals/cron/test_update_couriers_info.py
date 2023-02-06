# pylint: disable=unused-variable
import typing

import pytest

from driver_referrals.generated.cron import run_cron
from test_driver_referrals import conftest


COURIER_PARK_ID = 'p11'
COURIER_DRIVER_ID = 'd11'
COURIER_ORDERS_PROVIDER = 'eda'
REFERRER_PARK_ID = 'p1'
REFERRER_DRIVER_ID = 'd1'


async def get_profile(
        context, park_id: str, driver_id: str,
) -> typing.Optional[dict]:
    async with context.pg.master_pool.acquire() as connection:
        row = await connection.fetchrow(
            'SELECT * FROM referral_profiles'
            ' WHERE park_id = $1 AND driver_id = $2',
            park_id,
            driver_id,
        )
    return dict(row) if row else None


async def test_update_couriers_info_void(
        cron_context, mock_driver_profiles_couriers_updates,
):
    mock_driver_profiles_couriers_updates([])
    async with conftest.TablesDiffCounts(cron_context):
        await run_cron.main(
            ['driver_referrals.jobs.update_couriers_info', '-t', '0', '-d'],
        )


@pytest.mark.pgsql(
    'driver_referrals', files=['pg_driver_referrals_new_couriers.sql'],
)
@pytest.mark.config(
    DRIVER_REFERRALS_BLOCK_DRIVERS_AFTER_SAVING=[COURIER_ORDERS_PROVIDER],
)
async def test_update_new_couriers_info(
        cron_context,
        mock_driver_profiles_couriers_updates,
        mock_driver_profiles_couriers_profiles,
):
    mock_driver_profiles_couriers_updates([])
    mock_driver_profiles_couriers_profiles(
        {
            2: {
                'park_id': COURIER_PARK_ID,
                'driver_id': COURIER_DRIVER_ID,
                'orders_provider': COURIER_ORDERS_PROVIDER,
            },
        },
    )
    async with conftest.TablesDiffCounts(
            cron_context, {'referral_profiles': 1, 'notifications': 1},
    ):
        await run_cron.main(
            ['driver_referrals.jobs.update_couriers_info', '-t', '0', '-d'],
        )
    assert await get_profile(cron_context, 'p11', 'd11')


@pytest.mark.pgsql(
    'driver_referrals', files=['pg_driver_referrals_new_couriers.sql'],
)
@pytest.mark.config(
    DRIVER_REFERRALS_BLOCK_DRIVERS_AFTER_SAVING=[COURIER_ORDERS_PROVIDER],
)
async def test_not_new_courier_blocked(
        cron_context,
        mock_driver_profiles_couriers_updates,
        mock_driver_profiles_couriers_profiles,
        patch,
):
    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'SAME_LICENSE'

    mock_driver_profiles_couriers_updates([])
    mock_driver_profiles_couriers_profiles(
        {
            2: {
                'park_id': COURIER_PARK_ID,
                'driver_id': COURIER_DRIVER_ID,
                'orders_provider': COURIER_ORDERS_PROVIDER,
            },
        },
    )
    async with conftest.TablesDiffCounts(
            cron_context, {'referral_profiles': 1, 'notifications': 1},
    ):
        await run_cron.main(
            ['driver_referrals.jobs.update_couriers_info', '-t', '0', '-d'],
        )
    profile = await get_profile(cron_context, 'p11', 'd11')
    assert profile['status'] == 'blocked'


@pytest.mark.pgsql(
    'driver_referrals', files=['pg_driver_referrals_duplicate_couriers.sql'],
)
async def test_update_duplicate_couriers_info(
        cron_context,
        mock_driver_profiles_couriers_updates,
        mock_driver_profiles_couriers_profiles,
):
    mock_driver_profiles_couriers_updates([])
    mock_driver_profiles_couriers_profiles(
        {
            2: {
                'park_id': COURIER_PARK_ID,
                'driver_id': COURIER_DRIVER_ID,
                'orders_provider': COURIER_ORDERS_PROVIDER,
            },
        },
    )
    async with conftest.TablesDiffCounts(
            cron_context, {'referral_profiles': 1, 'duplicates_history': 1},
    ):
        await run_cron.main(
            ['driver_referrals.jobs.update_couriers_info', '-t', '0', '-d'],
        )
    old_profile = await get_profile(cron_context, 'p2', 'd2')
    assert old_profile['status'] == 'duplicate'

    new_profile = await get_profile(cron_context, 'p11', 'd11')
    assert new_profile
    assert new_profile['status'] == 'completed'


@pytest.mark.pgsql(
    'driver_referrals', files=['pg_driver_referrals_duplicate_couriers.sql'],
)
@pytest.mark.config(
    DRIVER_REFERRALS_BLOCK_DRIVERS_AFTER_SAVING=[COURIER_ORDERS_PROVIDER],
)
async def test_update_duplicate_couriers_info_blocked(
        cron_context,
        mock_driver_profiles_couriers_updates,
        mock_driver_profiles_couriers_profiles,
        patch,
):
    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'SAME_LICENSE'

    mock_driver_profiles_couriers_updates([])
    mock_driver_profiles_couriers_profiles(
        {
            2: {
                'park_id': COURIER_PARK_ID,
                'driver_id': COURIER_DRIVER_ID,
                'orders_provider': COURIER_ORDERS_PROVIDER,
            },
        },
    )
    async with conftest.TablesDiffCounts(
            cron_context, {'referral_profiles': 1, 'duplicates_history': 1},
    ):
        await run_cron.main(
            ['driver_referrals.jobs.update_couriers_info', '-t', '0', '-d'],
        )
    old_profile = await get_profile(cron_context, 'p2', 'd2')
    assert old_profile['status'] == 'duplicate'

    new_profile = await get_profile(cron_context, 'p11', 'd11')
    assert new_profile
    assert new_profile['status'] == 'blocked'
