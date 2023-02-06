import json

import pytest

from taxi_tests.utils import ordered_object


@pytest.fixture
def dummy_replication(mockserver):
    @mockserver.json_handler('/replication/state/all_yt_target_info')
    def mock_replication(request):
        return {
            'targets_info': [
                {
                    'table_path': 'table-path-both',
                    'target_names': ['target-name-both'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 0},
                        {'client_name': 'yt-repl', 'current_delay': 0},
                    ],
                },
                {
                    'table_path': 'table-path-none',
                    'target_names': ['target-name-none'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 100000},
                        {'client_name': 'yt-repl', 'current_delay': 100000},
                    ],
                },
                {
                    'table_path': 'table-path-test',
                    'target_names': ['target-name-test'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 0},
                        {'client_name': 'yt-repl', 'current_delay': 100000},
                    ],
                },
                {
                    'table_path': 'table-path-none-delay',
                    'target_names': ['target-name-none-delay'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': None},
                        {'client_name': 'yt-repl', 'current_delay': None},
                    ],
                },
            ],
        }


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_service_yt_enabled_both(
        taxi_archive_api, mockserver, dummy_replication,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def mock_lookup_rows(request):
        return _mock_lookup_rows(request, 'table-path-both')

    response = _perform_request(taxi_archive_api, 'target-name-both')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    ordered_object.assert_eq(response.json()['items'], [{'from': 'yt'}], [''])


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z', dummy_replication)
def test_service_yt_enabled_none(
        taxi_archive_api, mockserver, dummy_replication,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def mock_lookup_rows(request):
        assert False

    response = _perform_request(taxi_archive_api, 'target-name-none')
    assert response.status_code == 503


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z', dummy_replication)
def test_service_yt_enabled_test(
        taxi_archive_api, mockserver, dummy_replication,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    def mock_lookup_rows_test(request):
        return _mock_lookup_rows(request, 'table-path-test')

    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def mock_lookup_rows_repl(request):
        assert False

    response = _perform_request(taxi_archive_api, 'target-name-test')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    ordered_object.assert_eq(
        response.json(),
        {'items': [{'from': 'yt'}], 'source': 'yt-test'},
        [''],
    )
    assert mock_lookup_rows_test.times_called == 1
    assert mock_lookup_rows_repl.times_called == 0


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z', dummy_replication)
def test_service_yt_response_error(
        taxi_archive_api, mockserver, now, dummy_replication,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def mock_lookup_rows(request):
        return _mock_lookup_rows(request, 'table-path-both')

    # init cache
    taxi_archive_api.tests_control(now, invalidate_caches=True)

    @mockserver.json_handler('/replication/state/all_yt_target_info')
    def mock_replication_error(request):
        return mockserver.make_response(status=500)

    # update cache with 500 from replication service
    taxi_archive_api.tests_control(now, invalidate_caches=True)

    response = _perform_request(taxi_archive_api, 'target-name-both')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    ordered_object.assert_eq(response.json()['items'], [{'from': 'yt'}], [''])


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_service_yt_enabled_none_delays(
        taxi_archive_api, mockserver, dummy_replication,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def mock_lookup_rows(request):
        return _mock_lookup_rows(request, 'table-path-none-delay')

    response = _perform_request(taxi_archive_api, 'target-name-none-delay')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    ordered_object.assert_eq(response.json()['items'], [{'from': 'yt'}], [''])


def _mock_lookup_rows(request, table_path):
    request_path = json.loads(request.headers.get('X-Yt-Parameters'))['path']
    assert request_path == '//home/taxi/unstable/' + table_path
    return {'from': 'yt'}


def _perform_request(taxi_archive_api, target_name):
    return taxi_archive_api.post(
        'v1/yt/lookup_rows',
        json={
            'query': [{'id': 'lookup_id'}],
            'replication_rule': {'name': target_name, 'max_delay': 43200},
        },
    )
