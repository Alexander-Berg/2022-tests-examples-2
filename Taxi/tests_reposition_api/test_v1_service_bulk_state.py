# pylint: disable=C5521, C0103
import pytest

from .fbs import ServiceBulkStateFbs

fbs_handler = ServiceBulkStateFbs()


@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'active_session.sql',
    ],
)
async def test_single_driver(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/bulk_state',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'drivers': [
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'uuid'},
                ],
            },
        ),
    )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'states': [
            {
                'has_session': True,
                'active': True,
                'mode': 'poi',
                'session_id': 2003,
                'start_timestamp': 1539360311,
            },
        ],
    }


@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'active_session.sql',
    ],
)
async def test_multiple_drivers(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/bulk_state',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'drivers': [
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'uuid3'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': '888'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': 'uuid'},
                    {
                        'park_db_id': 'dbid_random',
                        'driver_profile_id': 'uuid_random',
                    },
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'states': [
            {
                'has_session': True,
                'active': True,
                'mode': 'poi',
                'submode': 'fast',
                'session_id': 2006,
                'start_timestamp': 1539360311,
            },
            {'has_session': False},
            {
                'has_session': True,
                'active': True,
                'mode': 'poi',
                'session_id': 2003,
                'start_timestamp': 1539360311,
            },
            {'has_session': False},
        ],
    }


@pytest.mark.now('2018-10-12T19:04:45+0300')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'zone_default.sql',
        'active_session.sql',
        'home_bonus.sql',
        'inactive_session.sql',
    ],
)
async def test_with_bonus(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/bulk_state',
        headers={'Content-Type': 'application/x-flatbuffers'},
        data=fbs_handler.build_request(
            {
                'drivers': [
                    {'park_db_id': '1488', 'driver_profile_id': 'driverSS'},
                    {'park_db_id': 'dbid777', 'driver_profile_id': '888'},
                ],
            },
        ),
    )
    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'states': [
            {
                'has_session': True,
                'mode': 'home',
                'session_id': 2012,
                'start_timestamp': 1539360225,
            },
            {
                'has_session': True,
                'active': True,
                'mode': 'home',
                'bonus': {'until': 1539361365540859000},
                'session_id': 2011,
                'start_timestamp': 1539360525,
            },
        ],
    }
