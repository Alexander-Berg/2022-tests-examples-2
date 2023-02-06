import pytest

from taxi_tests.utils import ordered_object


def parse_supply_hours(db_drivers):
    drivers = []
    for db_driver in db_drivers:
        work_hours = []
        for db_work_hour in db_driver['work_hours']:
            work_hours.append(
                {
                    'work_hour': db_work_hour['work_hour'].isoformat(),
                    'work_time': db_work_hour['work_time'],
                },
            )
        drivers.append(
            {
                'park_id': db_driver['park_id'],
                'driver_id': db_driver['driver_id'],
                'work_hours': work_hours,
            },
        )
    return drivers


@pytest.mark.config(
    DRIVER_SUPPLY_HOURS_ENABLED=True,
    DRIVER_SUPPLY_HOURS_CLEANER_ENABLED=True,
    DRIVER_SUPPLY_HOURS_CLEAN_AFTER_HOURS=7,
    DRIVER_SUPPLY_HOURS_CLEANER_BATCH_SIZE=2,
)
@pytest.mark.now('2018-10-01T20:13:28Z')
def test_update_driver_supply_hours(taxi_labor, db, load_json):
    taxi_labor.run_workers(['update-driver-supply-hours'])

    actual_data = parse_supply_hours(db.driver_supply_hours.find({}))
    expected_data = load_json('db_driver_supply_hours_updated.json')
    ordered_object.assert_eq(actual_data, expected_data, ['', 'work_hours'])

    taxi_labor.run_workers(['driver-supply-hours-cleaner'])

    actual_data = parse_supply_hours(db.driver_supply_hours.find({}))
    expected_data = load_json('db_driver_supply_hours_cleaned.json')
    ordered_object.assert_eq(actual_data, expected_data, ['', 'work_hours'])
