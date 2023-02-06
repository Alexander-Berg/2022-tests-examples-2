# pylint: disable=import-error
import pytest

from tests_dispatch_airport import common


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue.sql', 'driver_events.sql'],
)
@pytest.mark.now('2018-10-12T19:04:45+0300')
@pytest.mark.parametrize(
    'case',
    [
        {'is_valid': False, 'status': 'failedtoassign'},
        {'is_valid': True, 'status': 'pending'},
        {
            'is_valid': False,
            'session': {
                'is_active': True,
                'is_completed': False,
                'mode': 'Airport',
                'point': [0, 0],
            },
            'status': 'driving',
        },
        {
            'is_valid': True,
            'session': {
                'is_active': True,
                'is_completed': False,
                'mode': 'Airport',
                'point': [0, 0],
            },
            'status': 'driving',
        },
        {
            'is_valid': True,
            'session': {
                'is_active': True,
                'is_completed': True,
                'mode': 'Airport',
                'point': [0, 0],
                'bonus': {'until': '2018-10-12T19:02:45+0300'},
            },
            'status': 'waiting',
        },
        {
            'is_valid': True,
            'session': {
                'is_active': True,
                'is_completed': True,
                'mode': 'Airport',
                'point': [0, 0],
                'bonus': {'until': '2018-10-12T19:06:45+0300'},
            },
            'status': 'waiting',
        },
        {
            'is_valid': True,
            'session': {
                'is_active': False,
                'is_completed': True,
                'mode': 'Airport',
                'point': [0, 0],
            },
            'status': 'waiting',
        },
        {
            'is_valid': False,
            'session': {
                'is_active': True,
                'is_completed': True,
                'mode': 'Airport',
                'point': [0, 0],
            },
            'status': 'waiting',
        },
        {
            'is_valid': False,
            'session': {
                'is_active': False,
                'is_completed': True,
                'mode': 'Airport',
                'point': [0, 0],
            },
            'status': 'waiting',
        },
        {
            'is_valid': True,
            'session': {
                'is_active': False,
                'is_completed': False,
                'mode': 'Airport',
                'point': [0, 0],
                'end_ts': '2018-10-12T19:04:16+0300',
            },
            'status': 'driving',
        },
        {
            'is_valid': True,
            'session': {
                'is_active': False,
                'is_completed': False,
                'mode': 'Airport',
                'point': [0, 0],
                'end_ts': '2018-10-12T19:04:15+0300',
            },
            'status': 'cancelled',
        },
    ],
)
async def test_relocate_status(taxi_dispatch_airport, mockserver, case):
    @mockserver.json_handler('reposition-api/v1/service/offer_state')
    def _reposition_state(request):
        assert request.json == {'offer_id': 'reposition-id'}
        return {'is_valid': case['is_valid'], 'session': case.get('session')}

    drivers = [
        # driver not found
        ('dbid_uuid1', None),
        # no udid, no event, notification area
        ('dbid_uuid2', 'car2'),
        # no udid, no event, waiting area
        ('dbid_uuid3', 'car3'),
        # no udid, event, notification area
        ('dbid_uuid4', 'car4'),
        # no udid, event, waiting area
        ('dbid_uuid5', 'car5'),
        # udid, no event, notification area
        ('dbid_uuid6', 'car6'),
        # udid, no event, waiting area
        ('dbid_uuid7', 'car7'),
        # udid, event, notification area
        ('dbid_uuid8', 'car8'),
        # udid, event (not suitable target_airport_id), waiting area
        ('dbid_uuid9', 'car9'),
    ]
    for (driver_id, car_id) in drivers:
        resp = await taxi_dispatch_airport.post(
            '/v1/relocate/status',
            {'session_id': driver_id + '_reposition-id'},
            headers=common.DEFAULT_DISPATCH_AIRPORT_HEADER,
        )
        etalon = {'status': case['status']}
        if car_id is not None:
            etalon['car_number'] = car_id
        assert resp.json() == etalon


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue.sql', 'driver_events.sql'],
)
@pytest.mark.now('2018-10-12T19:04:45+0300')
@pytest.mark.parametrize('is_active', [True, False])
async def test_relocate_status_expose_waiting_status(
        taxi_dispatch_airport, mockserver, is_active,
):
    @mockserver.json_handler('reposition-api/v1/service/offer_state')
    def _reposition_state(request):
        assert request.json == {'offer_id': 'reposition-id'}
        return {
            'is_valid': True,
            'session': {
                'is_active': is_active,
                'is_completed': False,
                'mode': 'Airport',
                'point': [0, 0],
            },
        }

    resp = await taxi_dispatch_airport.post(
        '/v1/relocate/status',
        {'session_id': 'dbid_uuid10_reposition-id'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_HEADER,
    )
    r_json = resp.json()
    assert r_json == {'status': 'waiting', 'car_number': 'car10'}


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
async def test_relocate_status_bad_id(taxi_dispatch_airport):
    resp = await taxi_dispatch_airport.post(
        '/v1/relocate/status',
        {'session_id': 'dbid-uuid1_reposition-id'},
        headers=common.DEFAULT_DISPATCH_AIRPORT_HEADER,
    )

    assert resp.json() == {
        'code': 'MALFORMED_OFFER_ID',
        'message': 'Malformed offer id',
    }
