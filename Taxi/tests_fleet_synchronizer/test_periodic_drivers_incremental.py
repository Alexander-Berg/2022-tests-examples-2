import pytest

from tests_fleet_synchronizer import common


@pytest.mark.pgsql(
    'fleet-synchronizer-db',
    files=['pg_fleet-synchronizer-db.sql'],
    queries=[
        common.make_driver_mapping_query(
            park_id='ParkOne',
            driver_id='DriverOne',
            mapped_driver_id='DriverOneVezet',
            app_family=common.FLEET_TYPE_VEZET,
        ),
    ],
)
async def test_drivers_incremental(taxi_fleet_synchronizer, mongodb):
    # nothing mapped in mongo
    assert not list(
        mongodb.dbdrivers.find({'fleet_type': common.FLEET_TYPE_VEZET}),
    )
    assert not list(
        mongodb.dbcars.find({'fleet_type': common.FLEET_TYPE_VEZET}),
    )

    # set updated_ts for the task to hook the driver
    mongodb.dbdrivers.update_one(
        {'driver_id': 'DriverOne'},
        {'$currentDate': {'updated_ts': {'$type': 'timestamp'}}},
    )
    await taxi_fleet_synchronizer.invalidate_caches()

    await taxi_fleet_synchronizer.run_periodic_task('drivers_incremental')

    # mapped one driver
    drivers = list(
        mongodb.dbdrivers.find({'fleet_type': common.FLEET_TYPE_VEZET}),
    )
    assert len(drivers) == 1
    assert drivers[0]['driver_id'] == 'DriverOneVezet'
    assert drivers[0]['park_id'] == 'ParkOneVezet'

    # mapped one car
    cars = list(mongodb.dbcars.find({'fleet_type': common.FLEET_TYPE_VEZET}))
    assert len(cars) == 1
    assert cars[0]['park_id'] == 'ParkOneVezet'


@pytest.mark.pgsql(
    'fleet-synchronizer-db', files=['pg_fleet-synchronizer-db.sql'],
)
async def test_drivers_incremental_no_park(
        taxi_fleet_synchronizer, mongodb, pgsql,
):
    with pgsql['fleet-synchronizer-db'].cursor() as cursor:
        cursor.execute('TRUNCATE fleet_sync.parks_mappings')

    # nothing mapped in mongo
    assert not list(
        mongodb.dbdrivers.find({'fleet_type': common.FLEET_TYPE_VEZET}),
    )
    assert not list(
        mongodb.dbcars.find({'fleet_type': common.FLEET_TYPE_VEZET}),
    )

    # set updated_ts for the task to hook the driver
    mongodb.dbdrivers.update_one(
        {'driver_id': 'DriverOne'},
        {'$currentDate': {'updated_ts': {'$type': 'timestamp'}}},
    )

    await taxi_fleet_synchronizer.invalidate_caches()
    await taxi_fleet_synchronizer.run_periodic_task('drivers_incremental')

    # haven't mapped the driver
    drivers = list(
        mongodb.dbdrivers.find({'fleet_type': common.FLEET_TYPE_VEZET}),
    )
    assert not drivers

    # haven't mapped the car
    cars = list(mongodb.dbcars.find({'fleet_type': common.FLEET_TYPE_VEZET}))
    assert not cars


@pytest.mark.pgsql(
    'fleet-synchronizer-db', files=['pg_fleet-synchronizer-db.sql'],
)
async def test_drivers_incremental_no_driver(taxi_fleet_synchronizer, mongodb):
    # nothing mapped in mongo
    assert not list(
        mongodb.dbdrivers.find({'fleet_type': common.FLEET_TYPE_VEZET}),
    )
    assert not list(
        mongodb.dbcars.find({'fleet_type': common.FLEET_TYPE_VEZET}),
    )

    # set updated_ts for the task to hook the driver
    mongodb.dbdrivers.update_one(
        {'driver_id': 'DriverOne'},
        {'$currentDate': {'updated_ts': {'$type': 'timestamp'}}},
    )

    await taxi_fleet_synchronizer.invalidate_caches()
    await taxi_fleet_synchronizer.run_periodic_task('drivers_incremental')

    # haven't mapped the driver
    drivers = list(
        mongodb.dbdrivers.find({'fleet_type': common.FLEET_TYPE_VEZET}),
    )
    assert not drivers

    # haven't mapped the car
    cars = list(mongodb.dbcars.find({'fleet_type': common.FLEET_TYPE_VEZET}))
    assert not cars
