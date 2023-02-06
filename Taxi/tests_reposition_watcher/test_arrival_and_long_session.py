# pylint: disable=wrong-import-order, too-many-lines, import-only-modules
import datetime
import json

import pytest

from tests_reposition_watcher.utils import driver_statuses
from tests_reposition_watcher.utils import get_task_name
from tests_reposition_watcher.utils import select_named


# enable config
# enable exp
# add new sessions with shared checks
@pytest.mark.parametrize(
    'taximeter_status,air_dist_arrival',
    [
        ('order_free', False),
        ('order_busy', False),
        ('busy', False),
        ('free', False),
        ('free', True),
    ],
)
@pytest.mark.parametrize('config_checks', [True, False])
@pytest.mark.now('2018-11-26T12:00:00+00:00')
async def test_arrival_and_long_session(
        taximeter_status,
        air_dist_arrival,
        taxi_reposition_watcher,
        heatmap_storage_fixture,
        mockserver,
        pgsql,
        load,
        mock_maps_router,
        taxi_config,
        config_checks,
        driver_trackstory_v2_shorttracks,
):
    taxi_config.set_values(
        dict(
            REPOSITION_WATCHER_PGCLEANER={
                'query_timeout': 10,
                'chunk_size': 1000,
                'max_size': 10000 if config_checks else 0,
            },
        ),
    )
    queries = [
        load(
            'arrival_config_checks.sql'
            if config_checks
            else 'arrival_checks.sql',
        ),
    ]
    if air_dist_arrival:
        queries.append(load('update_arrival.sql'))
    pgsql['reposition_watcher'].apply_queries(queries)
    events = []
    rule_violations = []
    now = '2018-11-26T12:00:00+00:00'

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        return driver_statuses(
            json.loads(request.get_data())['driver_ids'], taximeter_status,
        )

    @mockserver.handler('/driver-protocol/service/reposition/rule-violations')
    def mock_rule_violation(request):
        request.get_data()
        return mockserver.make_response()

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/disable_session',
    )
    def mock_disable_session(request):
        req_dict = json.loads(request.get_data())
        if req_dict['session_id'] == 1502 or req_dict['session_id'] == 1508:
            reason_list = ['arrival', 'surge_arrival']
            reason_id = 0 if air_dist_arrival else 1
            if req_dict['session_id'] == 1508:
                reason_id = 1
            assert req_dict['reason'] == reason_list[reason_id]
        else:
            assert req_dict['reason'] == 'session_timeout'
        return {}

    @mockserver.json_handler('/reposition-api/v1/service/session/add_events')
    def _mock_add_event(request):
        events_ = json.loads(request.get_data())['events']

        for event in events_:
            events.append(event)

        return {'results': [{'has_failed': False} for _ in events_]}

    @mockserver.json_handler(
        '/reposition-api/v1/service/session/rule_violations',
    )
    def mock_reposition_rule_violations(request):
        rule_violations.append(json.loads(request.get_data()))
        return {}

    def build_shorttrack_response():
        responses = {
            'dbid777_uuid': {'lon': 30.0005, 'lat': 60.0005},
            'dbid777_uuid1': {'lon': 30.0006, 'lat': 60.0006},
            'dbid777_uuid2': {'lon': 30.0007, 'lat': 60.0007},
            'dbid777_888': {'lon': 30.0015, 'lat': 60.0025},
            '1488_driverSS2': {'lon': 30.0008, 'lat': 60.0008},
            'pg_park_pg_driver': {'lon': 30.0009, 'lat': 60.0009},
            'dbid_uuid1': {'lon': 30.0010, 'lat': 60.0010},
            'dbid_uuid2': {'lon': 30.0011, 'lat': 60.0011},
            'clid_uuid1': {'lon': 30.0002, 'lat': 60.0002},
            'dbid_uuid': {'lon': 30.0001, 'lat': 60.0002},
            'clid777_uuid': {'lon': 30.0002, 'lat': 60.0002},
        }

        if air_dist_arrival:
            responses['1488_driverSS'] = {'lon': 30.0001, 'lat': 60.0002}

        response = {'data': []}
        for key, value in responses.items():
            response['data'].append(
                {
                    'driver_id': key,
                    'adjusted': [
                        {
                            'timestamp': 1504893334,
                            'lon': 30.0,
                            'lat': 60.0,
                            'direction': 70,
                            'speed': 0,
                            'accuracy': 1.0,
                        },
                        {
                            'timestamp': 1504893333,
                            'lon': value['lon'],
                            'lat': value['lat'],
                            'direction': 70,
                            'speed': 0,
                            'accuracy': 1.0,
                        },
                    ],
                },
            )

        return response

    driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())

    @mockserver.json_handler('/driver-route-watcher/start-watch')
    def _mock_start_watch(request):
        return {}

    @mockserver.json_handler('/driver-route-responder/timeleft')
    def _mock_time_left(request):
        return mockserver.make_response(status=400, json={})

    @mockserver.json_handler('/driver-route-watcher/stop-watch')
    def _mock_stop_watch(request):
        return {}

    response = await taxi_reposition_watcher.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200
    stopped = taximeter_status == 'free'
    expected_disable_sessions = 0
    if stopped:
        expected_disable_sessions = 6 if air_dist_arrival else 5
    assert mock_disable_session.times_called == expected_disable_sessions
    assert driver_trackstory_v2_shorttracks.mock.times_called == 1

    assert _mock_start_watch.times_called == 3
    assert _mock_time_left.times_called == 0
    assert _mock_stop_watch.times_called == (1 if air_dist_arrival else 0)

    if stopped:
        violations_req = (await mock_rule_violation.wait_call())[
            'request'
        ].get_data()
        pushes = sorted(
            json.loads(violations_req)['violations'],
            key=lambda k: (k['type'], k['driver_uuid'], k['park_db_id']),
        )

        if air_dist_arrival:
            assert pushes == [
                {
                    'driver_uuid': 'driverSS',
                    'mode': 'home',
                    'park_db_id': '1488',
                    'type': 'arrival',
                    'urgency': 'final_warning',
                },
                {
                    'driver_uuid': 'uuid',
                    'mode': 'surge',
                    'park_db_id': 'dbid777',
                    'type': 'arrival',
                    'urgency': 'final_warning',
                },
                {
                    'driver_uuid': '888',
                    'mode': 'home',
                    'park_db_id': 'dbid777',
                    'type': 'long_session',
                    'urgency': 'final_warning',
                },
                {
                    'driver_uuid': 'driverSS2',
                    'mode': 'home',
                    'park_db_id': '1488',
                    'type': 'long_session',
                    'urgency': 'final_warning',
                },
                {
                    'driver_uuid': 'uuid2',
                    'mode': 'surge',
                    'park_db_id': 'dbid777',
                    'type': 'long_session',
                    'urgency': 'final_warning',
                },
            ]
            expected_events = [
                {
                    'session_id': 1501,
                    'type': 'session_timeout',
                    'occurred_at': now,
                },
                {
                    'session_id': 1502,
                    'type': (
                        'surge_arrived' if not air_dist_arrival else 'arrived'
                    ),
                    'occurred_at': now,
                },
                {
                    'session_id': 1503,
                    'type': 'session_timeout',
                    'occurred_at': now,
                },
                {
                    'occurred_at': now,
                    'type': (
                        'arrived' if not air_dist_arrival else 'surge_arrived'
                    ),
                    'session_id': 1508,
                },
                {
                    'session_id': 1509,
                    'type': 'session_timeout',
                    'occurred_at': now,
                },
                {
                    'session_id': 1510,
                    'type': 'session_timeout',
                    'occurred_at': now,
                },
            ]
            assert sorted(events, key=lambda x: x['session_id']) == sorted(
                expected_events, key=lambda x: x['session_id'],
            )
            assert _mock_add_event.times_called == 6
            assert mock_reposition_rule_violations.times_called == 7
            violations = sorted(rule_violations, key=lambda x: x['session_id'])
            air_dist_violations = []
            if air_dist_arrival:
                air_dist_violations = [
                    {
                        'type': 'arrived',
                        'valid_until': '2018-11-26T12:03:00+0000',
                    },
                ]
            expected_violations = [
                {
                    'session_id': 1501,
                    'violations': [
                        {
                            'type': 'session_timeout',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
                {
                    'session_id': 1502,
                    'violations': [
                        {
                            'type': 'arrived',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
                {
                    'session_id': 1503,
                    'violations': [
                        {
                            'type': 'session_timeout',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
                {
                    'session_id': 1507,
                    'violations': [
                        {
                            'type': 'session_timeout_warning',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
                {'session_id': 1508, 'violations': air_dist_violations},
                {
                    'session_id': 1509,
                    'violations': [
                        {
                            'type': 'session_timeout',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
                {
                    'session_id': 1510,
                    'violations': [
                        {
                            'type': 'session_timeout',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
            ]
            assert expected_violations == violations

    else:
        assert mock_rule_violation.times_called == (1 if stopped else 0)
        assert mock_reposition_rule_violations.times_called == 0
        assert rule_violations == []

    now = datetime.datetime(2018, 11, 26, 12, 0)
    left = [
        {
            'session_id': 1504,
            'drw_state': 'Disabled',
            'updated_at': now,
            'updating': None,
        },
        {
            'session_id': 1505,
            'drw_state': 'Active',
            'updated_at': now,
            'updating': None,
        },
        {
            'session_id': 1506,
            'drw_state': 'Active',
            'updated_at': now,
            'updating': None,
        },
        {
            'session_id': 1507,
            'drw_state': 'Disabled',
            'updated_at': now,
            'updating': None,
        },
    ]
    if not air_dist_arrival:
        left.append(
            {
                'session_id': 1502,
                'drw_state': 'Active',
                'updated_at': now,
                'updating': None,
            },
        )
    if taximeter_status != 'free':
        left.append(
            {
                'session_id': 1501,
                'drw_state': 'Disabled',
                'updated_at': now,
                'updating': None,
            },
        )
        left.append(
            {
                'session_id': 1503,
                'drw_state': 'Disabled',
                'updated_at': now,
                'updating': None,
            },
        )
        left.append(
            {
                'session_id': 1508,
                'drw_state': 'Disabled',
                'updated_at': now,
                'updating': None,
            },
        )
        left.append(
            {
                'session_id': 1509,
                'drw_state': 'Disabled',
                'updated_at': now,
                'updating': None,
            },
        )
        left.append(
            {
                'session_id': 1510,
                'drw_state': 'Disabled',
                'updated_at': now,
                'updating': None,
            },
        )

    right = select_named(
        """
    SELECT
      s.session_id, s.drw_state, r.updating, r.updated_at
    FROM state.sessions s
    INNER JOIN state.checks r ON s.session_id = r.session_id
    ORDER BY s.session_id
    """,
        pgsql['reposition_watcher'],
    )
    assert sorted(left, key=lambda x: x['session_id']) == sorted(
        right, key=lambda x: x['session_id'],
    )


@pytest.mark.parametrize(
    'taximeter_status,air_dist_arrival', [('free', False), ('free', True)],
)
@pytest.mark.parametrize('config_checks', [True, False])
@pytest.mark.now('2018-11-26T12:00:00+00:00')
async def test_drw_arrival_long_session(
        taximeter_status,
        air_dist_arrival,
        taxi_reposition_watcher,
        heatmap_storage_fixture,
        mockserver,
        pgsql,
        load,
        mock_maps_router,
        taxi_config,
        config_checks,
        driver_trackstory_v2_shorttracks,
):
    taxi_config.set_values(
        dict(
            REPOSITION_WATCHER_PGCLEANER={
                'query_timeout': 10,
                'chunk_size': 1000,
                'max_size': 10000 if config_checks else 0,
            },
        ),
    )
    queries = [
        load(
            'arrival_config_checks.sql'
            if config_checks
            else 'arrival_checks.sql',
        ),
        load('update_drw_state.sql'),
    ]
    if air_dist_arrival:
        queries.append(load('update_arrival.sql'))
    pgsql['reposition_watcher'].apply_queries(queries)
    events = []
    rule_violations = []
    now = '2018-11-26T12:00:00+00:00'

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        return driver_statuses(
            json.loads(request.get_data())['driver_ids'], taximeter_status,
        )

    @mockserver.handler('/driver-protocol/service/reposition/rule-violations')
    def mock_rule_violation(request):
        request.get_data()
        return mockserver.make_response()

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/disable_session',
    )
    def mock_disable_session(request):
        req_dict = json.loads(request.get_data())
        if req_dict['session_id'] in [1502, 1505, 1508]:
            reason_list = ['arrival', 'surge_arrival']
            reason_id = 0 if air_dist_arrival else 1
            if req_dict['session_id'] == 1508:
                reason_id = 1
            if req_dict['session_id'] == 1505:
                reason_id = 0
            assert req_dict['reason'] == reason_list[reason_id]
        else:
            assert req_dict['reason'] == 'session_timeout'
        return {}

    @mockserver.json_handler('/reposition-api/v1/service/session/add_events')
    def _mock_add_event(request):
        events_ = json.loads(request.get_data())['events']

        for event in events_:
            events.append(event)

        return {'results': [{'has_failed': False} for _ in events_]}

    @mockserver.json_handler(
        '/reposition-api/v1/service/session/rule_violations',
    )
    def mock_reposition_rule_violations(request):
        rule_violations.append(json.loads(request.get_data()))
        return {}

    def build_shorttrack_response():
        responses = {
            'dbid777_uuid': {'lon': 30.0005, 'lat': 60.0005},
            'dbid777_uuid1': {'lon': 30.0006, 'lat': 60.0006},
            'dbid777_uuid2': {'lon': 30.0007, 'lat': 60.0007},
            'dbid777_888': {'lon': 30.0015, 'lat': 60.0025},
            '1488_driverSS2': {'lon': 30.0008, 'lat': 60.0008},
            'pg_park_pg_driver': {'lon': 30.0009, 'lat': 60.0009},
            'dbid_uuid2': {'lon': 30.0011, 'lat': 60.0011},
            'clid_uuid1': {'lon': 30.0002, 'lat': 60.0002},
            'clid777_uuid': {'lon': 30.0002, 'lat': 60.0002},
        }

        response = {'data': []}
        for key, value in responses.items():
            response['data'].append(
                {
                    'driver_id': key,
                    'adjusted': [
                        {
                            'timestamp': 1504893334,
                            'lon': 30.0,
                            'lat': 60.0,
                            'direction': 70,
                            'speed': 0,
                            'accuracy': 1.0,
                        },
                        {
                            'timestamp': 1504893333,
                            'lon': value['lon'],
                            'lat': value['lat'],
                            'direction': 70,
                            'speed': 0,
                            'accuracy': 1.0,
                        },
                    ],
                },
            )

        return response

    driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())

    @mockserver.json_handler('/driver-route-watcher/start-watch')
    def _mock_start_watch(request):
        return {}

    @mockserver.json_handler('/driver-route-responder/timeleft')
    def _mock_time_left(request):
        args = json.loads(request.get_data())

        dbid = args['driver']['dbid']
        uuid = args['driver']['uuid']

        result = {
            'dbid_uuid': {
                'position': [30.0, 60.0],
                'destination': [30.0, 60.0],
                'time_left': 1800,
                'distance_left': 20,
                'tracking_type': 'route_tracking',
                'service_id': 'reposition-watcher',
                'etas': [],
            },
            'dbid_uuid1': {
                'position': [30.0, 60.0],
                'destination': [30.0, 60.0],
                'time_left': 180,
                'distance_left': 2000,
                'tracking_type': 'route_tracking',
                'service_id': 'reposition-watcher',
                'etas': [],
            },
            '1488_driverSS': {
                'position': [30.0, 60.0],
                'destination': [30.0, 60.0],
                'time_left': 1800,
                'distance_left': 20000,
                'tracking_type': 'route_tracking',
                'service_id': 'reposition-watcher',
                'etas': [],
            },
        }

        return result[f'{dbid}_{uuid}']

    @mockserver.json_handler('/driver-route-watcher/stop-watch')
    def _mock_stop_watch(request):
        return {}

    response = await taxi_reposition_watcher.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200
    stopped = taximeter_status == 'free'
    expected_disable_sessions = 0
    if stopped:
        expected_disable_sessions = 7 if air_dist_arrival else 6
    assert mock_disable_session.times_called == expected_disable_sessions
    assert driver_trackstory_v2_shorttracks.mock.times_called == 1

    assert _mock_start_watch.times_called == 0
    assert _mock_time_left.times_called == 3
    assert _mock_stop_watch.times_called == (2 if air_dist_arrival else 1)

    if stopped:
        violations_req = (await mock_rule_violation.wait_call())[
            'request'
        ].get_data()
        pushes = sorted(
            json.loads(violations_req)['violations'],
            key=lambda k: (k['type'], k['driver_uuid'], k['park_db_id']),
        )

        if air_dist_arrival:
            assert pushes == [
                {
                    'driver_uuid': 'driverSS',
                    'mode': 'home',
                    'park_db_id': '1488',
                    'type': 'arrival',
                    'urgency': 'final_warning',
                },
                {
                    'driver_uuid': 'uuid',
                    'mode': 'poi',
                    'park_db_id': 'dbid',
                    'type': 'arrival',
                    'urgency': 'final_warning',
                },
                {
                    'driver_uuid': 'uuid',
                    'mode': 'surge',
                    'park_db_id': 'dbid777',
                    'type': 'arrival',
                    'urgency': 'final_warning',
                },
                {
                    'driver_uuid': '888',
                    'mode': 'home',
                    'park_db_id': 'dbid777',
                    'type': 'long_session',
                    'urgency': 'final_warning',
                },
                {
                    'driver_uuid': 'driverSS2',
                    'mode': 'home',
                    'park_db_id': '1488',
                    'type': 'long_session',
                    'urgency': 'final_warning',
                },
                {
                    'driver_uuid': 'uuid2',
                    'mode': 'surge',
                    'park_db_id': 'dbid777',
                    'type': 'long_session',
                    'urgency': 'final_warning',
                },
            ]
            expected_events = [
                {
                    'session_id': 1501,
                    'type': 'session_timeout',
                    'occurred_at': now,
                },
                {
                    'session_id': 1502,
                    'type': (
                        'surge_arrived' if not air_dist_arrival else 'arrived'
                    ),
                    'occurred_at': now,
                },
                {
                    'session_id': 1503,
                    'type': 'session_timeout',
                    'occurred_at': now,
                },
                {'session_id': 1505, 'type': 'arrived', 'occurred_at': now},
                {
                    'occurred_at': now,
                    'type': (
                        'arrived' if not air_dist_arrival else 'surge_arrived'
                    ),
                    'session_id': 1508,
                },
                {
                    'session_id': 1509,
                    'type': 'session_timeout',
                    'occurred_at': now,
                },
                {
                    'session_id': 1510,
                    'type': 'session_timeout',
                    'occurred_at': now,
                },
            ]
            assert sorted(events, key=lambda x: x['session_id']) == sorted(
                expected_events, key=lambda x: x['session_id'],
            )
            assert _mock_add_event.times_called == 7
            assert mock_reposition_rule_violations.times_called == 8
            violations = sorted(rule_violations, key=lambda x: x['session_id'])
            air_dist_violations = []
            if air_dist_arrival:
                air_dist_violations = [
                    {
                        'type': 'arrived',
                        'valid_until': '2018-11-26T12:03:00+0000',
                    },
                ]
            expected_violations = [
                {
                    'session_id': 1501,
                    'violations': [
                        {
                            'type': 'session_timeout',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
                {
                    'session_id': 1502,
                    'violations': [
                        {
                            'type': 'arrived',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
                {
                    'session_id': 1503,
                    'violations': [
                        {
                            'type': 'session_timeout',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
                {
                    'session_id': 1505,
                    'violations': [
                        {
                            'type': 'arrived',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
                {
                    'session_id': 1507,
                    'violations': [
                        {
                            'type': 'session_timeout_warning',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
                {'session_id': 1508, 'violations': air_dist_violations},
                {
                    'session_id': 1509,
                    'violations': [
                        {
                            'type': 'session_timeout',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
                {
                    'session_id': 1510,
                    'violations': [
                        {
                            'type': 'session_timeout',
                            'valid_until': '2018-11-26T12:03:00+0000',
                        },
                    ],
                },
            ]
            assert expected_violations == violations

    else:
        assert mock_rule_violation.times_called == (1 if stopped else 0)
        assert mock_reposition_rule_violations.times_called == 0
        assert rule_violations == []

    now = datetime.datetime(2018, 11, 26, 12, 0)
    left = [
        {
            'session_id': 1504,
            'drw_state': 'Disabled',
            'updated_at': now,
            'updating': None,
        },
        {
            'session_id': 1506,
            'drw_state': 'Active',
            'updated_at': now,
            'updating': None,
        },
        {
            'session_id': 1507,
            'drw_state': 'Disabled',
            'updated_at': now,
            'updating': None,
        },
    ]
    if not air_dist_arrival:
        left.append(
            {
                'session_id': 1502,
                'drw_state': 'Active',
                'updated_at': now,
                'updating': None,
            },
        )
    if taximeter_status != 'free':
        left.append(
            {
                'session_id': 1501,
                'drw_state': 'Disabled',
                'updated_at': now,
                'updating': None,
            },
        )
        left.append(
            {
                'session_id': 1503,
                'drw_state': 'Disabled',
                'updated_at': now,
                'updating': None,
            },
        )
        left.append(
            {
                'session_id': 1508,
                'drw_state': 'Disabled',
                'updated_at': now,
                'updating': None,
            },
        )
        left.append(
            {
                'session_id': 1509,
                'drw_state': 'Disabled',
                'updated_at': now,
                'updating': None,
            },
        )
        left.append(
            {
                'session_id': 1510,
                'drw_state': 'Disabled',
                'updated_at': now,
                'updating': None,
            },
        )

    right = select_named(
        """
    SELECT
      s.session_id, s.drw_state, r.updating, r.updated_at
    FROM state.sessions s
    INNER JOIN state.checks r ON s.session_id = r.session_id
    ORDER BY s.session_id
    """,
        pgsql['reposition_watcher'],
    )
    assert sorted(left, key=lambda x: x['session_id']) == sorted(
        right, key=lambda x: x['session_id'],
    )


@pytest.mark.now('2018-11-26T12:00:00+00:00')
async def test_antisurge_arrival(
        taxi_reposition_watcher,
        heatmap_storage_fixture,
        mockserver,
        pgsql,
        load,
        mock_maps_router,
        now,
        driver_trackstory_v2_shorttracks,
):
    # default surge_value is set in code to 1.0
    queries = [load('update_antisurge_arrival.sql')]
    pgsql['reposition_watcher'].apply_queries(queries)
    events = []
    rule_violations = []
    now_str = '2018-11-26T12:00:00+00:00'

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        return driver_statuses(
            json.loads(request.get_data())['driver_ids'], 'free',
        )

    @mockserver.handler('/driver-protocol/service/reposition/rule-violations')
    def mock_rule_violation(request):
        request.get_data()
        return mockserver.make_response()

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/disable_session',
    )
    def mock_disable_session(request):
        req_dict = json.loads(request.get_data())
        assert req_dict['reason'] == 'antisurge_arrival'
        return {}

    @mockserver.json_handler('/reposition-api/v1/service/session/add_events')
    def _mock_add_event(request):
        events_ = json.loads(request.get_data())['events']

        for event in events_:
            events.append(event)

        return {'results': [{'has_failed': False} for _ in events_]}

    @mockserver.json_handler(
        '/reposition-api/v1/service/session/rule_violations',
    )
    def mock_reposition_rule_violations(request):
        rule_violations.append(json.loads(request.get_data()))
        return {}

    def build_shorttrack_response():
        responses = {
            'dbid777_888': {'lon': 30.1, 'lat': 60.1},
            'dbid777_999': {'lon': 30.1, 'lat': 60.1},
        }

        response = {'data': []}
        for key, value in responses.items():
            response['data'].append(
                {
                    'driver_id': key,
                    'adjusted': [
                        {
                            'timestamp': 1504893334,
                            'lon': 30.0,
                            'lat': 60.0,
                            'direction': 70,
                            'speed': 0,
                            'accuracy': 1.0,
                        },
                        {
                            'timestamp': 1504893333,
                            'lon': value['lon'],
                            'lat': value['lat'],
                            'direction': 70,
                            'speed': 0,
                            'accuracy': 1.0,
                        },
                    ],
                },
            )

        return response

    driver_trackstory_v2_shorttracks.set_data(build_shorttrack_response())

    @mockserver.json_handler('/driver-route-watcher/start-watch')
    def _mock_start_watch(request):
        return {}

    @mockserver.json_handler('/driver-route-responder/timeleft')
    def _mock_time_left(request):
        return mockserver.make_response(status=400, json={})

    @mockserver.json_handler('/driver-route-watcher/stop-watch')
    def _mock_stop_watch(request):
        return {}

    response = await taxi_reposition_watcher.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200
    expected_disable_sessions = 1
    assert mock_disable_session.times_called == expected_disable_sessions
    assert driver_trackstory_v2_shorttracks.mock.times_called == 1

    violations_req = (await mock_rule_violation.wait_call())[
        'request'
    ].get_data()
    pushes = sorted(
        json.loads(violations_req)['violations'],
        key=lambda k: (k['type'], k['driver_uuid'], k['park_db_id']),
    )
    assert pushes == [
        {
            'driver_uuid': '888',
            'mode': 'home',
            'park_db_id': 'dbid777',
            'type': 'anti_surge_arrival',
            'urgency': 'final_warning',
        },
    ]

    expected_events = [
        {
            'session_id': 1531,
            'type': 'arrived_by_antisurge',
            'occurred_at': now_str,
        },
    ]
    assert sorted(events, key=lambda x: x['session_id']) == sorted(
        expected_events, key=lambda x: x['session_id'],
    )
    assert _mock_add_event.times_called == 1

    assert mock_reposition_rule_violations.times_called == 1
    violations = sorted(rule_violations, key=lambda x: x['session_id'])
    expected_violations = [
        {
            'session_id': 1531,
            'violations': [
                {
                    'type': 'anti_surge_arrival',
                    'valid_until': '2018-11-26T12:03:00+0000',
                },
            ],
        },
    ]
    assert expected_violations == violations

    left = [
        {
            'session_id': 1532,
            'drw_state': 'Disabled',
            'updated_at': now,
            'updating': None,
        },
    ]

    right = select_named(
        """
    SELECT
      s.session_id, s.drw_state, r.updating, r.updated_at
    FROM state.sessions s
    INNER JOIN state.checks r ON s.session_id = r.session_id
    ORDER BY s.session_id
    """,
        pgsql['reposition_watcher'],
    )
    assert left == right
