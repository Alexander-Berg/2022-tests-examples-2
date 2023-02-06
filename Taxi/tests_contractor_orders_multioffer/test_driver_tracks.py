import pytest

URL = '/admin/v1/multioffer/driver-tracks'


@pytest.mark.pgsql(
    'contractor_orders_multioffer', files=['multioffer_driver_tracks.sql'],
)
async def test_order_id_no_candidates(taxi_contractor_orders_multioffer):
    params = {'order_id': 'order_id_no_candidates'}
    response = await taxi_contractor_orders_multioffer.get(URL, params=params)
    assert response.status_code == 200
    assert response.json()['drivers'] == []


@pytest.mark.pgsql(
    'contractor_orders_multioffer', files=['multioffer_driver_tracks.sql'],
)
async def test_bad_order_id(taxi_contractor_orders_multioffer):
    params = {'order_id': 'bad_order_id'}
    response = await taxi_contractor_orders_multioffer.get(URL, params=params)
    assert response.status_code == 200
    assert response.json()['drivers'] == []


@pytest.mark.pgsql(
    'contractor_orders_multioffer', files=['multioffer_driver_tracks.sql'],
)
async def test_two_candidates(taxi_contractor_orders_multioffer):
    params = {'order_id': 'order_id'}
    response = await taxi_contractor_orders_multioffer.get(URL, params=params)
    assert response.status_code == 200
    assert response.json()['drivers']
    drivers = response.json()['drivers']
    assert len(drivers) == 2
    assert {
        'car_number': 'Н123УТ777',
        'clid': '123456789001',
        'db_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
        'distance': 1935,
        'name': 'Иванов Иван Иванович',
        'point': {'lat': 44.12392, 'lon': 77.89571},
        'status': 'win',
        'time': 225,
        'uuid': '4bb5a0018d9641c681c1a854b21ec9ab',
    } in drivers
    assert {
        'car_number': 'Н321УТ777',
        'clid': '123456789002',
        'db_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
        'distance': 1000,
        'name': 'Смирнов Смирн Смирнович',
        'point': {'lat': 44.123, 'lon': 77.895},
        'status': 'declined',
        'time': 123,
        'uuid': 'e26e1734d70b46edabe993f515eda54e',
    } in drivers
