# pylint: disable=wrong-import-order, too-many-lines, import-only-modules
import datetime
import json

import pytest

from tests_reposition_watcher.utils import driver_status
from tests_reposition_watcher.utils import get_task_name
from tests_reposition_watcher.utils import select_named


@pytest.mark.parametrize(
    'immobility_violations,labels,warning,active',
    [
        (0, ['first_warning'], 0, True),
        (0, ['first_warning', 'last_warning'], 1, True),
        (0, ['first_warning', 'last_warning', 'final_warning'], 0, True),
        (
            0,
            ['first_warning', 'last_warning', 'final_warning', 'bogus'],
            0,
            True,
        ),
        (1, ['first_warning'], 0, True),
        (2, ['first_warning'], 0, True),
    ],
)
@pytest.mark.now('2018-11-26T08:00:00+0000')
async def test_immobility_check(
        immobility_violations,
        labels,
        warning,
        active,
        taxi_reposition_watcher,
        mockserver,
        pgsql,
        load,
        experiments3,
        mock_maps_router,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_experiment(
        name='check_movement',
        consumers=['reposition/rule_violation', 'reposition-watcher'],
        match={
            'consumers': [
                {'name': 'reposition/rule_violation'},
                {'name': 'reposition-watcher'},
            ],
            'predicate': {'type': 'true'},
            'enabled': True,
            'driver_id': '999',
            'park_db_id': 'dbid777',
        },
        clauses=[],
        default_value={'enabled': True, 'tags': labels},
    )

    queries = [load('test.sql'), load('immobility.sql')]
    pgsql['reposition_watcher'].apply_queries(queries)
    cursor = pgsql['reposition_watcher'].conn.cursor()
    cursor.execute(
        'UPDATE state.immobility '
        'SET immobility_violations=' + str(immobility_violations),
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
        assert req_dict['reason'] == 'immobility'
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
            'dbid777_999': {'lon': 30.0, 'lat': 60.0},
            'dbid888_777': {'lon': 30.0, 'lat': 60.0},
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
    if not active:
        assert mock_disable_session.times_called == 1
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
            'driver_uuid': '999',
            'mode': 'home',
            'park_db_id': 'dbid777',
            'type': 'no_movement',
            'urgency': labels[warning],
        },
    ]
    expected_violations = [
        {
            'session_id': 1511,
            'violations': [
                {
                    'type': 'immobility_warning',
                    'valid_until': '2018-11-26T08:03:00+0000',
                },
            ],
        },
    ]
    assert (
        sorted(rule_violations, key=lambda x: x['session_id'])
        == expected_violations
    )

    assert events == []

    assert _mock_add_event.times_called == 0
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
        {'session_id': 1511, 'updated_at': now, 'updating': None},
    ]

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

    right = select_named(
        """
        select s.immobility_violations, s.last_check from state.immobility s
        inner join state.checks r ON
        r.immobility_state_id = s.state_id
        where state_id = 101
        """,
        pgsql['reposition_watcher'],
    )
    assert [
        {
            'last_check': datetime.datetime(2018, 11, 26, 8, 0),
            'immobility_violations': immobility_violations + 1,
        },
    ] == right
