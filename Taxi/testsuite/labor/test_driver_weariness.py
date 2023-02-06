import datetime

from bson.objectid import ObjectId
import pytest


@pytest.mark.config(DRIVER_WEARINESS_ENABLED=True)
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_driver_weariness_calculation(taxi_labor, db, now):
    taxi_labor.run_workers(['update-driver-weariness'])

    # check calculation of work intervals
    # 4 intervals of work for 1 minute and 2 intervals of rest for 1 minute
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('0123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 60960
    assert weariness_obj['working_time'] == 240
    assert weariness_obj['working_time_no_rest'] == 240
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 18, 33,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 18, 35,
    )
    assert weariness_obj['block_time'] is None
    assert weariness_obj['block_till'] is None

    # check not calculate large intervals and statuses when driver is tired
    # 4 intervals with work for 1 minutes, 1 large interval(more than 1 hour)
    # and one "free" status when driver blocked (which calc as "not online")
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('1123456789ab0123456789ab')},
    )
    assert weariness_obj['_id'] == ObjectId('1123456789ab0123456789ab')
    assert weariness_obj['remaining_time'] == 60960
    assert weariness_obj['working_time'] == 240
    assert weariness_obj['working_time_no_rest'] == 3900
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 19, 34,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 19, 34,
    )
    assert weariness_obj['block_time'] is None
    assert weariness_obj['block_till'] is None

    # no work time
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('7123456789ab0123456789ab')},
    )
    assert weariness_obj is None


@pytest.mark.config(
    DRIVER_WEARINESS_ENABLED=True,
    DRIVER_WEARINESS_MAX_WORK_MINUTES={'__default__': 300},
)
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_driver_weariness_calculation_real_remaining_time(taxi_labor, db, now):
    taxi_labor.run_workers(['update-driver-weariness'])

    # in the first interval
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('3123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 1620
    assert weariness_obj['working_time'] == 16380
    assert weariness_obj['working_time_no_rest'] == 2100
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 23, 35,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 23, 35,
    )
    assert weariness_obj['block_time'] is None
    assert weariness_obj['block_till'] is None

    # in the second interval
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('2123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 12660
    assert weariness_obj['working_time'] == 16200
    assert weariness_obj['working_time_no_rest'] == 1920
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 23, 32,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 23, 32,
    )
    assert weariness_obj['block_time'] is None
    assert weariness_obj['block_till'] is None

    # in the fourth interval, that is too long for calculate
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('4123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 17700
    assert weariness_obj['working_time'] == 14400
    assert weariness_obj['working_time_no_rest'] == 300
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 23, 5,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 23, 5,
    )
    assert weariness_obj['block_time'] is None
    assert weariness_obj['block_till'] is None

    # returning max working time case
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('5123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 18000
    assert weariness_obj['working_time'] == 14100
    assert weariness_obj['working_time_no_rest'] == 14880
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 4, 37,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 4, 37,
    )
    assert weariness_obj['block_time'] is None
    assert weariness_obj['block_till'] is None


@pytest.mark.config(
    DRIVER_WEARINESS_ENABLED=True,
    DRIVER_WEARINESS_MAX_WORK_MINUTES={'__default__': 200},
)
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_driver_weariness_block_by_hours(taxi_labor, db, now):
    taxi_labor.run_workers(['update-driver-weariness'])

    # block by hours with interval equal 29 minutes in beginning
    # and 35 minutes more than max work time.
    # So block time is : 29m + 35m + 1h = 2h
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('6123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 0
    assert weariness_obj['working_time'] == 14100
    assert weariness_obj['working_time_no_rest'] == 14880
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 4, 37,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 4, 37,
    )
    assert weariness_obj['block_time'] == datetime.datetime(
        2018, 1, 22, 00, 00,
    )
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 2, 4)
    driver_id_17_update_time = weariness_obj['updated']

    # block by hours with no interval in beginning
    # and 34 minutes more than max work time
    # block time: 1h + 34m = 1h 34m
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('8123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 0
    assert weariness_obj['working_time'] == 14040
    assert weariness_obj['working_time_no_rest'] == 16620
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 4, 37,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 4, 37,
    )
    assert weariness_obj['block_time'] == datetime.datetime(
        2018, 1, 22, 00, 00,
    )
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 1, 34)
    driver_id_19_update_time = weariness_obj['updated']

    # block by hours with merging of intervals by 2 profiles
    # with 10 minutes interval in beginning
    # and work 44 minutes than max work time
    # block time: 44 minutes + 10 minutes + 1h = 1h 54 min
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('9123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 0
    assert weariness_obj['working_time'] == 14640
    assert weariness_obj['working_time_no_rest'] == 16020
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 4, 37,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 4, 37,
    )
    assert weariness_obj['block_time'] == datetime.datetime(
        2018, 1, 22, 00, 00,
    )
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 1, 54)
    driver_id_20_update_time = weariness_obj['updated']

    # change time and check that block times not changes.
    now = now + datetime.timedelta(minutes=30)
    taxi_labor.tests_control(now)

    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('6123456789ab0123456789ab')},
    )
    assert weariness_obj['updated'] == driver_id_17_update_time
    assert weariness_obj['block_time'] == datetime.datetime(
        2018, 1, 22, 00, 00,
    )
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 2, 4)

    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('8123456789ab0123456789ab')},
    )
    assert weariness_obj['updated'] == driver_id_19_update_time
    assert weariness_obj['block_time'] == datetime.datetime(
        2018, 1, 22, 00, 00,
    )
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 1, 34)

    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('9123456789ab0123456789ab')},
    )
    assert weariness_obj['updated'] == driver_id_20_update_time
    assert weariness_obj['block_time'] == datetime.datetime(
        2018, 1, 22, 00, 00,
    )
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 1, 54)


@pytest.mark.config(
    DRIVER_WEARINESS_ENABLED=True,
    DRIVER_WEARINESS_MAX_WORK_MINUTES={'__default__': 200},
)
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_driver_weariness_block_by_hours_with_old_block(taxi_labor, db, now):
    taxi_labor.run_workers(['update-driver-weariness'])

    # block by hours with interval equal 29 minutes in beginning
    # and 35 minutes more than max work time.
    # So block time is : 29m + 35m + 1h = 2h
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('d123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 0
    assert weariness_obj['working_time'] == 14100
    assert weariness_obj['working_time_no_rest'] == 14880
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 4, 37,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 4, 37,
    )
    # block time from old lock
    assert weariness_obj['block_time'] == datetime.datetime(
        2018, 1, 21, 22, 00,
    )
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 2, 4)
    driver_id_24_update_time = weariness_obj['updated']

    # change time and check that block times not changes.
    now = now + datetime.timedelta(minutes=29)
    taxi_labor.tests_control(now)

    taxi_labor.run_workers(['update-driver-weariness'])

    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('d123456789ab0123456789ab')},
    )
    assert weariness_obj['updated'] == driver_id_24_update_time
    assert weariness_obj['block_time'] == datetime.datetime(
        2018, 1, 21, 22, 00,
    )
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 2, 4)


@pytest.mark.config(
    DRIVER_WEARINESS_ENABLED=True,
    DRIVER_WEARINESS_MAX_WORK_MINUTES={'__default__': 200},
    DRIVER_WEARINESS_MAD_MAX_WORK_MINUTES={'__default__': 50},
    DRIVER_WEARINESS_MULTI_APP_DRIVERS_ENABLED=True,
)
@pytest.mark.driver_experiments('driver_weariness_experiment')
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_driver_weariness_multi_app_drivers(taxi_labor, db, now):
    taxi_labor.run_workers(['update-driver-weariness'])

    # block driver by new rules for multi app drivers
    # block_time = min_block_time (1h) + overlimit for work (9 min) = 1h 9min
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('a123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 0
    assert weariness_obj['working_time'] == 3540
    assert weariness_obj['working_time_no_rest'] == 3540
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 0, 59,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 0, 59,
    )
    assert weariness_obj['block_time'] == datetime.datetime(
        2018, 1, 22, 00, 00,
    )
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 1, 9)
    assert weariness_obj['is_multi_app_block'] is True

    # block by default rules, when multiapp config enabled.
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('b123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 12000
    assert weariness_obj['working_time'] == 3540
    assert weariness_obj['working_time_no_rest'] == 3540
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 0, 59,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 0, 59,
    )
    assert weariness_obj['block_time'] is None
    assert weariness_obj['block_till'] is None

    # block driver by new rules for multi app drivers,
    # when one profile is not multi app.
    # block_time = min_block_time (1h) + overlimit for work (8 min) = 1h 8min
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('c123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 0
    assert weariness_obj['working_time'] == 3480
    assert weariness_obj['working_time_no_rest'] == 3540
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 0, 59,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 0, 59,
    )
    assert weariness_obj['block_time'] == datetime.datetime(
        2018, 1, 22, 00, 00,
    )
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 1, 8)
    assert weariness_obj['is_multi_app_block'] is True


@pytest.mark.config(
    DRIVER_WEARINESS_ENABLED=True,
    DRIVER_WEARINESS_MAD_RETURNED_DRIVER_IDS=['1369_driverSS12'],
    DRIVER_WEARINESS_MAX_WORK_MINUTES={'__default__': 200},
    DRIVER_WEARINESS_MAD_MAX_WORK_MINUTES={'__default__': 50},
    DRIVER_WEARINESS_BLOCK_HOURS_EXCEED_MINUTES={'__default__': 40},
    DRIVER_WEARINESS_MULTI_APP_DRIVERS_ENABLED=True,
)
@pytest.mark.driver_experiments('driver_weariness_experiment')
@pytest.mark.filldb(driver_weariness='returned')
@pytest.mark.filldb(multiapp_drivers='returned')
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_driver_weariness_multi_app_returned_drivers(taxi_labor, db, now):
    taxi_labor.run_workers(['update-driver-weariness'])

    # unblock multiapp driver, because of returned config
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('a123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 12000
    assert weariness_obj['working_time'] == 3540
    assert weariness_obj['working_time_no_rest'] == 3540
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 0, 59,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 0, 59,
    )
    assert weariness_obj.get('block_time') is None
    assert weariness_obj.get('block_till') is None
    assert weariness_obj.get('is_multi_app_block') is None

    # don't unlock returned driver, because it is still multi app
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('b123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 0
    assert weariness_obj['working_time'] == 3540
    assert weariness_obj['working_time_no_rest'] == 3540
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 0, 59,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 0, 59,
    )
    assert weariness_obj['block_time'] == datetime.datetime(
        2018, 1, 21, 22, 00,
    )
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 1, 0)
    assert weariness_obj['is_multi_app_block'] is True

    # don't unlock driver, because it is not returned.
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('c123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 0
    assert weariness_obj['working_time'] == 3540
    assert weariness_obj['working_time_no_rest'] == 3540
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 21, 0, 59,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 21, 0, 59,
    )
    assert weariness_obj['block_time'] == datetime.datetime(
        2018, 1, 21, 22, 00,
    )
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 1, 0)
    assert weariness_obj['is_multi_app_block'] is True


@pytest.mark.config(
    DRIVER_WEARINESS_ENABLED=True,
    DRIVER_WEARINESS_MAX_WORK_MINUTES={'__default__': 200},
)
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_driver_weariness_no_move_statuses_check(taxi_labor, db, now):
    taxi_labor.run_workers(['update-driver-weariness'])

    # busy and free statuses after 2018-01-21T03:30:00.0 not calculated,
    # because driver is not moving
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('e123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 1320
    assert weariness_obj['working_time'] == 10680
    assert weariness_obj['working_time_no_rest'] == 14580
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 4, 37,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 4, 37,
    )
    assert weariness_obj['block_time'] is None
    assert weariness_obj['block_till'] is None


@pytest.mark.config(
    DRIVER_WEARINESS_ENABLED=True,
    DRIVER_WEARINESS_MAX_WORK_MINUTES={'__default__': 200},
)
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_driver_weariness_repositioned_and_free_verybusy(taxi_labor, db, now):
    taxi_labor.run_workers(['update-driver-weariness'])

    # busy and free statuses after 2018-01-21T03:30:00.0 not calculated,
    # because driver is not moving
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('f123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 12000
    assert weariness_obj['working_time'] == 60
    assert weariness_obj['working_time_no_rest'] == 60
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 1, 30,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 1, 32,
    )
    assert weariness_obj['block_time'] is None
    assert weariness_obj['block_till'] is None


@pytest.mark.config(
    DRIVER_WEARINESS_ENABLED=True,
    DRIVER_WEARINESS_MAX_WORK_MINUTES={'__default__': 200},
    DRIVER_WEARINESS_WORK_REST_ENABLED=True,
    DRIVER_WEARINESS_WORK_REST_TIME_MINUTES=480,
)
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_driver_weariness_work_rest_set(taxi_labor, db, now):
    taxi_labor.run_workers(['update-driver-weariness'])

    # rest in the end more than 480 minutes
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('0223456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 12000
    assert weariness_obj['working_time'] == 0
    assert weariness_obj['working_time_no_rest'] == 240
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 15, 32,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 15, 32,
    )
    assert weariness_obj['block_time'] is None
    assert weariness_obj['block_till'] is None

    # rest in the middle more than 480 minutes
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('1223456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 11940
    assert weariness_obj['working_time'] == 60
    assert weariness_obj['working_time_no_rest'] == 60
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 16, 32,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 16, 32,
    )
    assert weariness_obj['block_time'] is None
    assert weariness_obj['block_till'] is None


@pytest.mark.config(
    DRIVER_WEARINESS_ENABLED=True,
    DRIVER_WEARINESS_MAX_WORK_MINUTES={'__default__': 200},
    DRIVER_WEARINESS_WORK_REST_ENABLED=True,
    DRIVER_WEARINESS_WORK_REST_TIME_MINUTES=480,
    DRIVER_WEARINESS_BLOCK_NO_LONG_REST={'__default__': True, 'Москва': True},
    DRIVER_WEARINESS_MAX_WORK_NO_REST_MINUTES={'__default__': 5, 'Москва': 5},
    DRIVER_WEARINESS_BLOCK_NO_REST_MINUTES={'__default__': 180, 'Москва': 180},
)
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_driver_weariness_by_city(taxi_labor, db, now):
    taxi_labor.run_workers(['update-driver-weariness'])

    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('2123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 0
    assert weariness_obj['working_time'] == 1920
    assert weariness_obj['working_time_no_rest'] == 1920
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 23, 32,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 23, 32,
    )
    assert weariness_obj['block_time'] == datetime.datetime(2018, 1, 22, 0, 0)
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 2, 32)


@pytest.mark.config(
    DRIVER_WEARINESS_ENABLED=True,
    DRIVER_WEARINESS_MAX_WORK_MINUTES={'__default__': 200},
    DRIVER_WEARINESS_WORK_REST_ENABLED=True,
    DRIVER_WEARINESS_WORK_REST_TIME_MINUTES=480,
    DRIVER_WEARINESS_BLOCK_NO_LONG_REST_BY_PARK_AND_DRIVER={
        '1488': {'__default__': False, 'driverSS3': True},
    },
    DRIVER_WEARINESS_MAX_WORK_TIME_BY_PARK_AND_DRIVER={
        '1488': {'__default__': 200, 'driverSS3': 5},
    },
    DRIVER_WEARINESS_BLOCK_NO_REST_TIME_BY_PARK_AND_DRIVER={
        '1488': {'__default__': 480, 'driverSS3': 180},
    },
)
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_driver_weariness_by_driver_id(taxi_labor, db, now):
    taxi_labor.run_workers(['update-driver-weariness'])

    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('2123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 0
    assert weariness_obj['working_time'] == 1920
    assert weariness_obj['working_time_no_rest'] == 1920
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 23, 32,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 23, 32,
    )
    assert weariness_obj['block_time'] == datetime.datetime(2018, 1, 22, 0, 0)
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 2, 32)


@pytest.mark.config(
    DRIVER_WEARINESS_ENABLED=True,
    DRIVER_WEARINESS_MAX_WORK_MINUTES={'__default__': 200},
    DRIVER_WEARINESS_WORK_REST_ENABLED=True,
    DRIVER_WEARINESS_WORK_REST_TIME_MINUTES=480,
    DRIVER_WEARINESS_BLOCK_NO_LONG_REST_BY_PARK_AND_DRIVER={
        '1488': {'__default__': True},
    },
    DRIVER_WEARINESS_MAX_WORK_TIME_BY_PARK_AND_DRIVER={
        '1488': {'__default__': 5},
    },
    DRIVER_WEARINESS_BLOCK_NO_REST_TIME_BY_PARK_AND_DRIVER={
        '1488': {'__default__': 180},
    },
)
@pytest.mark.now('2018-01-22T00:00:00Z')
def test_driver_weariness_by_park_id(taxi_labor, db, now):
    taxi_labor.run_workers(['update-driver-weariness'])

    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('2123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 0
    assert weariness_obj['working_time'] == 1920
    assert weariness_obj['working_time_no_rest'] == 1920
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 23, 32,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 23, 32,
    )
    assert weariness_obj['block_time'] == datetime.datetime(2018, 1, 22, 0, 0)
    assert weariness_obj['block_till'] == datetime.datetime(2018, 1, 22, 2, 32)


@pytest.mark.config(
    DRIVER_WEARINESS_ENABLED=True,
    DRIVER_WEARINESS_BLOCK_NO_LONG_REST={'__default__': True},
    DRIVER_WEARINESS_MAX_WORK_NO_REST_MINUTES={'__default__': 400},
)
@pytest.mark.filldb(status_history='long_rest')
@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.parametrize(
    'working_time_no_rest',
    [
        pytest.param(
            0,
            marks=pytest.mark.config(
                DRIVER_WEARINESS_RESET_WORK_NO_REST_ENABLED=True,
            ),
        ),
        pytest.param(
            2700,
            marks=pytest.mark.config(
                DRIVER_WEARINESS_RESET_WORK_NO_REST_ENABLED=False,
            ),
        ),
    ],
)
def test_driver_weariness_no_long_rest(
        taxi_labor, db, now, working_time_no_rest,
):
    taxi_labor.run_workers(['update-driver-weariness'])

    # in the first interval
    weariness_obj = db.driver_weariness.find_one(
        {'_id': ObjectId('3123456789ab0123456789ab')},
    )
    assert weariness_obj['remaining_time'] == 24000 - working_time_no_rest
    assert weariness_obj['working_time'] == 16980
    assert weariness_obj['working_time_no_rest'] == working_time_no_rest
    assert weariness_obj['last_online'] == datetime.datetime(
        2018, 1, 21, 23, 35,
    )
    assert weariness_obj['last_status_time'] == datetime.datetime(
        2018, 1, 21, 23, 35,
    )
    assert weariness_obj['block_time'] is None
    assert weariness_obj['block_till'] is None
