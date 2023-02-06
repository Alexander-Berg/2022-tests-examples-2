# pylint: disable=C5521, W0621
# flake8: noqa E501
import datetime
import re

import pytest
import pytz

from . import yql_services_fixture
from .conftest import USER_AGENT
from .utils import select_named
from .yql_services_fixture import local_yql_services  # noqa: F401


HOURS_THRESHOLD = datetime.timedelta(hours=24)
NOW = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=pytz.timezone('UTC'))
DATE_FORMAT = '%Y-%m-%d'
ISO_FORMAT = '%FT%T'
TTL = (NOW + datetime.timedelta(days=1)).strftime(ISO_FORMAT)
HISTORY_PATH_PREFIX = (
    '//home/taxi/testing/features/reposition/sessions_history'
)
TABLE = 'home/taxi/testing/features/reposition/sessions_history/tablename'
OAUTH = 'OAuth taxi-robot-token'
YT_CHUNK_SIZE = 1000
TEST_SHARED_ID = 'XL15AAlSshlfAw44s4E1lUtwCkmt2cKTumKON1zwgqQ='
SESSIONS_PATH = (
    '//home/logfeller/logs/taxi/testing/'
    'taxi-testing-reposition-api-yandex-taxi-reposition-api-session-log'
)
FEEDBACKS_PATH = (
    '//home/logfeller/logs/taxi/testing/'
    'taxi-testing-reposition-api-yandex-taxi-reposition-api-feedback-log'
)
MATCH_ORDERS_PATH = (
    '//home/logfeller/logs'
    '/taxi-test-reposition-matcher-match-orders-drivers-json-log'
)

YT_DATA = [
    {
        'driver_id': (
            '1a04d6b1039d48e6a7d9f4865dc48b05_743ae89114d8c74b4ccdfb9089806c70'
        ),
        'session_id': 'pQJ0dNMp83zbLOvE',
        'session_start': '2020-01-01 13:39:23.082973+0000',
        'session_end': '2020-01-01 18:39:23.082973+0000',
        'reposition_mode': 'poi_coms',
        'reposition_submode': None,
        'completed': False,
        'bonus_until': None,
        'start_point_lon': 30.410732,
        'start_point_lat': 59.968151,
        'point_location_lon': 30.4362,
        'point_location_lat': 59.9546,
        'point_area_radius': None,
        'score': None,
        'score_comment': None,
        'score_choices': None,
        'events': '[{}]',
        'orders': '[]',
    },
    {
        'driver_id': (
            '5c1b5e310e9043e9acb0bad154e94680_d1a7427ea7d345a69d0cbc35e73e5f66'
        ),
        'session_id': 'qQK9b6320ZndEvYn',
        'session_start': '2020-01-01 13:39:23.082973+0000',
        'session_end': '2020-01-01 15:39:23.082973+0000',
        'reposition_mode': 'SuperSurge',
        'reposition_submode': None,
        'completed': False,
        'bonus_until': None,
        'start_point_lon': 37.349714999999996,
        'start_point_lat': 55.858351,
        'point_location_lon': 37.443302154541016,
        'point_location_lat': 55.849727630615234,
        'point_area_radius': None,
        'score': None,
        'score_comment': None,
        'score_choices': None,
        'events': '[{"OrderStarted":"2020-01-01T22:57:57.053455+0000"}]',
        'orders': '["43e9acb0bad154e94680d1a","9879f9fb9c4c941376a85"]',
    },
    {
        'driver_id': (
            '9b5a0b02051242d9a310f7e920b09f1e_0b4c9879f9fb9c4c941376a854b13e82'
        ),
        'session_id': 'gW4QbY10MgKbzqM5',
        'session_start': '2020-01-01 13:39:23.082973+0000',
        'session_end': '2020-01-01 20:39:23.082973+0000',
        'reposition_mode': 'poi',
        'reposition_submode': 'fast',
        'completed': False,
        'bonus_until': None,
        'offer_id': 'offer-AaAaaaA1AzAa',
        'start_point_lon': 37.600311,
        'start_point_lat': 55.530798,
        'point_location_lon': 37.57014846801758,
        'point_location_lat': 55.56767654418945,
        'point_area_radius': None,
        'score': None,
        'score_comment': None,
        'score_choices': None,
        'events': '[{"ClientStop":"2020-01-01T22:57:55.261139+0000"}]',
        'orders': '["510d6af41ad8562d38d2c"]',
    },
    {
        'driver_id': (
            '3e6b8510d6af41ad8562d3c08d2cc999_b4faac7c8fa8664cdbc95b81b33b4135'
        ),
        'session_id': 'Yq9wdLKnPowbjPXg',
        'session_start': '2020-01-01 18:39:23.082973+0000',
        'session_end': '2020-01-01 20:39:23.082973+0000',
        'reposition_mode': 'SuperSurge',
        'reposition_submode': None,
        'completed': False,
        'bonus_until': None,
        'start_point_lon': 30.246207,
        'start_point_lat': 59.984382999999994,
        'point_location_lon': 30.378877639770508,
        'point_location_lat': 59.98126983642578,
        'point_area_radius': None,
        'score': None,
        'score_comment': None,
        'score_choices': None,
        'events': '[{"ClientStop":"2020-01-01T22:57:37.398906+0000"}]',
        'orders': '["03e9acb0bad153e94680d1a","187949fb9c4c941376a85"]',
    },
    {
        'driver_id': (
            '6dfe722e29c845d9ba993d54be94e84a_27723ab5bb1942f098e61c823606bc7c'
        ),
        'session_id': 'gK4oeEz6ZAla0Byx',
        'session_start': '2020-01-01 12:39:23.082973+0000',
        'session_end': '2020-01-01 13:39:23.082973+0000',
        'reposition_mode': 'SuperSurge',
        'reposition_submode': None,
        'completed': True,
        'bonus_until': '2020-01-01 13:59:23.082973+0000',
        'start_point_lon': 37.605728,
        'start_point_lat': 54.101684,
        'point_location_lon': 37.4943,
        'point_location_lat': 54.0226,
        'point_area_radius': None,
        'score': None,
        'score_comment': None,
        'score_choices': None,
        'events': (
            '[{"Arrived":"2020-01-01T13:39:23.082973+0000"},'
            '{"ClientStop":"2020-01-01T13:40:11.71302+0000"}]'
        ),
        'orders': '[]',
    },
    {
        'driver_id': (
            '6dfe722e29c845d9ba993d54be94e84a_27723ab5bb1942f098e61c823606bc7c'
        ),
        'session_id': '5xYRdGBQYD5bDzOW',
        'session_start': '2020-01-01 18:39:23.082973+0000',
        'session_end': '2020-01-01 20:39:23.082973+0000',
        'reposition_mode': 'home',
        'reposition_submode': None,
        'completed': True,
        'bonus_until': None,
        'start_point_lon': 37.605728,
        'start_point_lat': 54.101684,
        'point_location_lon': 37.4943,
        'point_location_lat': 54.0226,
        'point_area_radius': None,
        'score': None,
        'score_comment': None,
        'score_choices': None,
        'events': (
            '[{"Arrived":"2020-01-01T18:39:23.082973+0000"},'
            '{"ClientStop":"2020-01-01T18:40:11.71302+0000"}]'
        ),
        'orders': '[]',
    },
]


@pytest.mark.pgsql('reposition', files=['sessions_history_operations.sql'])
async def test_poll(
        taxi_reposition_api,
        yt_client,
        local_yql_services,  # noqa: F811
        yt_apply_force,
):

    local_yql_services.add_status_response('RUNNING')
    local_yql_services.add_results_response(
        {
            'id': yql_services_fixture.OPERATION_ID,
            'status': 'RUNNING',
            'data': [{'Write': [{}]}],
            'updatedAt': '2019-06-18T07:04:50.528Z',
        },
    )

    operation_id = yql_services_fixture.OPERATION_ID
    response = await taxi_reposition_api.get(
        f'/v1/admin/sessions/history/?operation_id={operation_id}',
    )

    assert local_yql_services.times_called['status'] == 1
    assert local_yql_services.times_called['results'] == 0
    assert local_yql_services.times_called['results_data'] == 0

    assert response.status_code == 202
    assert response.json() == {}


def concat_yt_tables_range(request_type, path, from_date, to_date):
    if request_type == 'day':
        return (
            f'concatYtTablesRange(\'{path}/1d\', '
            f'\'{from_date}\', \'{to_date}\')'
        )

    return f'concatYtTablesRange(\'{path}/1h\')'


def select_sessions_pattern(
        detail_level,
        request_type,
        park_id,
        driver_profile_id,
        from_date,
        to_date,
        from_time,
        to_time,
):
    if detail_level == 'sessions':
        return f"""
            SELECT driver_id, ses.session_id AS session_id, session_start,
                session_end, reposition_mode, reposition_submode, completed,
                bonus_until, offer_id,

                YPathDouble(start_point, '/lon') as start_point_lon,
                YPathDouble(start_point, '/lat') as start_point_lat,

                YPathDouble(point_location, '/lon') as point_location_lon,
                YPathDouble(point_location, '/lat') as point_location_lat,

                point_area_radius,
                score,
                comment AS score_comment,
                '[' || arrayStringConcat(
                    arrayMap(
                    x -> '"' || x || '"',
                    YPathExtract(choices, '', 'Array(String)')
                    ), ','
                ) || ']' AS score_choices,
                '[{{'||arrayStringConcat(
                    arrayMap(
                    x -> '"' || x.1 || '":"' || x.2 || '"',
                    arrayFlatten(
                        arrayMap(
                        x -> YSONExtractKeysAndValues(
                            COALESCE(YPathRaw(COALESCE(events, '[]'),
                            '/'||toString(x)), ''),
                            'String'
                        ),
                        range(0, YSONLength(COALESCE(events, '[]')))
                        )
                    )
                    ), '}},{{'
                ) || '}}]' AS events,
                timestamp
            FROM {concat_yt_tables_range(
                request_type, SESSIONS_PATH, from_date, to_date)} AS ses
            ANY LEFT JOIN (
                SELECT
                    session_id,
                    score,
                    comment,
                    choices
                FROM {concat_yt_tables_range(
                    request_type, FEEDBACKS_PATH, from_date, to_date)}
            ) AS scr
            ON scr.session_id = ses.session_id
            WHERE
                timestamp > '{from_time}' AND
                timestamp < '{to_time}' AND
                driver_id = '{park_id}_{driver_profile_id}'
            """

    return f"""
        SELECT driver_id, ses.session_id AS session_id, session_start,
            session_end, reposition_mode, reposition_submode, completed,
            bonus_until, offer_id,

            YPathDouble(start_point, '/lon') as start_point_lon,
            YPathDouble(start_point, '/lat') as start_point_lat,

            YPathDouble(point_location, '/lon') as point_location_lon,
            YPathDouble(point_location, '/lat') as point_location_lat,

            point_area_radius,
            score,
            comment AS score_comment,
            '[' || arrayStringConcat(
                arrayMap(
                x -> '"' || x || '"',
                YPathExtract(choices, '', 'Array(String)')
                ), ','
            ) || ']' AS score_choices,
            '[{{'||arrayStringConcat(
                arrayMap(
                x -> '"' || x.1 || '":"' || x.2 || '"',
                arrayFlatten(
                    arrayMap(
                    x -> YSONExtractKeysAndValues(
                        COALESCE(YPathRaw(COALESCE(events, '[]'),
                        '/'||toString(x)), ''),
                        'String'
                    ),
                    range(0, YSONLength(COALESCE(events, '[]')))
                    )
                )
                ), '}},{{'
            ) || '}}]' AS events,
            '[' || orders || ']' AS orders,
            timestamp
        FROM {concat_yt_tables_range(
            request_type, SESSIONS_PATH, from_date, to_date)} AS ses
        ANY LEFT JOIN (
            SELECT
                session_id,
                score,
                comment,
                choices
            FROM {concat_yt_tables_range(
                request_type, FEEDBACKS_PATH, from_date, to_date)}
        ) AS scr
        ON scr.session_id = ses.session_id
        ANY LEFT JOIN (
            SELECT
            session_id,
            '"' || arrayStringConcat(groupUniqArray(order_id), '","')
            || '"' AS orders
            FROM {concat_yt_tables_range(
                request_type, MATCH_ORDERS_PATH, from_date, to_date)}
            WHERE
                en_route = 1 AND
                driver_id = '{park_id}_{driver_profile_id}'
            GROUP BY
                session_id
        ) AS match
        ON match.session_id = ses.session_id
        WHERE
            timestamp > '{from_time}' AND
            timestamp < '{to_time}' AND
            driver_id = '{park_id}_{driver_profile_id}'
        """


def select_sessions(
        detail_level,
        request_type,
        park_id,
        driver_profile_id,
        from_date,
        to_date,
        from_time,
        to_time,
):
    if request_type in ('day', 'hour'):
        return f"""
            USE chyt.hahn/robot-reposition-alias;
            CREATE TABLE `{HISTORY_PATH_PREFIX}/tablename`
            engine = YtTable('{{expiration_time="{TTL}"}}') AS
            {select_sessions_pattern(
            detail_level,
            request_type,
            park_id,
            driver_profile_id,
            from_date,
            to_date,
            from_time,
            to_time,
            )}
            ORDER BY
                timestamp DESC,
                session_id DESC;
            """

    return f"""
        USE chyt.hahn/robot-reposition-alias;
        CREATE TABLE `{HISTORY_PATH_PREFIX}/tablename`
        engine = YtTable('{{expiration_time="{TTL}"}}') AS
        SELECT * FROM
            (
                (
                    {select_sessions_pattern(detail_level, 'day',
                    park_id, driver_profile_id, from_date, to_date,
                    from_time, to_time)}
                )
                UNION ALL
                (
                    {select_sessions_pattern(detail_level, 'hour',
                    park_id, driver_profile_id, from_date, to_date,
                    from_time, to_time)}
                )
            )
        ORDER BY
            timestamp DESC,
            session_id DESC;
    """


@pytest.mark.yt(
    schemas=[
        {
            'path': '//' + TABLE,
            'attributes': {
                'schema': [
                    {'name': 'driver_id', 'type': 'string'},
                    {'name': 'session_id', 'type': 'string'},
                    {'name': 'session_start', 'type': 'string'},
                    {'name': 'session_end', 'type': 'string'},
                    {'name': 'reposition_mode', 'type': 'string'},
                    {'name': 'reposition_submode', 'type': 'string'},
                    {'name': 'completed', 'type': 'boolean'},
                    {'name': 'bonus_until', 'type': 'string'},
                    {'name': 'offer_id', 'type': 'string'},
                    {'name': 'start_point_lon', 'type': 'double'},
                    {'name': 'start_point_lat', 'type': 'double'},
                    {'name': 'point_location_lon', 'type': 'double'},
                    {'name': 'point_location_lat', 'type': 'double'},
                    {'name': 'point_area_radius', 'type': 'double'},
                    {'name': 'score', 'type': 'uint64'},
                    {'name': 'score_comment', 'type': 'string'},
                    {'name': 'score_choices', 'type': 'string'},
                    {'name': 'events', 'type': 'string'},
                    {'name': 'orders', 'type': 'string'},
                ],
            },
        },
    ],
    static_table_data=[{'path': '//' + TABLE, 'values': YT_DATA}],
)
@pytest.mark.pgsql('reposition', files=['sessions_history_operations.sql'])
@pytest.mark.parametrize('result', [YT_DATA])
@pytest.mark.parametrize('failed', [True, False])
@pytest.mark.parametrize('orders', [True, False])
async def test_get(
        taxi_reposition_api,
        yt_client,
        local_yql_services,  # noqa: F811
        result,  # noqa: F811
        failed,
        pgsql,
        orders,
        yt_apply_force,
        mockserver,
):
    @mockserver.json_handler('/yql/api/v2/operations/operation_id/results')
    def _operation_status(request):
        return {
            'id': 'operation_id_0',
            'errors': [{'message': 'Bad operation'}],
        }

    if not orders:
        cursor = pgsql['reposition'].conn.cursor()
        cursor.execute(
            'UPDATE state.sessions_history_operations '
            'SET detail_level=\'Sessions\'',
        )
    status = 'COMPLETED' if not failed else 'ERROR'
    local_yql_services.add_status_response(status)
    local_yql_services.add_results_response(
        {
            'id': yql_services_fixture.OPERATION_ID,
            'status': status,
            'data': [{'Write': [{}]}],
            'updatedAt': '2019-06-18T07:04:50.528Z',
        },
    )

    operation_id = yql_services_fixture.OPERATION_ID
    response = await taxi_reposition_api.get(
        f'/v1/admin/sessions/history/?operation_id={operation_id}',
    )

    assert local_yql_services.times_called['status'] == 1
    assert local_yql_services.times_called['results'] == 0
    assert local_yql_services.times_called['results_data'] == 0

    if failed:
        assert response.status_code == 500
        assert {
            'code': '500',
            'message': (
                'Bad YQL Operation operation_id, '
                'error: {"id":"operation_id_0",'
                '"errors":[{"message":"Bad operation"}]}'
            ),
        } == response.json()
        return

    assert response.status_code == 200

    expected_response = {
        'sessions': [
            {
                'orders': [],
                'events': [],
                'driver_profile_id': '743ae89114d8c74b4ccdfb9089806c70',
                'is_completed': False,
                'mode': 'poi_coms',
                'park_id': '1a04d6b1039d48e6a7d9f4865dc48b05',
                'point_location': [30.4362, 59.9546],
                'session_end': '2020-01-01 18:39:23.082973+0000',
                'session_id': 'pQJ0dNMp83zbLOvE',
                'session_start': '2020-01-01 13:39:23.082973+0000',
                'start_point': [30.410732, 59.968151],
                'feedback': {},
            },
            {
                'orders': ['43e9acb0bad154e94680d1a', '9879f9fb9c4c941376a85'],
                'events': [
                    {
                        'event': 'OrderStarted',
                        'occurred_at': '2020-01-01T22:57:57.053455+0000',
                    },
                ],
                'driver_profile_id': 'd1a7427ea7d345a69d0cbc35e73e5f66',
                'is_completed': False,
                'mode': 'SuperSurge',
                'park_id': '5c1b5e310e9043e9acb0bad154e94680',
                'point_location': [37.443302154541016, 55.849727630615234],
                'session_end': '2020-01-01 15:39:23.082973+0000',
                'session_id': 'qQK9b6320ZndEvYn',
                'session_start': '2020-01-01 13:39:23.082973+0000',
                'start_point': [37.349714999999996, 55.858351],
                'feedback': {},
            },
            {
                'orders': ['510d6af41ad8562d38d2c'],
                'events': [
                    {
                        'event': 'ClientStop',
                        'occurred_at': '2020-01-01T22:57:55.261139+0000',
                    },
                ],
                'driver_profile_id': '0b4c9879f9fb9c4c941376a854b13e82',
                'is_completed': False,
                'mode': 'poi',
                'park_id': '9b5a0b02051242d9a310f7e920b09f1e',
                'point_location': [37.57014846801758, 55.56767654418945],
                'session_end': '2020-01-01 20:39:23.082973+0000',
                'session_id': 'gW4QbY10MgKbzqM5',
                'offer_id': 'offer-AaAaaaA1AzAa',
                'session_start': '2020-01-01 13:39:23.082973+0000',
                'start_point': [37.600311, 55.530798],
                'submode': 'fast',
                'feedback': {},
            },
            {
                'orders': ['03e9acb0bad153e94680d1a', '187949fb9c4c941376a85'],
                'events': [
                    {
                        'event': 'ClientStop',
                        'occurred_at': '2020-01-01T22:57:37.398906+0000',
                    },
                ],
                'driver_profile_id': 'b4faac7c8fa8664cdbc95b81b33b4135',
                'is_completed': False,
                'mode': 'SuperSurge',
                'park_id': '3e6b8510d6af41ad8562d3c08d2cc999',
                'point_location': [30.378877639770508, 59.98126983642578],
                'session_end': '2020-01-01 20:39:23.082973+0000',
                'session_id': 'Yq9wdLKnPowbjPXg',
                'session_start': '2020-01-01 18:39:23.082973+0000',
                'start_point': [30.246207, 59.984382999999994],
                'feedback': {},
            },
            {
                'orders': [],
                'bonus_until': '2020-01-01 13:59:23.082973+0000',
                'events': [
                    {
                        'event': 'Arrived',
                        'occurred_at': '2020-01-01T13:39:23.082973+0000',
                    },
                    {
                        'event': 'ClientStop',
                        'occurred_at': '2020-01-01T13:40:11.71302+0000',
                    },
                ],
                'driver_profile_id': '27723ab5bb1942f098e61c823606bc7c',
                'is_completed': True,
                'mode': 'SuperSurge',
                'point_location': [37.4943, 54.0226],
                'park_id': '6dfe722e29c845d9ba993d54be94e84a',
                'session_id': 'gK4oeEz6ZAla0Byx',
                'session_start': '2020-01-01 12:39:23.082973+0000',
                'session_end': '2020-01-01 13:39:23.082973+0000',
                'start_point': [37.605728, 54.101684],
                'feedback': {},
            },
            {
                'orders': [],
                'events': [
                    {
                        'event': 'Arrived',
                        'occurred_at': '2020-01-01T18:39:23.082973+0000',
                    },
                    {
                        'event': 'ClientStop',
                        'occurred_at': '2020-01-01T18:40:11.71302+0000',
                    },
                ],
                'driver_profile_id': '27723ab5bb1942f098e61c823606bc7c',
                'is_completed': True,
                'mode': 'home',
                'park_id': '6dfe722e29c845d9ba993d54be94e84a',
                'point_location': [37.4943, 54.0226],
                'session_end': '2020-01-01 20:39:23.082973+0000',
                'session_id': '5xYRdGBQYD5bDzOW',
                'session_start': '2020-01-01 18:39:23.082973+0000',
                'start_point': [37.605728, 54.101684],
                'feedback': {},
            },
        ],
    }
    response_json = response.json()
    if orders:
        for ses in expected_response['sessions']:
            ses['orders'] = sorted(ses['orders'])
        for ses in response_json['sessions']:
            ses['orders'] = sorted(ses['orders'])
    else:
        for ses in expected_response['sessions']:
            ses.pop('orders', None)

    assert response_json == expected_response


@pytest.mark.nofilldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'from_time, to_time, request_type',
    [
        (
            NOW - datetime.timedelta(days=2),
            NOW + datetime.timedelta(days=10),
            'day-hour',
        ),
        (
            NOW - datetime.timedelta(days=2),
            NOW + datetime.timedelta(days=1),
            'day-hour',
        ),
        (
            NOW - datetime.timedelta(days=3),
            NOW - datetime.timedelta(days=2),
            'day',
        ),
        (NOW - datetime.timedelta(days=2), None, 'day-hour'),
        (NOW - datetime.timedelta(hours=2), None, 'hour'),
    ],
)
@pytest.mark.parametrize(
    'detail_level', [None, 'sessions', 'sessions-with-orders'],
)
@pytest.mark.yt(
    schemas=[
        {'path': f'{SESSIONS_PATH}/1d/2019-12-30', 'attributes': {}},
        {'path': f'{MATCH_ORDERS_PATH}/1d/2019-12-30', 'attributes': {}},
    ],
)
async def test_retrieve(
        taxi_reposition_api,
        yt_client,
        from_time,
        to_time,
        request_type,
        detail_level,
        mockserver,
        pgsql,
):
    park_id = '1488'
    driver_profile_id = 'driverSS'

    @mockserver.json_handler('/yql/api/v2/operations/operation_id_0/share_id')
    def _share_handler(request):
        assert request.headers['User-Agent'] == USER_AGENT
        assert request.headers['Authorization'] == OAUTH

        # add commas
        return mockserver.make_response('\"' + TEST_SHARED_ID + '\"', 200)

    @mockserver.json_handler('/yql/api/v2/operations')
    def handler(request):
        assert request.headers['User-Agent'] == USER_AGENT
        assert request.headers['Authorization'] == OAUTH

        requested_data = request.json
        query = re.sub(
            r'sessions_history/[^`]*`',
            'sessions_history/tablename`',
            requested_data['content'].replace('\n', '').replace(' ', ''),
        )

        from_date = from_time.strftime(DATE_FORMAT)
        from_iso = from_time.strftime(ISO_FORMAT)
        if to_time is None:
            to_date = NOW.strftime(DATE_FORMAT)
            to_iso = NOW.strftime(ISO_FORMAT)
        else:
            to_date = to_time.strftime(DATE_FORMAT)
            to_iso = to_time.strftime(ISO_FORMAT)
        expected_query = select_sessions(
            detail_level,
            request_type,
            park_id,
            driver_profile_id,
            from_date,
            to_date,
            from_iso,
            to_iso,
        )
        expected_query = expected_query.replace('\n', '').replace(' ', '')

        assert expected_query == query

        return {
            'id': f'operation_id_{handler.times_called}',
            'status': 'RUNNING',
        }

    data = {
        'from': from_time.isoformat(),
        'park_id': '1488',
        'driver_profile_id': 'driverSS',
        'detail_level': detail_level,
    }
    if to_time is not None:
        data['to'] = to_time.isoformat()

    response = await taxi_reposition_api.post(
        '/v1/admin/sessions/history/request', data,
    )
    assert response.status_code == 200

    assert yt_client.exists(HISTORY_PATH_PREFIX)

    response = response.json()
    operation_id = response['operation_id']
    assert operation_id == 'operation_id_0'

    rows = select_named(
        'SELECT operation_id, path, share_id, created '
        'FROM state.sessions_history_operations',
        pgsql['reposition'],
    )
    assert len(rows) == 1
    rows[0].pop('path', None)
    assert rows == [
        {
            'operation_id': 'operation_id_0',
            'share_id': TEST_SHARED_ID,
            'created': datetime.datetime(2020, 1, 1, 0, 0),
        },
    ]


@pytest.mark.now(NOW.isoformat())
@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'data',
    [
        (
            {
                'park_id': '1488',
                'driver_profile_id': 'driverSS',
                'from': 'not timestamp',
            }
        ),
        (
            {
                'park_id': '1488',
                'driver_profile_id': 'driverSS',
                'from': NOW.isoformat(),
                'to': '2019-02-04T23:59:59+0000',
            }
        ),
        (
            {
                'park_id': '1488',
                'driver_profile_id': 'driverSS',
                'from': NOW.isoformat(),
                'to': NOW.isoformat(),
            }
        ),
        ({}),
    ],
)
async def test_admin_bad_history_search_bad_requests(
        taxi_reposition_api, data, pgsql,
):
    response = await taxi_reposition_api.post(
        '/v1/admin/sessions/history/request', data,
    )
    assert response.status_code == 400
    rows = select_named(
        'SELECT operation_id, path, created '
        'FROM state.sessions_history_operations',
        pgsql['reposition'],
    )
    assert not rows


@pytest.mark.now(NOW.isoformat())
async def test_failed_operation(taxi_reposition_api, mockserver):
    @mockserver.json_handler('/yql/api/v2/operations')
    def mock_operations(request):
        return {'id': f'operation_id', 'status': 'ERROR'}

    @mockserver.json_handler('/yql/api/v2/operations/operation_id/results')
    def _operation_status(request):
        return {'id': 'operation_id', 'errors': [{'message': 'Bad operation'}]}

    data = {
        'from': (NOW - datetime.timedelta(hours=2)).isoformat(),
        'park_id': '1488',
        'driver_profile_id': 'driverSS',
    }

    response = await taxi_reposition_api.post(
        '/v1/admin/sessions/history/request', data,
    )
    assert response.status_code == 500
    assert mock_operations.times_called == 1
