import time

import pytest

from taxi_tests import utils


@pytest.mark.parametrize(
    'query,expected_status_history',
    [
        (
            # query
            [
                {
                    'dbid': 'dbid',
                    'uuid': 'driver1',
                    'status': 'online',
                    'order_status': 'none',
                    'order_provider': 'unknown',
                    'updated_ts': 0,
                },
                {
                    'dbid': 'dbid',
                    'uuid': 'driver2',
                    'status': 'busy',
                    'order_status': 'none',
                    'order_provider': 'unknown',
                    'updated_ts': 0,
                },
            ],
            # expected_status_history
            [
                {
                    'driver_id': 'clid_driver1',
                    'statuses': [{'status': 'free', 'taxi_status': 'free'}],
                },
                {
                    'driver_id': 'clid_driver2',
                    'statuses': [
                        {'status': 'verybusy', 'taxi_status': 'busy'},
                    ],
                },
            ],
        ),
        (
            # query
            [
                {
                    'dbid': 'dbid',
                    'uuid': 'driver3',
                    'status': 'online',
                    'order_status': 'transporting',
                    'order_provider': 'yandex',
                    'updated_ts': 0,
                },
            ],
            # expected_status_history
            [
                {
                    'driver_id': 'clid_driver3',
                    'statuses': [
                        {'status': 'verybusy', 'taxi_status': 'order_free'},
                    ],
                },
            ],
        ),
        (
            # query
            [
                {
                    'dbid': 'dbid',
                    'uuid': 'driver4',
                    'status': 'busy',
                    'order_status': 'transporting',
                    'order_provider': 'yandex',
                    'updated_ts': 0,
                },
            ],
            # expected_status_history
            [
                {
                    'driver_id': 'clid_driver4',
                    'statuses': [
                        {'status': 'verybusy', 'taxi_status': 'order_busy'},
                    ],
                },
            ],
        ),
    ],
)
def test_driver_status_store(
        taxi_georeceiver, query, expected_status_history, db,
):
    @utils.timeout(1, False)
    def wait_mongo(collection, key):
        while True:
            if collection.find_one(key):
                return True
            time.sleep(0.01)

    response = taxi_georeceiver.post('/service/driver-status/store', query)
    assert response.status_code == 200

    taxi_georeceiver.invalidate_caches()

    for status_history in expected_status_history:
        if not wait_mongo(
                db.status_history, {'driver_id': status_history['driver_id']},
        ):
            assert not 'timeout'
            return

        entry2 = db.status_history.find_one(
            {'driver_id': status_history['driver_id']},
        )
        assert len(entry2['statuses']) == len(status_history['statuses'])
        entry2['statuses'].sort(key=lambda k: k['timestamp'])
        for i in range(len(entry2['statuses'])):
            status = entry2['statuses'][i]['status']
            exp_status = status_history['statuses'][i]['status']
            assert status == exp_status
            tx_status = entry2['statuses'][i]['taxi_status']
            exp_tx_status = status_history['statuses'][i]['taxi_status']
            assert tx_status == exp_tx_status
