# pylint: disable=import-only-modules
import json

import pytest

from .utils import select_named


@pytest.mark.now('2019-09-01T13:00:07')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'zone_default.sql',
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_home.sql',
        'submodes_poi.sql',
        'check_rules.sql',
        'check_rules_to_watcher.sql',
        'active_session.sql',
        'sessions_to_watcher.sql',
    ],
)
async def test_main(
        taxi_reposition_api,
        taxi_reposition_api_monitor,
        load_json,
        mockserver,
        pgsql,
):
    @mockserver.json_handler('/reposition-watcher/v1/service/session/add')
    def mock_reposition_watcher_add(request):
        data = json.loads(request.get_data())
        assert data['session_id']
        assert data['work_mode']
        add_responses[str(data['session_id'])] = data

        return mockserver.make_response(status=200)

    @mockserver.json_handler('/reposition-watcher/v1/service/session/remove')
    def mock_reposition_watcher_remove(request):
        data = json.loads(request.get_data())
        assert data['session_id']
        remove_responses[str(data['session_id'])] = data

        return mockserver.make_response(status=200)

    old_metrics = await taxi_reposition_api_monitor.get_metric(
        'reposition-watcher-uploader',
    )

    add_responses, remove_responses = {}, {}

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': 'reposition-watcher-uploader'},
        )
    ).status_code == 200

    assert mock_reposition_watcher_add.times_called == 3
    assert mock_reposition_watcher_remove.times_called == 1

    expected_add_responses = load_json('reposition_watcher_add_responses.json')
    expected_remove_responses = load_json(
        'reposition_watcher_remove_responses.json',
    )

    add_ids = ['2004', '2005', '2006']
    remove_ids = ['2008']

    for add_id in add_ids:
        assert add_responses[add_id] == expected_add_responses[add_id]

    for remove_id in remove_ids:
        assert (
            remove_responses[remove_id] == expected_remove_responses[remove_id]
        )

    query = 'SELECT COUNT(*) FROM state.sessions_to_reposition_watcher '
    rows = select_named(query, pgsql['reposition'])

    assert rows[0]['count'] == 0

    metrics = await taxi_reposition_api_monitor.get_metric(
        'reposition-watcher-uploader',
    )
    for key, value in old_metrics.items():
        metrics[key] -= value
    assert metrics == {
        'ok_total': 9,
        'ok_deleted': 9,
        'ok_sent': 4,
        'error_wrong_session_requests_order': 0,
        'warn_session_restarts': 0,
        'warn_one_session_few_events': 2,
        'error_one_driver_few_sessions': 1,
        'warn_skipped': 0,
        'error_sent': 0,
        'error_deleted': 0,
    }


@pytest.mark.now('2019-09-01T13:00:07')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'zone_default.sql',
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_home.sql',
        'submodes_poi.sql',
        'check_rules.sql',
        'check_rules_to_watcher.sql',
        'active_session.sql',
        'intersecting_add_remove_sessions.sql',
    ],
)
async def test_intersecting_sections(
        taxi_reposition_api, load_json, mockserver, pgsql,
):
    @mockserver.json_handler('/reposition-watcher/v1/service/session/add')
    def mock_reposition_watcher_add(request):
        data = json.loads(request.get_data())
        assert data['session_id']
        assert data['work_mode']
        add_responses[str(data['session_id'])] = data

        return mockserver.make_response(status=200)

    @mockserver.json_handler('/reposition-watcher/v1/service/session/remove')
    def mock_reposition_watcher_remove(request):
        data = json.loads(request.get_data())
        assert data['session_id']
        remove_responses[str(data['session_id'])] = data

        return mockserver.make_response(status=200)

    add_responses, remove_responses = {}, {}

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': 'reposition-watcher-uploader'},
        )
    ).status_code == 200

    assert mock_reposition_watcher_add.times_called == 3
    assert mock_reposition_watcher_remove.times_called == 1

    expected_add_responses = load_json('reposition_watcher_add_responses.json')
    expected_remove_responses = load_json(
        'reposition_watcher_remove_responses.json',
    )

    add_ids = ['2005', '2006', '2009']
    remove_ids = ['2007']

    for add_id in add_ids:
        assert add_responses[add_id] == expected_add_responses[add_id]

    for remove_id in remove_ids:
        assert (
            remove_responses[remove_id] == expected_remove_responses[remove_id]
        )

    query = 'SELECT COUNT(*) FROM state.sessions_to_reposition_watcher'
    rows = select_named(query, pgsql['reposition'])

    assert rows[0]['count'] == 0


@pytest.mark.now('2019-09-01T13:00:07')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'zone_default.sql',
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_home.sql',
        'submodes_poi.sql',
        'check_rules.sql',
        'check_rules_to_watcher.sql',
        'active_session.sql',
        'sessions_to_watcher_uploader_warning.sql',
    ],
)
async def test_warnings(
        taxi_reposition_api,
        taxi_reposition_api_monitor,
        load_json,
        mockserver,
        pgsql,
):
    @mockserver.json_handler('/reposition-watcher/v1/service/session/add')
    def mock_reposition_watcher_add(request):
        data = json.loads(request.get_data())
        assert data['session_id']
        assert data['work_mode']
        add_responses[str(data['session_id'])] = data

        return mockserver.make_response(status=200)

    @mockserver.json_handler('/reposition-watcher/v1/service/session/remove')
    def mock_reposition_watcher_remove(request):
        data = json.loads(request.get_data())
        assert data['session_id']
        remove_responses[str(data['session_id'])] = data

        return mockserver.make_response(status=200)

    old_metrics = await taxi_reposition_api_monitor.get_metric(
        'reposition-watcher-uploader',
    )

    add_responses, remove_responses = {}, {}

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': 'reposition-watcher-uploader'},
        )
    ).status_code == 200

    assert mock_reposition_watcher_add.times_called == 4
    assert mock_reposition_watcher_remove.times_called == 2

    expected_add_responses = load_json('reposition_watcher_add_responses.json')
    expected_remove_responses = load_json(
        'reposition_watcher_remove_responses.json',
    )

    add_ids = ['2003', '2004', '2005', '2006']
    remove_ids = ['2008', '2009']

    for add_id in add_ids:
        assert add_responses[add_id] == expected_add_responses[add_id]

    for remove_id in remove_ids:
        assert (
            remove_responses[remove_id] == expected_remove_responses[remove_id]
        )

    query = 'SELECT COUNT(*) FROM state.sessions_to_reposition_watcher '
    rows = select_named(query, pgsql['reposition'])

    assert rows[0]['count'] == 0

    metrics = await taxi_reposition_api_monitor.get_metric(
        'reposition-watcher-uploader',
    )
    for key, value in old_metrics.items():
        metrics[key] -= value
    assert metrics == {
        'ok_total': 8,
        'ok_deleted': 8,
        'ok_sent': 6,
        'warn_session_restarts': 1,
        'warn_one_session_few_events': 2,
        'error_one_driver_few_sessions': 0,
        'error_wrong_session_requests_order': 0,
        'warn_skipped': 0,
        'error_sent': 0,
        'error_deleted': 0,
    }


@pytest.mark.now('2019-09-01T13:00:07')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'zone_default.sql',
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_home.sql',
        'submodes_poi.sql',
        'check_rules.sql',
        'check_rules_to_watcher.sql',
        'active_session.sql',
        'sessions_to_watcher_uploader_wrong_order.sql',
    ],
)
async def test_wrong_order(
        taxi_reposition_api,
        taxi_reposition_api_monitor,
        load_json,
        mockserver,
        pgsql,
):
    @mockserver.json_handler('/reposition-watcher/v1/service/session/add')
    def mock_reposition_watcher_add(request):
        data = json.loads(request.get_data())
        assert data['session_id']
        assert data['work_mode']
        add_responses[str(data['session_id'])] = data

        return mockserver.make_response(status=200)

    @mockserver.json_handler('/reposition-watcher/v1/service/session/remove')
    def mock_reposition_watcher_remove(request):
        data = json.loads(request.get_data())
        assert data['session_id']
        remove_responses[str(data['session_id'])] = data

        return mockserver.make_response(status=200)

    old_metrics = await taxi_reposition_api_monitor.get_metric(
        'reposition-watcher-uploader',
    )

    add_responses, remove_responses = {}, {}

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': 'reposition-watcher-uploader'},
        )
    ).status_code == 200

    assert mock_reposition_watcher_add.times_called == 4
    assert mock_reposition_watcher_remove.times_called == 1

    expected_add_responses = load_json('reposition_watcher_add_responses.json')
    expected_remove_responses = load_json(
        'reposition_watcher_remove_responses.json',
    )

    add_ids = ['2003', '2004', '2005', '2006']
    remove_ids = ['2009']

    for add_id in add_ids:
        assert add_responses[add_id] == expected_add_responses[add_id]

    for remove_id in remove_ids:
        assert (
            remove_responses[remove_id] == expected_remove_responses[remove_id]
        )

    query = 'SELECT COUNT(*) FROM state.sessions_to_reposition_watcher '
    rows = select_named(query, pgsql['reposition'])

    assert rows[0]['count'] == 0

    metrics = await taxi_reposition_api_monitor.get_metric(
        'reposition-watcher-uploader',
    )
    for key, value in old_metrics.items():
        metrics[key] -= value
    assert metrics == {
        'ok_total': 9,
        'ok_deleted': 9,
        'ok_sent': 5,
        'warn_session_restarts': 1,
        'warn_one_session_few_events': 2,
        'error_wrong_session_requests_order': 1,
        'error_one_driver_few_sessions': 0,
        'warn_skipped': 0,
        'error_sent': 0,
        'error_deleted': 0,
    }


@pytest.mark.now('2019-09-01T13:00:07')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'zone_default.sql',
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_home.sql',
        'submodes_poi.sql',
        'check_rules.sql',
        'check_rules_to_watcher.sql',
        'active_session.sql',
        'sessions_to_watcher_uploader_warning.sql',
    ],
)
async def test_watcher_failure(
        taxi_reposition_api,
        taxi_reposition_api_monitor,
        load_json,
        mockserver,
        pgsql,
):
    @mockserver.json_handler('/reposition-watcher/v1/service/session/add')
    def mock_reposition_watcher_add(request):
        data = json.loads(request.get_data())
        assert data['session_id']
        assert data['work_mode']
        add_responses[str(data['session_id'])] = data

        return mockserver.make_response(status=200)

    @mockserver.json_handler('/reposition-watcher/v1/service/session/remove')
    def mock_reposition_watcher_remove(request):
        data = json.loads(request.get_data())
        assert data['session_id']
        remove_responses[str(data['session_id'])] = data

        return mockserver.make_response(status=400)

    old_metrics = await taxi_reposition_api_monitor.get_metric(
        'reposition-watcher-uploader',
    )

    add_responses, remove_responses = {}, {}

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': 'reposition-watcher-uploader'},
        )
    ).status_code == 200

    assert mock_reposition_watcher_add.times_called == 3
    assert mock_reposition_watcher_remove.times_called == 2

    expected_add_responses = load_json('reposition_watcher_add_responses.json')
    expected_remove_responses = load_json(
        'reposition_watcher_remove_responses.json',
    )

    add_ids = ['2004', '2005', '2006']
    remove_ids = ['2008', '2009']

    for add_id in add_ids:
        assert add_responses[add_id] == expected_add_responses[add_id]

    for remove_id in remove_ids:
        assert (
            remove_responses[remove_id] == expected_remove_responses[remove_id]
        )

    query = 'SELECT COUNT(*) FROM state.sessions_to_reposition_watcher '
    rows = select_named(query, pgsql['reposition'])

    assert rows[0]['count'] == 3

    metrics = await taxi_reposition_api_monitor.get_metric(
        'reposition-watcher-uploader',
    )
    for key, value in old_metrics.items():
        metrics[key] -= value
    assert metrics == {
        'ok_total': 8,
        'ok_deleted': 5,
        'ok_sent': 3,
        'warn_session_restarts': 0,
        'warn_one_session_few_events': 2,
        'error_one_driver_few_sessions': 0,
        'error_wrong_session_requests_order': 0,
        'warn_skipped': 1,
        'error_sent': 2,
        'error_deleted': 0,
    }
