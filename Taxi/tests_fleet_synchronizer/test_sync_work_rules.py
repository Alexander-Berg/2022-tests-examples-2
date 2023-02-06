import pytest

INIT_PARK = 'ParkOne'
MAPPED_PARK = 'ParkOneMapped'


@pytest.mark.config(
    FLEET_SYNCHRONIZER_WORK_RULES_SYNC_SETTINGS={
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
async def test_work_rules_sync(
        taxi_fleet_synchronizer, mockserver, is_task, driver_work_rules,
):
    driver_work_rules.set_rules(INIT_PARK, [1, 2, 3])
    driver_work_rules.set_rules(MAPPED_PARK, [3])

    if is_task:
        await taxi_fleet_synchronizer.run_periodic_task('work_rules')
    else:
        await taxi_fleet_synchronizer.post(
            '/fleet-synchronizer/v1/sync/park/property',
            params={'park_id': 'ParkOne', 'app_family': 'uberdriver'},
            headers={'Content-Type': 'application/json'},
        )

    assert driver_work_rules.mock_order_types_list.times_called == 1
    assert driver_work_rules.mock_order_types_put.times_called == 1
    assert driver_work_rules.mock_list_rules.times_called == 1
    assert driver_work_rules.mock_get_extended_rule.times_called == 3
    assert driver_work_rules.mock_put_extended_rule.times_called == 3

    original_rules = sorted(
        driver_work_rules.get_rules(INIT_PARK), key=lambda x: x['id'],
    )
    mapped_rules = sorted(
        driver_work_rules.get_rules(MAPPED_PARK), key=lambda x: x['id'],
    )

    for rule in original_rules:
        for entry in rule['calc_table']:
            if float(entry['commission_percent']) > 100:
                entry['commission_percent'] = '100.0000'

    assert mapped_rules == original_rules
