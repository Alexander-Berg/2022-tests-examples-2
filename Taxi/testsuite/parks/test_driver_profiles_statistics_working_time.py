import json

import pytest

from taxi_tests.utils import ordered_object


def err(error_message):
    return {'error': {'text': error_message}}


@pytest.mark.now('2018-12-21T12:00:00.000000Z')
@pytest.mark.parametrize(
    'request_json,status_code,response_json',
    [
        ({}, 400, err('query must be present')),
        (
            {
                'query': {
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.park must be present'),
        ),
        (
            {'query': {'park': {'id': 'xXx'}}},
            400,
            err('query.time_interval must be present'),
        ),
        (
            {
                'query': {
                    'park': {'driver_profile_id': ['yyy']},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.park.id must be present'),
        ),
        (
            {
                'query': {
                    'park': {'id': 123, 'driver_profile_id': ['yyy']},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.park.id must be a non-empty utf-8 string without BOM'),
        ),
        (
            {
                'query': {
                    'park': {'id': '', 'driver_profile_id': ['yyy']},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.park.id must be a non-empty utf-8 string without BOM'),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx'},
                    'time_interval': {
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.time_interval.start_at must be present'),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx'},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.time_interval.end_at must be present'),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx'},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                    },
                },
            },
            400,
            err('query.time_interval.subintervals_duration must be present'),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx', 'driver_profile_id': 'yyy'},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.park.driver_profile_id must be an array'),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx'},
                    'time_interval': {
                        'start_at': '2018-12-05T14:01:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.time_interval.start_at must contain whole UTC hours'),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx'},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:00:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            400,
            err('query.time_interval.end_at must contain whole UTC hours'),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx'},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 3599,
                    },
                },
            },
            400,
            err(
                'query.time_interval.subintervals_duration'
                ' must be greater than or equal to 1 hour (in seconds)',
            ),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx'},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 604801,
                    },
                },
            },
            400,
            err(
                'query.time_interval.subintervals_duration'
                ' must be less than or equal to 168 hours (in seconds)',
            ),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx'},
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 4500,
                    },
                },
            },
            400,
            err(
                'query.time_interval.subintervals_duration'
                ' must be multiple of 1 hours (in seconds)',
            ),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx'},
                    'time_interval': {
                        'start_at': '2018-12-06T14:00:00+0000',
                        'end_at': '2018-12-06T14:00:00+0000',
                        'subintervals_duration': 3600,
                    },
                },
            },
            400,
            err('query.time_interval must contain at least one subinterval'),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx'},
                    'time_interval': {
                        'start_at': '2018-12-01T14:00:00+0300',
                        'end_at': '2018-12-19T11:45:00+0045',
                        'subintervals_duration': 604800,
                    },
                },
            },
            400,
            err(
                'query.time_interval must contain '
                'whole number of subintervals',
            ),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx'},
                    'time_interval': {
                        'start_at': '2018-12-20T23:00:00+0000',
                        'end_at': '2018-12-22T11:00:00+0000',
                        'subintervals_duration': 7200,
                    },
                },
            },
            400,
            err(
                'query.time_interval'
                ' must not contain subintervals exceed current time',
            ),
        ),
        (
            {
                'query': {
                    'park': {'id': 'xXx'},
                    'time_interval': {
                        'start_at': '2018-12-20T23:00:00+0000',
                        'end_at': '2018-12-21T13:00:00+0000',
                        'subintervals_duration': 3600,
                    },
                },
            },
            400,
            err(
                'query.time_interval'
                ' must not contain subintervals exceed current time',
            ),
        ),
        (
            {
                'query': {
                    'park': {
                        'id': 'xXx',
                        'driver_profile_id': ['anton', 'todua'],
                    },
                    'time_interval': {
                        'start_at': '2018-12-05T14:00:00+0300',
                        'end_at': '2018-12-06T17:45:00+0045',
                        'subintervals_duration': 21600,
                    },
                },
            },
            200,
            {
                'time_interval': {
                    'end_at': '2018-12-06T17:00:00+0000',
                    'start_at': '2018-12-05T11:00:00+0000',
                    'subintervals_count': 5,
                    'subintervals_duration': 21600,
                },
                'working_time': [
                    {
                        'driver_profile_id': 'anton',
                        'park_id': 'xXx',
                        'subintervals_working_time': [0, 0, 0, 222, 111],
                    },
                ],
            },
        ),
        (
            {
                'query': {
                    'park': {
                        'id': 'xXx',
                        'driver_profile_id': ['anton', 'todua'],
                    },
                    'time_interval': {
                        'start_at': '2018-12-01T13:00:00+0700',
                        'end_at': '2018-12-15T13:00:00+0700',
                        'subintervals_duration': 604800,
                    },
                },
            },
            200,
            {
                'time_interval': {
                    'start_at': '2018-12-01T06:00:00+0000',
                    'end_at': '2018-12-15T06:00:00+0000',
                    'subintervals_duration': 604800,
                    'subintervals_count': 2,
                },
                'working_time': [
                    {
                        'park_id': 'xXx',
                        'driver_profile_id': 'anton',
                        'subintervals_working_time': [333, 0],
                    },
                ],
            },
        ),
        (
            {
                'query': {
                    'park': {
                        'id': 'yYy',
                        'driver_profile_id': ['anton', 'unknown'],
                    },
                    'time_interval': {
                        'start_at': '2018-12-03T03:00:00+0300',
                        'end_at': '2018-12-10T03:00:00+0300',
                        'subintervals_duration': 86400,
                    },
                },
            },
            200,
            {
                'time_interval': {
                    'start_at': '2018-12-03T00:00:00+0000',
                    'end_at': '2018-12-10T00:00:00+0000',
                    'subintervals_duration': 86400,
                    'subintervals_count': 7,
                },
                'working_time': [
                    {
                        'park_id': 'yYy',
                        'driver_profile_id': 'anton',
                        'subintervals_working_time': [
                            3333,
                            2222,
                            0,
                            0,
                            0,
                            0,
                            10000,
                        ],
                    },
                ],
            },
        ),
        (
            {
                'query': {
                    'park': {'id': 'yYy'},
                    'time_interval': {
                        'start_at': '2018-12-05T12:00:00+0300',
                        'end_at': '2018-12-10T00:00:00+0300',
                        'subintervals_duration': 3600,
                    },
                },
            },
            200,
            {
                'time_interval': {
                    'start_at': '2018-12-05T09:00:00+0000',
                    'end_at': '2018-12-09T21:00:00+0000',
                    'subintervals_duration': 3600,
                    'subintervals_count': 108,
                },
                'working_time': [
                    {
                        'park_id': 'yYy',
                        'driver_profile_id': 'anton',
                        'subintervals_working_time': [
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            3600,
                            3600,
                            2800,
                            0,
                            0,
                            0,
                        ],
                    },
                    {
                        'park_id': 'yYy',
                        'driver_profile_id': 'todua',
                        'subintervals_working_time': [
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            333,
                            777,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                        ],
                    },
                ],
            },
        ),
    ],
)
def test_post(taxi_parks, request_json, status_code, response_json):
    response = taxi_parks.post(
        '/driver-profiles/statistics/working-time',
        data=json.dumps(request_json),
    )

    assert response.status_code == status_code
    ordered_object.assert_eq(response.json(), response_json, ['working_time'])
