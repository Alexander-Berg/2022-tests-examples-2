# pylint: disable=wrong-import-order, unused-variable, import-only-modules,
import json

import pytest

from tests_reposition_watcher.utils import driver_statuses
from tests_reposition_watcher.utils import get_task_name
from tests_reposition_watcher.utils import select_named


@pytest.mark.nofilldb()
@pytest.mark.parametrize('has_violations', [False, True])
@pytest.mark.now('2018-11-26T12:00:00+0000')
async def test_rule_violations(
        has_violations,
        taxi_reposition_watcher,
        heatmap_storage_fixture,
        mockserver,
        pgsql,
        load,
        mock_maps_router,
        driver_trackstory_v2_shorttracks,
):
    taximeter_status = 'free'
    queries = [load('test.sql'), load('update_arrival.sql')]
    if has_violations is True:
        queries.append(load('update_violations.sql'))
    pgsql['reposition_watcher'].apply_queries(queries)
    events = []
    rule_violations = []

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
            '1488_driverSS': {'lon': 30.0, 'lat': 60.00001},
            'dbid777_uuid': {'lon': 30.0005, 'lat': 60.0005},
            'clid_uuid1': {'lon': 30.0002, 'lat': 60.0002},
            'dbid_uuid': {'lon': 30.0001, 'lat': 60.0002},
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
        return mockserver.make_response(status=400, json={})

    @mockserver.json_handler('/driver-route-watcher/stop-watch')
    def _mock_stop_watch(request):
        return {}

    response = await taxi_reposition_watcher.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    assert mock_reposition_rule_violations.times_called == 7
    violations = sorted(rule_violations, key=lambda x: x['session_id'])
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
                {'type': 'arrived', 'valid_until': '2018-11-26T12:03:00+0000'},
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
        {
            'session_id': 1508,
            'violations': [
                {'type': 'arrived', 'valid_until': '2018-11-26T12:03:00+0000'},
            ],
        },
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

    assert (
        sorted(expected_violations, key=lambda x: x['session_id'])
        == violations
    )

    rows = select_named(
        """
    SELECT
      s.session_id, s.violation_type
    FROM state.rule_violations s
    """,
        pgsql['reposition_watcher'],
    )

    for row in rows:
        if row['session_id'] == 1501 and not has_violations:
            assert False
            continue
        if 1503 < row['session_id'] < 1507:
            assert False
        else:
            assert row['violation_type'] == 'SessionTimeoutWarning'
