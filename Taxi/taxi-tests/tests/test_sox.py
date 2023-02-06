import logging

import pymongo

from taxi_tests import utils
from taxi_tests.utils import log_requests

logger = logging.getLogger(__file__)

POINT_SOURCE = [37.535, 55.546]
POINT_DESTINATION = [37.535, 55.546]
SATISFY_ERROR_MSG = f'Drivers were not satisfied in time'


def _try_make_order(client_maker, park_clid):
    client = client_maker()
    client.init_phone(phone='random')
    client.set_current_park(park_clid)
    client.launch()
    client.set_source(POINT_SOURCE)
    client.set_destinations([POINT_DESTINATION])

    try:
        client.order('speed-1000,wait-0')
        client.wait_for_order_status(timeout=90)
    except TimeoutError as exc:
        logger.exception(exc)
        return False

    return True


def _check_drivers(drivers, park_id):
    for driver in drivers:
        if driver['dbid'] == park_id and driver['is_satisfied']:
            return False
    return True


def test_takes_urgent(client_maker):
    park_clid = '111501'

    order_success = _try_make_order(client_maker, park_clid)
    assert order_success

    response = log_requests.post(
        'http://candidates.taxi.yandex.net/profiles-snapshot',
        json={'parts': 1, 'part': 0},
    )
    response.raise_for_status()
    drivers = response.json()['drivers']

    client = pymongo.MongoClient('mongodb://mongo.taxi.yandex:27017/')
    client.dbtaxi.parks.update(
        {'_id': park_clid},
        {
            '$set': {'takes_urgent': False},
            '$currentDate': {
                'updated': True,
                'updated_ts': {'$type': 'timestamp'},
            },
        },
        upsert=False,
    )

    # candidates cache update
    park_id = '1b0512eca97c4a1bbe53b50bdc0d5179'
    for _ in utils.wait_for(120, SATISFY_ERROR_MSG, sleep=5):
        satisfy = log_requests.post(
            'http://candidates.taxi.yandex.net/satisfy',
            json={'driver_ids': drivers, 'zone_id': 'moscow'},
        )
        satisfy.raise_for_status()
        satisfy_drivers = satisfy.json()['drivers']
        if _check_drivers(satisfy_drivers, park_id):
            break
    order_success = _try_make_order(client_maker, park_clid)
    assert not order_success


def test_disabled_provider(client_maker):
    park_clid = '111502'
    park_db_id = '744b7ef014054c08b756c75cc64cf300'

    order_success = _try_make_order(client_maker, park_clid)
    assert order_success

    response = log_requests.post(
        'http://candidates.taxi.yandex.net/profiles-snapshot',
        json={'parts': 1, 'part': 0},
    )
    response.raise_for_status()
    drivers = response.json()['drivers']

    client = pymongo.MongoClient('mongodb://mongo.taxi.yandex:27017/')
    client.dbparks.parks.update_one(
        {'_id': park_db_id},
        {
            '$set': {'provider_config.yandex': {'clid': None, 'apikey': None}},
            '$currentDate': {'modified_date': True},
        },
    )

    # candidates cache update
    for _ in utils.wait_for(120, SATISFY_ERROR_MSG, sleep=5):
        satisfy = log_requests.post(
            'http://candidates.taxi.yandex.net/satisfy',
            json={'driver_ids': drivers, 'zone_id': 'moscow'},
        )
        satisfy.raise_for_status()
        satisfy_drivers = satisfy.json()['drivers']
        if _check_drivers(satisfy_drivers, park_db_id):
            break

    order_success = _try_make_order(client_maker, park_clid)
    assert not order_success


def test_deactivated_park(client_maker):
    # in `volumes/bootstrap_db/db_parks.json`, park with clid '111503'
    # has mark "account.deactivated"
    park_clid = '111503'
    order_success = _try_make_order(client_maker, park_clid)
    assert not order_success
