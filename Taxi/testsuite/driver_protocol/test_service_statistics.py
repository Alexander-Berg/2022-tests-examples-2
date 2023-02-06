import pytest


@pytest.mark.xfail(reason='flap, see TAXIBACKEND-19276')
def test_service_statistics(taxi_driver_protocol):
    response = taxi_driver_protocol.get('service/statistics')
    assert response.status_code == 200
    body = response.json()
    assert 'total' in body
    total = body['total']
    assert 'code' in total
    assert 'message' in total
    assert 'queue_waiting_times' in body


@pytest.mark.config(
    AIRPORT_QUEUE_SETTINGS={
        'moscow': {
            'ENABLED': True,
            'HIGH_GRADE': 100,
            'ACTIVATION_AREA': 'moscow_activation',
            'SURROUNDING_AREA': 'moscow_surrounding',
            'HOME_ZONE': 'moscow',
            'ML_WHITELIST_CLASSES': ['vip'],
        },
    },
)
def test_service_statistics_fail(taxi_driver_protocol):
    response = taxi_driver_protocol.get('service/statistics')
    assert response.status_code == 200
    body = response.json()
    assert body['queue_waiting_times']['moscow']['vip']['no_info']


@pytest.mark.config(
    AIRPORT_QUEUE_SETTINGS={
        'moscow': {
            'ENABLED': True,
            'HIGH_GRADE': 100,
            'ACTIVATION_AREA': 'moscow_activation',
            'SURROUNDING_AREA': 'moscow_surrounding',
            'HOME_ZONE': 'moscow',
            'ML_WHITELIST_CLASSES': ['vip'],
            'ML_STATS_EXCLUDE_CLASSES': ['vip'],
        },
    },
)
def test_service_statistics_ok(taxi_driver_protocol):
    response = taxi_driver_protocol.get('service/statistics')
    assert response.status_code == 200
    body = response.json()
    assert 'moscow' not in body['queue_waiting_times']


@pytest.mark.config(
    AIRPORT_QUEUE_SETTINGS={
        'moscow': {
            'ENABLED': True,
            'HIGH_GRADE': 100,
            'ACTIVATION_AREA': 'moscow_activation',
            'SURROUNDING_AREA': 'moscow_surrounding',
            'HOME_ZONE': 'moscow',
            'ML_WHITELIST_CLASSES': ['econom'],
        },
    },
)
def test_service_statistics_ok2(taxi_driver_protocol):
    response = taxi_driver_protocol.get('service/statistics')
    assert response.status_code == 200
    body = response.json()
    test_zone = body['queue_waiting_times']['moscow']['econom']
    assert test_zone['updated'] > 50
