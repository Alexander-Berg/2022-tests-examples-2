import logging

import pytest
import requests

from taxi_tests import utils

logger = logging.getLogger(__file__)


# one driver park
CURRENT_PARK = '999013'
PARK_DB_ID = 'f6d9f7e55a9144239f706f15525ff2bb'
DESTINATION_POINT = [37.5, 55.8]
PARK_DRIVERS_IDS = [
    '7de5c84edb2d49b1983baf1dcf2d19bb',
    'd0db0b5e0bda4365895039f4221d98cf',
    '63fc7d9a5b404dfda300667e88fe3c4d',
]
DRIVER_ID = PARK_DRIVERS_IDS[0]
CACHE1_ERROR_MSG = 'Cache-stats has not been updated properly in first time'
CACHE2_ERROR_MSG = 'Cache-stats has not been updated properly in second time'
LON_ERROR_MSG = f'Tracker did not return \'lon\' in time'


@pytest.mark.skip(reason='EFFICIENCYDEV-7201')
def test_order_reposition(tracker, reposition, client_maker,
                          taximeter_control):
    create_home_request = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {
            'min': 500,
            'max': 100000,
        },
        'mode_type': 'ToPoint',
    }

    reposition.put('v1/settings/modes?mode=home', create_home_request)

    response = reposition.get('cache-stats')
    time_update = response['ModesCache']['last_update']
    for _ in utils.wait_for(150, CACHE1_ERROR_MSG):
        response = reposition.get('cache-stats')
        last_update = response['ModesCache']['last_update']
        if time_update != last_update:
            break

    for _ in utils.wait_for(150, LON_ERROR_MSG):
        try:
            response = tracker.get(
                'position?dbid=' + PARK_DB_ID + '&uuid=' + DRIVER_ID,
            )
            if response['lon']:
                break
        except requests.RequestException:
            logger.exception('Tracker request failed')

    start_request = {
        'driver_id': DRIVER_ID,
        'park_db_id': PARK_DB_ID,
        'mode': 'home',
        'point': {
            'address': 'home_address',
            'city': 'moscow',
            'point': DESTINATION_POINT,
        },
    }
    response = reposition.post('v1/reposition/start', start_request,
                               headers={'Accept-Language': 'ru-RU'})
    assert response['session_id']

    # make sure that reposition driver is cached by tracker
    response = tracker.get('cache-stats')
    time_update = response['RepositionIndexCache']['last_update']
    for _ in utils.wait_for(150, CACHE2_ERROR_MSG):
        response = tracker.get('cache-stats')
        last_update = response['RepositionIndexCache']['last_update']
        if time_update != last_update:
            break

    response = tracker.get(
        'position?dbid=' + PARK_DB_ID + '&uuid=' + DRIVER_ID,
    )
    point_start = [response['lon'], response['lat']]

    client = client_maker()
    client.init_phone(phone='random')
    client.launch()
    client.set_current_park(CURRENT_PARK)
    client.set_source(point_start)
    client.set_destinations([DESTINATION_POINT])
    client.order('manual_control-1')
    response = client.wait_for_order_status('driving')
    client.taximeter = taximeter_control.find_by_phone(
        response['driver']['phone'],
    )
    # make sure, that driver is the same
    info = client.taximeter.info()
    assert info['order']['driver_id'] in PARK_DRIVERS_IDS

    response = client.taxiontheway(cancel=True)
    assert response['status'] == 'cancelled'
