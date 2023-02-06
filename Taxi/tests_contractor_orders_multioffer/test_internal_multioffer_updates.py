import datetime

import pytest

CURRENT_DT = '2020-03-20T11:22:33.123456Z'
TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S%zZ'


@pytest.mark.pgsql(
    'contractor_orders_multioffer', files=['multioffer_internal_state.sql'],
)
async def test_return_all(taxi_contractor_orders_multioffer):
    params = {'limit': 100}
    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v1/multioffer/updates', json=params,
    )
    assert response.status_code == 200
    json = response.json()
    multioffers = json['multioffers']
    assert len(multioffers) == 3

    assert multioffers[0]['order_id'] == '123'
    assert len(multioffers[0]['drivers']) == 2
    drivers = multioffers[0]['drivers']
    assert drivers[0]['park_id'] == 'park_id'
    assert drivers[0]['driver_profile_id'] == 'driver_profile_id_1'
    assert 'auction_iteration' not in drivers[0]
    assert drivers[1]['park_id'] == 'park_id'
    assert drivers[1]['driver_profile_id'] == 'driver_profile_id_6'
    assert 'auction_iteration' not in drivers[1]

    assert multioffers[1]['order_id'] == '321'
    assert len(multioffers[1]['drivers']) == 4
    drivers = multioffers[1]['drivers']
    assert drivers[0]['park_id'] == 'park_id'
    assert drivers[0]['driver_profile_id'] == 'driver_profile_id_2'
    assert 'auction_iteration' not in drivers[0]
    assert drivers[1]['park_id'] == 'park_id'
    assert drivers[1]['driver_profile_id'] == 'driver_profile_id_3'
    assert 'auction_iteration' not in drivers[1]
    assert drivers[2]['park_id'] == 'park_id'
    assert drivers[2]['driver_profile_id'] == 'driver_profile_id_4'
    assert 'auction_iteration' not in drivers[2]
    assert drivers[3]['park_id'] == 'park_id'
    assert drivers[3]['driver_profile_id'] == 'driver_profile_id_5'
    assert 'auction_iteration' not in drivers[3]

    assert multioffers[2]['order_id'] == '987'
    assert len(multioffers[2]['drivers']) == 4
    drivers = multioffers[2]['drivers']
    assert drivers[0]['park_id'] == 'park_id'
    assert drivers[0]['driver_profile_id'] == 'driver_profile_id_7'
    assert drivers[0]['auction_iteration'] == 1
    assert drivers[1]['park_id'] == 'park_id'
    assert drivers[1]['driver_profile_id'] == 'driver_profile_id_8'
    assert drivers[1]['auction_iteration'] == 1
    assert drivers[2]['park_id'] == 'park_id'
    assert drivers[2]['driver_profile_id'] == 'driver_profile_id_9'
    assert drivers[2]['auction_iteration'] == 2
    assert drivers[3]['park_id'] == 'park_id'
    assert drivers[3]['driver_profile_id'] == 'driver_profile_id_10'
    assert drivers[3]['auction_iteration'] == 1


@pytest.mark.now(CURRENT_DT)
async def test_return_nothing(taxi_contractor_orders_multioffer):
    params = {'limit': 100, 'last_updated_at': CURRENT_DT}
    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v1/multioffer/updates', json=params,
    )
    assert response.status_code == 200
    json = response.json()
    multioffers = json['multioffers']
    assert not multioffers
    assert json['last_updated_at'] == CURRENT_DT.replace('Z', '+00:00')


@pytest.mark.now(CURRENT_DT)
async def test_idempotency(taxi_contractor_orders_multioffer, mocked_time):
    request_date = mocked_time.now() - datetime.timedelta(minutes=35)
    last_updated_at = request_date.strftime(TIMESTAMP_FORMAT)
    params = {'limit': 100, 'last_updated_at': last_updated_at}
    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v1/multioffer/updates', json=params,
    )
    assert response.status_code == 200
    json = response.json()
    multioffers = json['multioffers']
    assert not multioffers
    assert json['last_updated_at'] == last_updated_at.replace('Z', '+00:00')
