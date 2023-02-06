# pylint: disable=C5521, C0103
import pytest

from .fbs import ServiceSessionsFbs

fbs_handler = ServiceSessionsFbs()


@pytest.mark.now('2017-11-19T16:47:54.721')
async def test_empty(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/sessions', params={},
    )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {'sessions': []}


@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'sessions.sql'])
@pytest.mark.now('2017-11-19T16:47:54.721')
async def test_simple(taxi_reposition_api):
    response = await taxi_reposition_api.post(
        '/v1/service/sessions', params={},
    )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'sessions': [
            {
                'driver_id': 'd1',
                'end': None,
                'mode': 'home',
                'park_db_id': 'dbid777',
                'start': 1511110074,
                'submode': '',
            },
            {
                'driver_id': 'd2',
                'end': None,
                'mode': 'home',
                'park_db_id': 'dbid777',
                'start': 1511109774,
                'submode': '',
            },
            {
                'driver_id': 'd3',
                'end': 1511110674,
                'mode': 'surge',
                'park_db_id': 'dbid777',
                'start': 1511109474,
                'submode': '',
            },
        ],
    }


@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'sessions.sql'])
@pytest.mark.parametrize('idx,end_time', [(0, 0), (1, 20 * 60), (2, 40 * 60)])
@pytest.mark.now('2017-11-19T17:07:54.721')
async def test_with_end_time(taxi_reposition_api, idx, end_time):
    response = await taxi_reposition_api.post(
        '/v1/service/sessions',
        params={'time_since_completed_offer': end_time},
    )

    expected_response = [
        {
            'driver_id': 'd1',
            'end': None,
            'mode': 'home',
            'park_db_id': 'dbid777',
            'start': 1511110074,
            'submode': '',
        },
        {
            'driver_id': 'd2',
            'end': None,
            'mode': 'home',
            'park_db_id': 'dbid777',
            'start': 1511109774,
            'submode': '',
        },
    ]
    if idx > 0:
        expected_response.append(
            {
                'driver_id': 'd3',
                'end': 1511110674,
                'mode': 'surge',
                'park_db_id': 'dbid777',
                'start': 1511109474,
                'submode': '',
            },
        )
    if idx > 1:
        expected_response.append(
            {
                'driver_id': 'd5',
                'end': 1511108874,
                'mode': 'surge',
                'park_db_id': 'dbid777',
                'start': 1511108274,
                'submode': '',
            },
        )

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'sessions': expected_response,
    }
