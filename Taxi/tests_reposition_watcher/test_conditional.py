# pylint: disable=import-only-modules
import datetime

import pytest

from tests_reposition_watcher.utils import driver_status
from tests_reposition_watcher.utils import get_task_name
from tests_reposition_watcher.utils import select_named


@pytest.mark.now('2020-05-28T12:00:00+0000')
@pytest.mark.pgsql('reposition_watcher', files=['conditional_check.sql'])
@pytest.mark.parametrize(
    'to_disable,disable_session_calls', [(False, 0), (True, 1)],
)
@pytest.mark.parametrize('send_push', [True, False])
async def test_conditional(
        taxi_reposition_watcher,
        mockserver,
        pgsql,
        testpoint,
        driver_trackstory_v2_shorttracks,
        experiments3,
        to_disable,
        disable_session_calls,
        send_push,
):
    @mockserver.json_handler('/candidates/profiles')
    def _mock_profiles(request):
        return driver_status('free')

    @mockserver.json_handler(
        '/driver-protocol/service/reposition/rule-violations',
    )
    def _mock_rule_violation(request):
        assert request.json == {
            'violations': [
                {
                    'park_db_id': 'dbid888',
                    'driver_uuid': '777',
                    'type': 'conditional',
                    'urgency': 'final_warning',
                    'mode': 'home',
                },
            ],
        }
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
        return mockserver.make_response(status=400, json={})

    @mockserver.json_handler('/driver-route-watcher/stop-watch')
    def _mock_stop_watch(request):
        return {}

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/disable_session',
    )
    def mock_disable_session(request):
        assert request.json == {'session_id': 1512, 'reason': 'conditional'}
        return {}

    @testpoint('reposition-watcher::finish')
    def _on_watcher_finish(data):
        pass

    def _fetch_sessions():
        return select_named(
            'SELECT s.session_id, r.updating, r.updated_at '
            'FROM state.sessions s '
            'INNER JOIN state.checks r ON s.session_id = r.session_id '
            'ORDER BY s.session_id',
            pgsql['reposition_watcher'],
        )

    experiments3.add_config(
        consumers=['reposition-watcher/conditional-check'],
        name='reposition_watcher_conditional_check',
        match={
            'enabled': True,
            'consumers': [{'name': 'reposition-watcher/conditional-check'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'time',
                'predicate': {
                    'type': 'gt',
                    'init': {
                        'arg_name': 'reposition_start_ts',
                        'arg_type': 'timepoint',
                        'value': '2018-11-26T06:00:00+00:00',
                    },
                },
                'value': {'to_disable': to_disable, 'send_push': send_push},
            },
        ],
        default_value={'to_disable': False},
    )

    assert _fetch_sessions() == [
        {'session_id': 1511, 'updating': None, 'updated_at': None},
        {'session_id': 1512, 'updating': None, 'updated_at': None},
    ]

    response = await taxi_reposition_watcher.post(
        'service/cron', json={'task_name': get_task_name()},
    )
    assert response.status_code == 200

    await _on_watcher_finish.wait_call()

    assert mock_disable_session.times_called == disable_session_calls
    assert driver_trackstory_v2_shorttracks.mock.times_called == 1

    if to_disable:
        assert _fetch_sessions() == [
            {
                'session_id': 1511,
                'updating': None,
                'updated_at': datetime.datetime(2020, 5, 28, 12, 0, 0),
            },
        ]
        assert _mock_rule_violation.times_called == int(send_push)
    else:
        assert _fetch_sessions() == [
            {
                'session_id': 1511,
                'updating': None,
                'updated_at': datetime.datetime(2020, 5, 28, 12, 0, 0),
            },
            {
                'session_id': 1512,
                'updating': None,
                'updated_at': datetime.datetime(2020, 5, 28, 12, 0, 0),
            },
        ]
        assert _mock_rule_violation.times_called == 0
