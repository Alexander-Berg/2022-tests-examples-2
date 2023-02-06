# pylint: disable=C5521, C0103
import datetime

import pytest
import pytz

from .fbs import DriversIndexFbs

fbs_handler = DriversIndexFbs()


@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'sessions.sql'])
@pytest.mark.now('2017-11-19T16:47:54.721')
async def test_clean(taxi_reposition_api):
    response = await taxi_reposition_api.post('/v2/drivers/index', params={})

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'revision': 6,
        'has_more': False,
        'drivers': [
            {
                'driver_id': 'd1',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': True,
                'mode_name': 'home',
                'bonus_until': None,
                'destination_point': [1.0, 2.0],
            },
            {
                'driver_id': 'd2',
                'park_db_id': 'dbid777',
                'can_take_orders': False,
                'can_take_orders_when_busy': False,
                'reposition_check_required': True,
                'mode_name': 'home',
                'bonus_until': None,
                'destination_point': [1.0, 2.0],
            },
            {
                'driver_id': 'd3',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': False,
                'mode_name': 'home',
                'bonus_until': None,
                'destination_point': [1.0, 2.0],
            },
            {
                'driver_id': 'd5',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': True,
                'mode_name': 'surge',
                'bonus_until': datetime.datetime(
                    2017, 11, 19, 17, 7, 54, tzinfo=pytz.timezone('UTC'),
                ),
                'destination_point': [1.0, 2.0],
            },
        ],
    }


@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'sessions.sql'])
@pytest.mark.now('2017-11-19T16:47:54.721')
async def test_clean_chunked(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v2/drivers/index', params={'limit': 1},
    )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'revision': 2,
        'has_more': True,
        'drivers': [
            {
                'driver_id': 'd1',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': True,
                'mode_name': 'home',
                'bonus_until': None,
                'destination_point': [1.0, 2.0],
            },
        ],
    }

    response = await taxi_reposition_api.post(
        '/v2/drivers/index', params={'from': 2, 'limit': 2},
    )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'revision': 4,
        'has_more': True,
        'drivers': [
            {
                'driver_id': 'd2',
                'park_db_id': 'dbid777',
                'can_take_orders': False,
                'can_take_orders_when_busy': False,
                'reposition_check_required': True,
                'mode_name': 'home',
                'bonus_until': None,
                'destination_point': [1.0, 2.0],
            },
            {
                'driver_id': 'd3',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': False,
                'mode_name': 'home',
                'bonus_until': None,
                'destination_point': [1.0, 2.0],
            },
        ],
    }

    response = await taxi_reposition_api.post(
        '/v2/drivers/index', params={'from': 4, 'limit': 2},
    )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'revision': 6,
        'has_more': False,
        'drivers': [
            {
                'driver_id': 'd5',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': True,
                'mode_name': 'surge',
                'bonus_until': datetime.datetime(
                    2017, 11, 19, 17, 7, 54, tzinfo=pytz.timezone('UTC'),
                ),
                'destination_point': [1.0, 2.0],
            },
        ],
    }


@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'sessions.sql'])
@pytest.mark.now('2017-11-19T16:47:54.721')
async def test_diff(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v2/drivers/index', params={'from': 11},
    )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'revision': 6,
        'has_more': False,
        'drivers': [
            {
                'driver_id': 'd1',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': True,
                'mode_name': 'home',
                'bonus_until': None,
                'destination_point': [1.0, 2.0],
            },
            {
                'driver_id': 'd2',
                'park_db_id': 'dbid777',
                'can_take_orders': False,
                'can_take_orders_when_busy': False,
                'reposition_check_required': True,
                'mode_name': 'home',
                'bonus_until': None,
                'destination_point': [1.0, 2.0],
            },
            {
                'driver_id': 'd3',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': False,
                'mode_name': 'home',
                'bonus_until': None,
                'destination_point': [1.0, 2.0],
            },
            {
                'driver_id': 'd4',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': False,
                'mode_name': 'home',
                'bonus_until': None,
                'destination_point': [1.0, 2.0],
            },
            {
                'driver_id': 'd5',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': True,
                'mode_name': 'surge',
                'bonus_until': datetime.datetime(
                    2017, 11, 19, 17, 7, 54, tzinfo=pytz.timezone('UTC'),
                ),
                'destination_point': [1.0, 2.0],
            },
        ],
    }


@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'sessions.sql'])
@pytest.mark.now('2017-11-19T16:47:54.721')
async def test_empty_diff(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v2/drivers/index', params={'from': 16},
    )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'revision': 6,
        'has_more': False,
        'drivers': [],
    }


@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'sessions.sql'])
@pytest.mark.now('2017-11-19T16:47:54.721')
async def test_overlap(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v2/drivers/index', params={'from': 13},
    )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'revision': 6,
        'has_more': False,
        'drivers': [
            {
                'driver_id': 'd3',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': False,
                'mode_name': 'home',
                'bonus_until': None,
                'destination_point': [1.0, 2.0],
            },
            {
                'driver_id': 'd4',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': False,
                'mode_name': 'home',
                'bonus_until': None,
                'destination_point': [1.0, 2.0],
            },
            {
                'driver_id': 'd5',
                'park_db_id': 'dbid777',
                'can_take_orders': True,
                'can_take_orders_when_busy': False,
                'reposition_check_required': True,
                'mode_name': 'surge',
                'bonus_until': datetime.datetime(
                    2017, 11, 19, 17, 7, 54, tzinfo=pytz.timezone('UTC'),
                ),
                'destination_point': [1.0, 2.0],
            },
        ],
    }


@pytest.mark.now('2017-11-19T16:47:54.721')
async def test_empty_table(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v2/drivers/index', params={'limit': 1},
    )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'revision': 0,
        'has_more': False,
        'drivers': [],
    }
