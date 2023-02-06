import os

import pytest

from tests_scooters_ops_relocation import utils


HANDLER = '/scooters-ops-relocation/v1/events/create'

DBEVENTS = [
    {
        'id': 'event1_outcome',
        'type': 'outcome',
        'occured_at': '2021-01-01T13:25:11+03:00',
        'location': (35, 51),
    },
    {
        'id': 'event1_income',
        'type': 'income',
        'occured_at': '2021-01-01T14:25:11+03:00',
        'location': (35, 53),
    },
]

API_EVENT_0 = {
    'type': 'outcome',
    'occured_at': '2021-01-01T10:25:11+00:00',
    'location': {'lon': 35, 'lat': 51},
}

API_EVENT_1 = {
    'type': 'income',
    'occured_at': '2021-01-01T11:25:11+00:00',
    'location': {'lon': 35, 'lat': 53},
}

BEFORE_EVENTS_TS = '2021-01-01T10:00:00+0000'


@pytest.mark.skipif(
    os.getenv('IS_TEAMCITY'),
    reason='I haven\'t been able to install postgis yet',
)
@pytest.mark.parametrize(
    'geometry, from_tp, allowed_types, expected_events',
    [
        pytest.param(
            {'tl': {'lon': 34, 'lat': 50}, 'br': {'lon': 36, 'lat': 52}},
            BEFORE_EVENTS_TS,
            None,
            [API_EVENT_0],
            id='bbox_search',
        ),
        pytest.param(
            {
                'outer': [
                    {'lon': 34, 'lat': 52},
                    {'lon': 36, 'lat': 52},
                    {'lon': 36, 'lat': 55},
                    {'lon': 34, 'lat': 55},
                    {'lon': 34, 'lat': 52},
                ],
            },
            BEFORE_EVENTS_TS,
            None,
            [API_EVENT_1],
            id='polygon_search',
        ),
        pytest.param(
            {'center': {'lon': 35, 'lat': 50}, 'radius_m': 200000},
            BEFORE_EVENTS_TS,
            None,
            [API_EVENT_0],
            id='circle_search',
        ),
        pytest.param(
            {'tl': {'lon': 34, 'lat': 50}, 'br': {'lon': 36, 'lat': 54}},
            '2021-01-01T11:00:00+00:00',
            None,
            [API_EVENT_1],
            id='time_bound',
        ),
        pytest.param(
            {'tl': {'lon': 34, 'lat': 50}, 'br': {'lon': 36, 'lat': 54}},
            BEFORE_EVENTS_TS,
            ['outcome'],
            [API_EVENT_0],
            id='filter_types',
        ),
    ],
)
async def test_fetch_events(
        taxi_scooters_ops_relocation,
        pgsql,
        geometry,
        from_tp,
        allowed_types,
        expected_events,
):
    for event in DBEVENTS:
        utils.add_event(pgsql, event)

    resp = await taxi_scooters_ops_relocation.post(
        '/scooters-ops-relocation/v1/events/fetch',
        {
            'geometry': geometry,
            'from_tp': from_tp,
            'allowed_types': allowed_types,
        },
    )

    assert resp.status_code == 200, resp.text
    assert (
        sorted(resp.json()['events'], key=lambda x: x['occured_at'])
        == expected_events
    )
