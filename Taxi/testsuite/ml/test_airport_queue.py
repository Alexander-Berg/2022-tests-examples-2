from __future__ import print_function

import pytest


CONFIG_V2 = {
    'AIRPORT_QUEUE_ML_CONFIG': {
        'airports': [
            {
                'airport_name': 'platov_airport',
                'iata_code': 'rov',
                'update_timetable_data': True,
                'use_timetable_model': True,
            },
        ],
        'timetable_base_url': 'nononon',
        'timetable_data_life_time_s': 900,
        'timetable_enabled': False,
        'timetable_log_future_s': 7200,
        'timetable_log_past_s': 7200,
        'timetable_request_retries': 1,
        'timetable_request_timeout_ms': 1000,
        'timetable_update_interval_time_s': 1,
    },
}


def check_values(request, response):
    assert 'predicted' in response.json()
    assert 'raw_predicted' in response.json()
    assert len(response.json()['predicted']) == len(
        response.json()['raw_predicted'],
    )
    assert all(x > 0 for x in response.json()['predicted'])


def test_ml_airport_queue_ok(taxi_ml, load_json):
    request = load_json('request_ok.json')
    response = taxi_ml.post('airport_queue', json=request)
    assert response.status_code == 200
    check_values(request, response)


def test_ml_airport_queue_bad(taxi_ml, load_json):
    request = load_json('request_bad.json')
    response = taxi_ml.post('airport_queue', json=request)
    assert response.status_code == 400


def test_ml_airport_queue_timetable_request(
        taxi_ml, mock_timetable_airport_queue,
):
    taxi_ml.invalidate_caches()

    mock_timetable_airport_queue.wait_call()


def test_ml_airport_queue_timetable_bad_request(
        taxi_ml, mock_timetable_airport_queue,
):
    taxi_ml.invalidate_caches()

    mock_timetable_airport_queue.set_response([{'lala': 'bad'}])
    mock_timetable_airport_queue.wait_call()


@pytest.mark.config(**CONFIG_V2)
def test_ml_airport_queue_v2_ok(taxi_ml, load_json):
    request = load_json('request_ok.json')
    response = taxi_ml.post('airport_queue', json=request)
    assert response.status_code == 200
    check_values(request, response)


@pytest.mark.config(**CONFIG_V2)
def test_ml_airport_queue_v2_bad(taxi_ml, load_json):
    request = load_json('request_bad.json')
    response = taxi_ml.post('airport_queue', json=request)
    assert response.status_code == 400
