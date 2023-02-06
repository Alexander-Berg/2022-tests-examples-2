# pylint: disable=wrong-import-order, too-many-lines, import-only-modules
import datetime
import json

import pytest

from tests_reposition_watcher.utils import driver_status
from tests_reposition_watcher.utils import get_task_name
from tests_reposition_watcher.utils import select_named


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'failed_checks,urgency,is_drw_fallback',
    [
        (0, 'first_warning', False),
        (1, 'last_warning', True),
        (2, 'final_warning', False),
    ],
)
@pytest.mark.now('2018-11-26T08:00:00+0000')
async def test_route_check(
        failed_checks,
        urgency,
        is_drw_fallback,
        taxi_reposition_watcher,
        mockserver,
        pgsql,
        load,
        mock_maps_router,
        statistics,
        driver_trackstory_v2_shorttracks,
):
    queries = [load('test.sql'), load('route.sql')]
    if not is_drw_fallback:
        queries.append(load('update_drw_state.sql'))
    pgsql['reposition_watcher'].apply_queries(queries)
    violations = 2
    total_checks = 3
    cursor = pgsql['reposition_watcher'].conn.cursor()
    cursor.execute(
        'UPDATE state.route '
        'SET violations_count='
        + str(violations)
        + ', last_checks_count='
        + str(total_checks)
        + ', failed_checks_count='
        + str(failed_checks),
    )
    events = []
    rule_violations = []

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        return driver_status('free')

    @mockserver.handler('/driver-protocol/service/reposition/rule-violations')
    def mock_rule_violation(request):
        request.get_data()
        return mockserver.make_response()

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/disable_session',
    )
    def mock_disable_session(request):
        req_dict = json.loads(request.get_data())
        assert req_dict['reason'] == 'route'
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
            'dbid777_999': {'lon': 37.631680, 'lat': 55.736567},
            'dbid888_777': {'lon': 30.631680, 'lat': 59.736567},
        }

        response = {'data': []}
        for key, value in responses.items():
            response['data'].append(
                {
                    'driver_id': key,
                    'adjusted': [
                        {
                            'timestamp': 1504893333,
                            'lon': value['lon'],
                            'lat': value['lat'],
                            'direction': 70,
                            'speed': 0,
                            'accuracy': 1.0,
                        },
                        {
                            'timestamp': 1504893334,
                            'lon': 30.0,
                            'lat': 60.0,
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

    if is_drw_fallback:
        statistics.fallbacks = ['reposition.drw_time_lefts.fallback']
        await taxi_reposition_watcher.invalidate_caches()

    async with statistics.capture(taxi_reposition_watcher) as capture:
        response = await taxi_reposition_watcher.post(
            'service/cron', json={'task_name': get_task_name()},
        )
    assert response.status_code == 200

    if urgency == 'final_warning':
        assert mock_disable_session.times_called == 1
    assert driver_trackstory_v2_shorttracks.mock.times_called == 1

    assert _mock_start_watch.times_called == 0
    assert _mock_time_left.times_called == (3 if not is_drw_fallback else 0)
    assert _mock_stop_watch.times_called == 0

    assert 'reposition.drw_time_lefts.success' not in capture.statistics
    if not is_drw_fallback:
        assert 'reposition.drw_time_lefts.error' in capture.statistics
        assert capture.statistics['reposition.drw_time_lefts.error'] == 3

    violations_req = (await mock_rule_violation.wait_call())[
        'request'
    ].get_data()
    pushes = sorted(
        json.loads(violations_req)['violations'],
        key=lambda k: (k['type'], k['driver_uuid'], k['park_db_id']),
    )

    assert pushes == [
        {
            'driver_uuid': '999',
            'mode': 'home',
            'park_db_id': 'dbid777',
            'type': 'route',
            'urgency': urgency,
        },
    ]

    now = '2018-11-26T08:00:00+00:00'
    if urgency == 'final_warning':
        assert events == [
            {'occurred_at': now, 'type': 'route', 'session_id': 1511},
        ]
        assert _mock_add_event.times_called == 1

    expected_violations = [
        {
            'session_id': 1511,
            'violations': [
                {
                    'type': (
                        'route'
                        if urgency == 'final_warning'
                        else 'route_warning'
                    ),
                    'valid_until': '2018-11-26T08:03:00+0000',
                },
            ],
        },
    ]
    assert (
        sorted(rule_violations, key=lambda x: x['session_id'])
        == expected_violations
    )

    assert mock_rule_violation.times_called == 0
    assert mock_reposition_rule_violations.times_called == 1
    now = datetime.datetime(2018, 11, 26, 8, 0)

    left = [
        {'session_id': 1501, 'updated_at': now, 'updating': None},
        {'session_id': 1502, 'updated_at': now, 'updating': None},
        {'session_id': 1503, 'updated_at': now, 'updating': None},
        {'session_id': 1504, 'updated_at': now, 'updating': None},
        {'session_id': 1505, 'updated_at': now, 'updating': None},
        {'session_id': 1506, 'updated_at': now, 'updating': None},
        {'session_id': 1507, 'updated_at': now, 'updating': None},
        {'session_id': 1508, 'updated_at': now, 'updating': None},
        {'session_id': 1509, 'updated_at': now, 'updating': None},
        {'session_id': 1510, 'updated_at': now, 'updating': None},
    ]
    if urgency != 'final_warning':
        left.append({'session_id': 1511, 'updated_at': now, 'updating': None})

    right = select_named(
        """
    SELECT
      s.session_id, r.updating, r.updated_at
    FROM state.sessions s
    INNER JOIN state.checks r ON s.session_id = r.session_id
    ORDER BY s.session_id
    """,
        pgsql['reposition_watcher'],
    )
    assert left == right

    if urgency != 'final_warning':
        right = select_named(
            """
                     select s.violations_count, s.last_check from state.route s
                     inner join state.checks r ON
                     r.route_state_id = s.state_id
                     where state_id = 101
                     """,
            pgsql['reposition_watcher'],
        )
        assert [
            {'last_check': now, 'violations_count': violations + 1},
        ] == right


@pytest.mark.now('2020-06-25T13:00:00+0000')
@pytest.mark.pgsql('reposition_watcher', files=['drw.sql'])
async def test_drw(
        taxi_reposition_watcher,
        mockserver,
        pgsql,
        load,
        testpoint,
        statistics,
        driver_trackstory_v2_shorttracks,
):
    events = []
    rule_violations = []

    @mockserver.json_handler('/candidates/profiles')
    def _mock_profiles(request):
        return driver_status('free')

    @mockserver.handler('/driver-protocol/service/reposition/rule-violations')
    def _mock_rule_violation(request):
        request.get_data()
        return mockserver.make_response()

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/disable_session',
    )
    def _mock_disable_session(request):
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
    def _mock_reposition_rule_violations(request):
        rule_violations.append(json.loads(request.get_data()))
        return {}

    def build_shorttrack_response():
        responses = {
            'dbid777_999': {'lon': 37.631680, 'lat': 55.736567},
            'dbid888_777': {'lon': 30.631680, 'lat': 59.736567},
            'dbid333_333': {'lon': 37.631680, 'lat': 55.736567},
            'dbid444_444': {'lon': 30.631680, 'lat': 59.736567},
            'dbid555_555': {'lon': 37.631680, 'lat': 55.736567},
        }

        response = {'data': []}
        for key, value in responses.items():
            response['data'].append(
                {
                    'driver_id': key,
                    'raw': [
                        {
                            'timestamp': 1504893333,
                            'lon': value['lon'],
                            'lat': value['lat'],
                            'direction': 70,
                            'speed': 0,
                            'accuracy': 1.0,
                        },
                        {
                            'timestamp': 1504893334,
                            'lon': 30.0,
                            'lat': 60.0,
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
            'dbid777_999': {
                'position': [37.631680, 55.736567],
                'destination': [30.0, 60.0],
                'time_left': 1800,
                'distance_left': 20000,
                'tracking_type': 'route_tracking',
                'service_id': 'reposition-watcher',
                'etas': [],
            },
            'dbid888_777': {
                'position': [30.631680, 59.736567],
                'destination': [30.0, 60.0],
                'time_left': 180,
                'distance_left': 2000,
                'tracking_type': 'route_tracking',
                'service_id': 'reposition-watcher',
                'etas': [],
            },
            'dbid333_333': {
                'position': [37.631680, 55.736567],
                'destination': [30.0, 60.0],
                'time_left': 1800,
                'distance_left': 20000,
                'tracking_type': 'route_tracking',
                'service_id': 'reposition-watcher',
                'etas': [],
            },
            'dbid444_444': {
                'position': [30.631680, 59.736567],
                'destination': [30.0, 60.0],
                'time_left': 180,
                'distance_left': 2000,
                'tracking_type': 'route_tracking',
                'service_id': 'reposition-watcher',
                'etas': [],
            },
            'dbid555_555': {
                'position': [37.631680, 55.736567],
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

    @testpoint('reposition-watcher::finish')
    def _on_watcher_finish(data):
        pass

    def _fetch_sessions():
        return select_named(
            'SELECT s.session_id, s.drw_state, r.updating, r.updated_at '
            'FROM state.sessions s '
            'INNER JOIN state.checks r ON s.session_id = r.session_id '
            'ORDER BY s.session_id',
            pgsql['reposition_watcher'],
        )

    def _fetch_route_states():
        return select_named(
            'SELECT r.state_id, r.drw, r.drw_dry_run '
            'FROM state.route r '
            'ORDER BY r.state_id',
            pgsql['reposition_watcher'],
        )

    assert _fetch_sessions() == [
        {
            'session_id': 1511,
            'drw_state': 'Assigned',
            'updating': None,
            'updated_at': None,
        },
        {
            'session_id': 1512,
            'drw_state': 'Active',
            'updating': None,
            'updated_at': None,
        },
        {
            'session_id': 1513,
            'drw_state': None,
            'updating': None,
            'updated_at': None,
        },
        {
            'session_id': 1514,
            'drw_state': 'Active',
            'updating': None,
            'updated_at': None,
        },
        {
            'session_id': 1515,
            'drw_state': 'Disabled',
            'updating': None,
            'updated_at': None,
        },
    ]

    assert _fetch_route_states() == [
        {'state_id': 101, 'drw': False, 'drw_dry_run': None},
        {'state_id': 102, 'drw': True, 'drw_dry_run': True},
        {'state_id': 103, 'drw': False, 'drw_dry_run': None},
        {'state_id': 104, 'drw': True, 'drw_dry_run': False},
        {'state_id': 105, 'drw': False, 'drw_dry_run': None},
    ]

    async with statistics.capture(taxi_reposition_watcher) as capture:
        response = await taxi_reposition_watcher.post(
            'service/cron', json={'task_name': get_task_name()},
        )
    assert response.status_code == 200

    await _on_watcher_finish.wait_call()

    assert driver_trackstory_v2_shorttracks.mock.times_called == 1

    assert _mock_rule_violation.times_called == 1

    assert _mock_reposition_rule_violations.times_called == 1
    assert _mock_disable_session.times_called == 1

    assert _mock_start_watch.times_called == 2
    assert _mock_time_left.times_called == 2
    assert _mock_stop_watch.times_called == 1

    assert 'reposition.drw_time_lefts.success' in capture.statistics
    assert capture.statistics['reposition.drw_time_lefts.success'] == 2
    assert 'reposition.drw_time_lefts.error' not in capture.statistics

    assert _fetch_sessions() == [
        {
            'session_id': 1511,
            'drw_state': 'Active',
            'updating': None,
            'updated_at': datetime.datetime(2020, 6, 25, 13, 0, 0),
        },
        {
            'session_id': 1512,
            'drw_state': 'Active',
            'updating': None,
            'updated_at': datetime.datetime(2020, 6, 25, 13, 0, 0),
        },
        {
            'session_id': 1513,
            'drw_state': 'Active',
            'updating': None,
            'updated_at': datetime.datetime(2020, 6, 25, 13, 0, 0),
        },
        {
            'session_id': 1515,
            'drw_state': 'Disabled',
            'updating': None,
            'updated_at': datetime.datetime(2020, 6, 25, 13, 0, 0),
        },
    ]

    assert _fetch_route_states() == [
        {'state_id': 101, 'drw': False, 'drw_dry_run': None},
        {'state_id': 102, 'drw': True, 'drw_dry_run': True},
        {'state_id': 103, 'drw': False, 'drw_dry_run': None},
        {'state_id': 105, 'drw': False, 'drw_dry_run': None},
    ]

    async with statistics.capture(taxi_reposition_watcher) as capture:
        response = await taxi_reposition_watcher.post(
            'service/cron', json={'task_name': get_task_name()},
        )
    assert response.status_code == 200

    await _on_watcher_finish.wait_call()

    assert _mock_start_watch.times_called == 2
    assert _mock_time_left.times_called == 5
    assert _mock_stop_watch.times_called == 1

    assert _fetch_sessions() == [
        {
            'session_id': 1511,
            'drw_state': 'Active',
            'updating': None,
            'updated_at': datetime.datetime(2020, 6, 25, 13, 0, 0),
        },
        {
            'session_id': 1512,
            'drw_state': 'Active',
            'updating': None,
            'updated_at': datetime.datetime(2020, 6, 25, 13, 0, 0),
        },
        {
            'session_id': 1513,
            'drw_state': 'Active',
            'updating': None,
            'updated_at': datetime.datetime(2020, 6, 25, 13, 0, 0),
        },
        {
            'session_id': 1515,
            'drw_state': 'Disabled',
            'updating': None,
            'updated_at': datetime.datetime(2020, 6, 25, 13, 0, 0),
        },
    ]


@pytest.mark.now('2020-06-25T13:00:00+0000')
@pytest.mark.pgsql('reposition_watcher', files=['drw.sql'])
async def test_drw_reset(
        taxi_reposition_watcher,
        mockserver,
        pgsql,
        load,
        testpoint,
        statistics,
        now,
        driver_trackstory_v2_shorttracks,
):
    events = []
    rule_violations = []

    @mockserver.json_handler('/candidates/profiles')
    def _mock_profiles(request):
        return driver_status('free')

    @mockserver.handler('/driver-protocol/service/reposition/rule-violations')
    def _mock_rule_violation(request):
        request.get_data()
        return mockserver.make_response()

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/disable_session',
    )
    def _mock_disable_session(request):
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
    def _mock_reposition_rule_violations(request):
        rule_violations.append(json.loads(request.get_data()))
        return {}

    def build_shorttrack_response():
        responses = {
            'dbid777_999': {'lon': 37.631680, 'lat': 55.736567},
            'dbid888_777': {'lon': 30.631680, 'lat': 59.736567},
            'dbid333_333': {'lon': 37.631680, 'lat': 55.736567},
            'dbid444_444': {'lon': 30.631680, 'lat': 59.736567},
            'dbid555_555': {'lon': 37.631680, 'lat': 55.736567},
        }

        response = {'data': []}
        for key, value in responses.items():
            response['data'].append(
                {
                    'driver_id': key,
                    'raw': [
                        {
                            'timestamp': 1504893333,
                            'lon': value['lon'],
                            'lat': value['lat'],
                            'direction': 70,
                            'speed': 0,
                            'accuracy': 1.0,
                        },
                        {
                            'timestamp': 1504893334,
                            'lon': 30.0,
                            'lat': 60.0,
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
        return {}

    @mockserver.json_handler('/driver-route-watcher/stop-watch')
    def _mock_stop_watch(request):
        return {}

    @testpoint('reposition-watcher::finish')
    def _on_watcher_finish(data):
        pass

    def _fetch_sessions():
        return select_named(
            'SELECT s.session_id, s.drw_state, r.updating, r.updated_at '
            'FROM state.sessions s '
            'INNER JOIN state.checks r ON s.session_id = r.session_id '
            'ORDER BY s.session_id',
            pgsql['reposition_watcher'],
        )

    def _fetch_route_states():
        return select_named(
            'SELECT r.state_id, r.last_check, r.start_time,'
            ' r.violations_count, r.failed_checks_count, '
            'r.last_checks_count, r.drw, r.drw_dry_run '
            'FROM state.route r '
            'ORDER BY r.state_id',
            pgsql['reposition_watcher'],
        )

    statistics.fallbacks = ['reposition.drw_time_lefts.fallback']
    await taxi_reposition_watcher.invalidate_caches()

    response = await taxi_reposition_watcher.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    await _on_watcher_finish.wait_call()

    assert _mock_start_watch.times_called == 0
    assert _mock_time_left.times_called == 0
    assert _mock_stop_watch.times_called == 2

    assert _fetch_sessions() == [
        {
            'session_id': 1511,
            'drw_state': 'Disabled',
            'updating': None,
            'updated_at': now,
        },
        {
            'session_id': 1512,
            'drw_state': 'Disabled',
            'updating': None,
            'updated_at': now,
        },
        {
            'session_id': 1513,
            'drw_state': 'Disabled',
            'updating': None,
            'updated_at': now,
        },
        {
            'session_id': 1514,
            'drw_state': 'Disabled',
            'updating': None,
            'updated_at': now,
        },
        {
            'session_id': 1515,
            'drw_state': 'Disabled',
            'updating': None,
            'updated_at': now,
        },
    ]

    assert _fetch_route_states() == [
        {
            'state_id': 101,
            'last_check': now,
            'start_time': now,
            'violations_count': 0,
            'failed_checks_count': 0,
            'last_checks_count': 0,
            'drw': False,
            'drw_dry_run': None,
        },
        {
            'state_id': 102,
            'last_check': now,
            'start_time': now,
            'violations_count': 0,
            'failed_checks_count': 0,
            'last_checks_count': 0,
            'drw': False,
            'drw_dry_run': None,
        },
        {
            'state_id': 103,
            'last_check': now,
            'start_time': now,
            'violations_count': 0,
            'failed_checks_count': 0,
            'last_checks_count': 0,
            'drw': False,
            'drw_dry_run': None,
        },
        {
            'state_id': 104,
            'last_check': now,
            'start_time': now,
            'violations_count': 0,
            'failed_checks_count': 0,
            'last_checks_count': 0,
            'drw': False,
            'drw_dry_run': None,
        },
        {
            'state_id': 105,
            'last_check': now,
            'start_time': now,
            'violations_count': 0,
            'failed_checks_count': 0,
            'last_checks_count': 0,
            'drw': False,
            'drw_dry_run': None,
        },
    ]


@pytest.mark.now('2020-06-25T13:00:00+0000')
@pytest.mark.pgsql('reposition_watcher', files=['drw_pending.sql'])
async def test_drr_become_pending(
        taxi_reposition_watcher,
        mockserver,
        pgsql,
        testpoint,
        now,
        driver_trackstory_v2_shorttracks,
):
    events = []
    rule_violations = []

    @mockserver.json_handler('/candidates/profiles')
    def _mock_profiles(request):
        return driver_status('free')

    @mockserver.handler('/driver-protocol/service/reposition/rule-violations')
    def _mock_rule_violation(request):
        request.get_data()
        return mockserver.make_response()

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/disable_session',
    )
    def _mock_disable_session(request):
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
    def _mock_reposition_rule_violations(request):
        rule_violations.append(json.loads(request.get_data()))
        return {}

    def build_shorttrack_response():
        responses = {
            'dbid777_999': {'lon': 37.631680, 'lat': 55.736567},
            'dbid888_777': {'lon': 30.631680, 'lat': 59.736567},
            'dbid333_333': {'lon': 37.631680, 'lat': 55.736567},
            'dbid444_444': {'lon': 30.631680, 'lat': 59.736567},
            'dbid555_555': {'lon': 37.631680, 'lat': 55.736567},
        }

        response = {'data': []}
        for key, value in responses.items():
            response['data'].append(
                {
                    'driver_id': key,
                    'raw': [
                        {
                            'timestamp': 1504893333,
                            'lon': value['lon'],
                            'lat': value['lat'],
                            'direction': 70,
                            'speed': 0,
                            'accuracy': 1.0,
                        },
                        {
                            'timestamp': 1504893334,
                            'lon': 30.0,
                            'lat': 60.0,
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
        req = json.loads(request.get_data())
        dbid_uuid = req['driver']
        if dbid_uuid['dbid'] == 'dbid333':
            data = {
                'destination': [30, 60],
                'position': [30, 60],
                'time_left': 2,
                'distance_left': 20,
                'tracking_type': 'route_tracking',
                'service_id': 'reposition-watcher',
                'etas': [],
            }
        else:
            return mockserver.make_response(status=425, json={})
        return mockserver.make_response(status=200, json=data)

    @mockserver.json_handler('/driver-route-watcher/stop-watch')
    def _mock_stop_watch(request):
        return {}

    @testpoint('reposition-watcher::finish')
    def _on_watcher_finish(data):
        pass

    def _fetch_sessions():
        return select_named(
            'SELECT s.session_id, s.drw_state, r.updating, r.updated_at '
            'FROM state.sessions s '
            'INNER JOIN state.checks r ON s.session_id = r.session_id '
            'ORDER BY s.session_id',
            pgsql['reposition_watcher'],
        )

    response = await taxi_reposition_watcher.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    await _on_watcher_finish.wait_call()

    assert _mock_start_watch.times_called == 0
    assert _mock_time_left.times_called == 3
    assert _mock_stop_watch.times_called == 0

    assert _fetch_sessions() == [
        {
            'session_id': 1511,
            'drw_state': 'Pending',
            'updating': None,
            'updated_at': now,
        },
        {
            'session_id': 1512,
            'drw_state': 'Pending',
            'updating': None,
            'updated_at': now,
        },
        {
            'session_id': 1513,
            'drw_state': 'Active',
            'updating': None,
            'updated_at': now,
        },
    ]
