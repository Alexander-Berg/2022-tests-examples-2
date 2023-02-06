import pytest

INIT_PARK = 'ParkOne'
MAPPED_PARK = 'ParkOneMapped'


@pytest.mark.config(
    FLEET_SYNCHRONIZER_DISP_USERS_SYNC_SETTINGS={
        'uberdriver': {'enabled': True, 'sleep_ms': 10},
        'general_settings': {
            'enabled': True,
            'period': 60 * 60 * 24,
            'distlock_margin': 100,
            'bulk_size': 50,
            'distlock_settings': {
                'acquire_interval_minutes': 12 * 60,
                'prolong_interval_minutes': 2 * 60,
                'lock_ttl_minutes': 2 * 60,
                'forced_stop_margin_milliseconds': 500,
                'worker_func_restart_delay_seconds': 1,
            },
        },
    },
)
@pytest.mark.parametrize('is_task', [True, False])
@pytest.mark.parametrize(
    'is_mapped_active,has_excessive_user,has_excessive_group',
    [(False, False, False), (True, False, False), (True, True, True)],
)
async def test_disp_users_sync(
        taxi_fleet_synchronizer,
        mongodb,
        dispatcher_access_control,
        is_mapped_active,
        is_task,
        has_excessive_user,
        has_excessive_group,
):
    dispatcher_access_control.set_init_park(INIT_PARK)

    if has_excessive_user:
        user_data = dict(
            dispatcher_access_control.get_user_data(
                INIT_PARK, dispatcher_access_control.DISPATCHER_USER_ID,
            ),
        )
        user_data['id'] = 'some_user_id'
        user_data['park_id'] = MAPPED_PARK

        dispatcher_access_control.set_user(
            MAPPED_PARK, 'some_user_id', user_data,
        )

    if has_excessive_group:
        dispatcher_access_control.create_group(
            MAPPED_PARK, 'some_group_id', 'some_group_name',
        )

    mongodb.dbparks.update_one(
        {'_id': MAPPED_PARK},
        {
            '$set': {'is_active': is_mapped_active},
            '$currentDate': {
                'modified_date': {'$type': 'date'},
                'updated_ts': {'$type': 'timestamp'},
            },
        },
    )

    await taxi_fleet_synchronizer.invalidate_caches()

    if is_task:
        await taxi_fleet_synchronizer.run_periodic_task('disp_users')
    else:
        await taxi_fleet_synchronizer.post(
            '/fleet-synchronizer/v1/sync/park/property',
            params={
                'park_id': 'ParkOne',
                'app_family': 'uberdriver',
                'type': 'disp_users',
            },
            headers={'Content-Type': 'application/json'},
        )

    dac_fixture = dispatcher_access_control
    if is_mapped_active:
        assert MAPPED_PARK in dac_fixture.grants
        assert MAPPED_PARK in dac_fixture.groups
        assert MAPPED_PARK in dac_fixture.users
    else:
        assert MAPPED_PARK not in dac_fixture.grants
        assert MAPPED_PARK not in dac_fixture.groups
        assert MAPPED_PARK not in dac_fixture.users

    assert 'write_grant_1' in dac_fixture.get_admin_grants(INIT_PARK)
    assert 'company_write' in dac_fixture.get_admin_grants(INIT_PARK)

    if is_mapped_active:
        assert 'write_grant_1' in dac_fixture.get_admin_grants(MAPPED_PARK)
        assert 'read_grant_3' in dac_fixture.get_dispatcher_grants(MAPPED_PARK)
        assert 'read_grant_3' not in dac_fixture.get_admin_grants(MAPPED_PARK)
        assert 'company_write' not in dac_fixture.get_admin_grants(MAPPED_PARK)
        assert 'driver_write_common' in dac_fixture.get_admin_grants(
            MAPPED_PARK,
        )

    if is_mapped_active:
        assert dac_fixture.mock_groups_list.times_called == 2
        assert dac_fixture.mock_sync_parks_groups.times_called == 2 + int(
            has_excessive_group,
        )
        assert dac_fixture.mock_sync_parks_groups_grants.times_called == 2

        assert dac_fixture.mock_parks_groups_users_list.times_called == 2
        assert dac_fixture.mock_sync_parks_users.times_called == 2 + int(
            has_excessive_user,
        )
        assert dac_fixture.mock_parks_grants_list.times_called == 1
        assert dac_fixture.mock_parks_grants_groups_list.times_called == 1
    else:
        assert dac_fixture.mock_groups_list.times_called == 0
        assert dac_fixture.mock_sync_parks_groups.times_called == 0
        assert dac_fixture.mock_sync_parks_groups_grants.times_called == 0
        assert dac_fixture.mock_parks_groups_users_list.times_called == 0
        assert dac_fixture.mock_sync_parks_users.times_called == 0
