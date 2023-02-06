from time import time
import unittest

import pytest


@unittest.skip('not ready')
def test_road_accident_check_not_finished(taxi_jobs, db, mockserver, now):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'lat': 55.971204,
            'lon': 37.413673,
            'timestamp': 1526517142000,
            'speed': 123,
            'direction': 328,
        }

    taxi_jobs.run('road_accident_check', '--debug', '--without-lock')
    res = db.road_accidents.find_one()
    assert 'status' not in res
    assert res['tracker_check'][0]['status'] == 2


@unittest.skip('not ready')
@pytest.mark.filldb(road_accidents='confirmed')
@pytest.mark.config(
    ROAD_ACCIDENT_CHECK_JOB_PARAMS={
        'enabled': True,
        'stop_check_after_second': 20,
        'check_no_order': False,
        'min_distance_from_accident_meters': 500,
        'dist_lock_time_seconds': 300,
        'task_run_time_seconds': 250,
    },
)
def test_road_accident_check_confirmed(taxi_jobs, db, mockserver, now):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'lat': 55.44002914428711,
            'lon': 37.76626205444336,
            'timestamp': time(),
            'speed': 123,
            'direction': 328,
        }

    taxi_jobs.run('road_accident_check', '--debug', '--without-lock')
    res = db.road_accidents.find_one()
    assert res['status'] == 1


@unittest.skip('not ready')
@pytest.mark.filldb(road_accidents='unconfirmed')
def test_road_accident_check_unconfirmed(taxi_jobs, db, mockserver, now):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'lat': 56.44002914428711,
            'lon': 37.76626205444336,
            'timestamp': time(),
            'speed': 123,
            'direction': 328,
        }

    taxi_jobs.run('road_accident_check', '--debug', '--without-lock')
    res = db.road_accidents.find_one()
    assert res['status'] == 2
