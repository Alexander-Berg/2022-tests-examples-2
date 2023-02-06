# pylint: disable = cell-var-from-loop
import pytest


@pytest.mark.parametrize(
    'driver_work_modes',
    [
        ['orders', 'driver-fix', 'orders'],
        ['driver-fix', 'orders', 'driver-fix'],
    ],
)
@pytest.mark.pgsql('reposition', files=['drivers.sql'])
async def test_driver_work_mode(
        taxi_reposition_api, driver_work_modes, testpoint, pgsql,
):
    await taxi_reposition_api.invalidate_caches(
        clean_update=False, cache_names=['driver-work-modes-cache'],
    )

    for driver_work_mode in driver_work_modes:

        @testpoint('driver_work_modes_cache_inserting_value')
        async def _inserted_driver_work_mode(data):
            if driver_work_mode == 'orders':
                assert data == {}
            else:
                assert data == {'5': driver_work_mode}

        driver_work_mode_str = (
            f'\'{driver_work_mode}\''
            if driver_work_mode != 'orders'
            else 'NULL'
        )

        cursor = pgsql['reposition'].cursor()
        cursor.execute(
            'INSERT INTO state.driver_work_modes(driver_id_id, work_mode) '
            f'VALUES (IdId(\'uuid\', \'dbid\'), {driver_work_mode_str}) '
            'ON CONFLICT (driver_id_id) DO UPDATE '
            'SET work_mode = excluded.work_mode;',
        )

        await taxi_reposition_api.invalidate_caches(
            clean_update=False, cache_names=['driver-work-modes-cache'],
        )
        assert _inserted_driver_work_mode.times_called == 1
