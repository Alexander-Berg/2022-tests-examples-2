import pytest

from taxi_tests import utils


DRIVER_ID = '7de5c84edb2d49b1983baf1dcf2d19bb'
PARK_DB_ID = 'f6d9f7e55a9144239f706f15525ff2bb'
DBID_UUID = PARK_DB_ID + '_' + DRIVER_ID
DESTINATION_POINT = [37.5, 55.8]
ZONE = '__default__'


@pytest.mark.skip(reason='flaps')
def test_check_tags_reposition(
        reposition, tags,
):
    wait_for_cache = utils.wait_for_cache

    headers = {'Accept-Language': 'ru-RU'}
    tags.put('/v1/providers/items',
             json={'services': ['reposition'],
                   'description': 'reposition service'},
             params={'id': 'reposition'})

    create_home_request = {
        'backend_only': False,
        'display_rules': [],
        'allowed_distance': {
            'min': 500,
            'max': 100000,
        },
        'mode_type': 'ToPoint',
    }

    reposition.put('v1/settings/zones/item?zone={}'.format(ZONE), json={})
    reposition.put('v1/settings/modes?mode=home', create_home_request)
    wait_for_cache(['ModesCache', 'ZonesCache'], reposition, sleep_for=2.5)

    session_tags = sorted(['reposition_home', 'reposition_start_by_udid'])
    completed_tags = ['tag_completed']
    request = {
        'session': {'tags': session_tags},
        'completed': {'tags': completed_tags},
    }
    reposition.put('/v1/settings/zones/tags?zone={}&mode=home'.format(ZONE),
                   json=request)
    wait_for_cache('TagsCache', reposition)

    response = reposition.post(
        'v1/reposition/start',
        json={
            'park_db_id': PARK_DB_ID,
            'driver_id': DRIVER_ID,
            'mode': 'home',
            'point': {
                'address': 'home_address',
                'city': 'moscow',
                'point': DESTINATION_POINT,
            },
        },
        headers=headers,
    )
    assert response['session_id']
    wait_for_cache('TagsCache', reposition)

    resp_tags = tags.post('/v1/match',
                          json={'entities': [
                              {'id': DBID_UUID, 'type': 'dbid_uuid'},
                          ]},
                          headers=headers)
    assert sorted(resp_tags['entities'][0]['tags']) == session_tags

    response = reposition.post(
        'v1/reposition/stop',
        json={
            'park_db_id': PARK_DB_ID,
            'driver_id': DRIVER_ID,
        },
        headers=headers,
    )
    assert response == {}
    wait_for_cache('TagsCache', reposition)

    resp_tags = tags.post('/v1/match',
                          json={'entities': [
                              {'id': DBID_UUID, 'type': 'dbid_uuid'},
                          ]},
                          headers=headers)
    assert not resp_tags['entities'][0]['tags']
