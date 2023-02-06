import datetime
import time

import dateutil.parser
import pytest

from taxi_tests import utils


@pytest.mark.now('2018-02-16T14:00:01Z')
def test_simple(taxi_georeceiver, db):
    response = taxi_georeceiver.get('ping')
    assert response.status_code == 200

    response = taxi_georeceiver.get(
        '/service/status/store',
        params={
            'uuid': 'driver1',
            'status': 'verybusy',
            'status_int': 3,
            'robot': 1,
            'classes': 'comfortplus,vip,business2',
            'onlycard': 0,
            'provider': 1,
            'clid': '999011',
            'apikey': '8c***********************',
            'st': '1518789600',
        },
    )
    assert response.status_code == 200
    response = taxi_georeceiver.get(
        '/service/status/store',
        params={
            'uuid': 'driver1',
            'status': 'free',
            'status_int': 3,
            'robot': 1,
            'classes': 'comfortplus,vip,business2',
            'onlycard': 0,
            'provider': 1,
            'clid': '999011',
            'apikey': '8c***********************',
            'st': '1518789601',
        },
    )
    assert response.status_code == 200
    response = taxi_georeceiver.get(
        '/service/status/store',
        params={
            'uuid': 'driver2',
            'status': 'verybusy',
            'status_int': 3,
            'robot': 1,
            'classes': 'comfortplus,vip,business2',
            'onlycard': 0,
            'provider': 1,
            'clid': '999011',
            'apikey': '8c***********************',
            'st': '1518789600',
        },
    )
    assert response.status_code == 200
    response = taxi_georeceiver.get(
        '/service/status/store',
        params={
            'uuid': 'driver2',
            'status': 'verybusy',
            'status_int': 0,
            'robot': 1,
            'classes': 'comfortplus,vip,business2',
            'onlycard': 0,
            'provider': 1,
            'clid': '999011',
            'apikey': '8c***********************',
            'st': '1518789601',
        },
    )
    assert response.status_code == 200
    response = taxi_georeceiver.get(
        '/service/status/store',
        params={
            'uuid': 'driver3',
            'status': 'verybusy',
            'status_int': 3,
            'robot': 1,
            'classes': 'comfortplus,vip,business2',
            'onlycard': 0,
            'provider': 1,
            'clid': '999011',
            'apikey': '8c***********************',
            'st': '1518789601',
        },
    )
    assert response.status_code == 200
    response = taxi_georeceiver.get(
        '/service/status/store',
        params={
            'uuid': 'driver4',
            'status': 'verybusy',
            'status_int': 3,
            'robot': 1,
            'classes': 'comfortplus,vip,business2',
            'onlycard': 0,
            'provider': 1,
            'clid': '999011',
            'apikey': '8c***********************',
            'st': '1518789600',
        },
    )
    assert response.status_code == 200
    response = taxi_georeceiver.get(
        '/service/status/store',
        params={
            'uuid': 'driver5',
            'status': 'verybusy',
            'status_int': 3,
            'robot': 1,
            'classes': 'comfortplus,vip,business2',
            'onlycard': 0,
            'provider': 1,
            'clid': '999011',
            'apikey': '8c***********************',
            'st': '1518789600',
        },
    )
    assert response.status_code == 404
    mock_now = utils.to_utc(dateutil.parser.parse('2018-02-16T14:00:01Z'))
    taxi_georeceiver.invalidate_caches(mock_now)

    @utils.timeout(1, False)
    def wait_mongo():
        while True:
            if db.status_history.find_one({'driver_id': '999011_driver2'}):
                return True
            time.sleep(0.01)

    if not wait_mongo():
        assert not 'timeout'
        return

    docs = db.status_history.find().sort('driver_id')
    docs_list = []
    for i in docs:
        docs_list.append(i)

    for i in range(len(docs_list)):
        docs_list[i]['statuses'].sort(key=lambda k: k['timestamp'])

    ref = [
        {
            'driver_id': '999011_driver1',
            'created': datetime.datetime(2018, 2, 16, 12, 0, 0),
            'statuses': [
                {
                    'timestamp': datetime.datetime(2018, 2, 16, 14, 0),
                    'status': 'verybusy',
                    'taxi_status': 'order_free',
                },
                {
                    'timestamp': datetime.datetime(2018, 2, 16, 14, 0, 1),
                    'status': 'free',
                    'taxi_status': 'order_free',
                },
            ],
        },
        {
            'driver_id': '999011_driver2',
            'created': datetime.datetime(2018, 2, 16, 12, 0, 0),
            'statuses': [
                {
                    'timestamp': datetime.datetime(2018, 2, 16, 14, 0),
                    'status': 'verybusy',
                    'taxi_status': 'order_free',
                },
                {
                    'timestamp': datetime.datetime(2018, 2, 16, 14, 0, 1),
                    'status': 'verybusy',
                    'taxi_status': 'off',
                },
            ],
        },
        {
            'driver_id': '999011_driver3',
            'created': datetime.datetime(2018, 2, 16, 12, 0, 0),
            'statuses': [
                {
                    'timestamp': datetime.datetime(2018, 2, 16, 14, 0, 1),
                    'status': 'verybusy',
                    'taxi_status': 'order_free',
                    'is_blocked': True,
                },
            ],
        },
        {
            'driver_id': '999011_driver4',
            'created': datetime.datetime(2018, 2, 16, 12, 0, 0),
            'statuses': [
                {
                    'timestamp': datetime.datetime(2018, 2, 16, 14, 0),
                    'status': 'verybusy',
                    'taxi_status': 'order_free',
                },
            ],
        },
    ]
    assert len(docs_list) == len(ref)
    for i in range(len(ref)):
        for k in ref[i]:
            assert ref[i][k] == docs_list[i][k]


def test_onlycard_flag_is_written_to_db(taxi_georeceiver, db):
    response1 = taxi_georeceiver.get(
        '/service/status/store?clid=999011&'
        'uuid=driver1&status=free&status_int=2'
        '&provider=0&apikey=8c***********************',
    )
    assert response1.status_code == 200
    response2 = taxi_georeceiver.get(
        '/service/status/store?clid=999011&'
        'uuid=driver2&status=verybusy&status_int=2'
        '&onlycard=0&provider=0&apikey=8c***********************',
    )
    assert response2.status_code == 200
    response3 = taxi_georeceiver.get(
        '/service/status/store?clid=999011&'
        'uuid=driver3&status=free&status_int=2'
        '&onlycard=1&provider=0&apikey=8c***********************',
    )
    assert response3.status_code == 200
    time.sleep(3)
