import json

import bson
import pytest


YT_RESPONSE_YSON = (
    b'{"k3"=1;"k1"={"k2"=["v1";5;#;];};"k5"=#;"k4"=4.5;};{"kk"="vv"};'
)


@pytest.fixture
def dummy_replication(mockserver):
    @mockserver.json_handler('/replication/state/all_yt_target_info')
    def mock_replication(request):
        return {
            'targets_info': [
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-test'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 0},
                        {'client_name': 'yt-repl', 'current_delay': 100000},
                    ],
                },
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-repl'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 100000},
                        {'client_name': 'yt-repl', 'current_delay': 0},
                    ],
                },
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-not-updated'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 100000},
                        {'client_name': 'yt-repl', 'current_delay': 100000},
                    ],
                },
            ],
        }


@pytest.mark.parametrize(
    'yt_replication_rule, archive_api_response',
    [
        (
            {'name': 'repl-name-test', 'max_delay': 43200},
            {'source': 'yt-test', 'items': [{'from': 'yt-test-cluster'}]},
        ),
        (
            {'name': 'repl-name-repl', 'max_delay': 43200},
            {'source': 'yt-repl', 'items': [{'from': 'yt-repl-cluster'}]},
        ),
    ],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_request(
        taxi_archive_api,
        mockserver,
        dummy_replication,
        yt_replication_rule,
        archive_api_response,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    def lookup_rows_test(request):
        return {'from': 'yt-test-cluster'}

    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def lookup_rows_repl(request):
        return {'from': 'yt-repl-cluster'}

    response = taxi_archive_api.post(
        'v1/yt/lookup_rows',
        json={
            'query': [{'id': 'lookup_id'}],
            'replication_rule': yt_replication_rule,
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json() == archive_api_response


@pytest.mark.parametrize(
    'yt_replication_rule',
    [
        ({'name': 'repl-name-not-updated', 'max_delay': 0}),
        ({'name': 'repl-name-not-updated'}),
    ],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_any_delay(
        taxi_archive_api, mockserver, dummy_replication, yt_replication_rule,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def lookup_rows_repl(request):
        return {'from': 'yt'}

    response = taxi_archive_api.post(
        'v1/yt/lookup_rows',
        json={
            'query': [{'id': 'lookup_id'}],
            'replication_rule': yt_replication_rule,
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json()['items'] == [{'from': 'yt'}]


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_request_not_found(
        taxi_archive_api, mockserver, dummy_replication,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def lookup_rows_test(request):
        return mockserver.make_response()

    response = taxi_archive_api.post(
        'v1/yt/lookup_rows',
        json={
            'query': [{'id': 'lookup_id'}],
            'replication_rule': {'name': 'repl-name-test', 'max_delay': 43200},
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json() == {'source': 'yt-test', 'items': []}


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_parallel_requests(taxi_archive_api, mockserver, dummy_replication):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    def lookup_rows_test(request):
        return {'from': 'yt'}

    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def lookup_rows_repl(request):
        return {'from': 'yt'}

    response = taxi_archive_api.post(
        'v1/yt/lookup_rows',
        json={
            'query': [{'id': 'lookup_id'}],
            'replication_rule': {'name': 'repl-name-test', 'max_delay': 0},
            'parallel_requests': 1,
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json()['items'] == [{'from': 'yt'}]

    assert lookup_rows_test.times_called + lookup_rows_repl.times_called == 1


@pytest.mark.config(
    YT_HOSTS_UPDATE_ENABLED=True,
    YT_HTTP_CLIENT_SETTINGS={
        '__default__': {
            'attempts': 1,
            'hosts-number': 2,
            'request-timeout-ms': 10000,
            'total-wait-timeout-ms': 10000,
        },
        'yt-test': {
            'attempts': 1,
            'hosts-number': 2,
            'request-timeout-ms': 2000,
            'total-wait-timeout-ms': 10000,
        },
    },
)
@pytest.mark.parametrize('from_request', [True, False])
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_yt_internal_timeout(
        taxi_archive_api, mockserver, dummy_replication, from_request,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    def lookup_rows_yt_test(request):
        yt_parameters = json.loads(request.headers['X-YT-Parameters'])
        assert yt_parameters['timeout'] == (1000 if from_request else 2000)
        return {'from': 'yt'}

    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def lookup_rows_yt_repl(request):
        yt_parameters = json.loads(request.headers['X-YT-Parameters'])
        assert yt_parameters['timeout'] == (1000 if from_request else 10000)
        return {'from': 'yt'}

    request_json = {
        'query': [{'id': 'lookup_id'}],
        'replication_rule': {'name': 'repl-name-test', 'max_delay': 0},
    }
    if from_request:
        request_json['yt_timeout_ms'] = 1000

    response = taxi_archive_api.post('v1/yt/lookup_rows', json=request_json)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json()['items'] == [{'from': 'yt'}]

    assert lookup_rows_yt_test.wait_call()
    assert lookup_rows_yt_repl.wait_call()


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_request_bson(taxi_archive_api, mockserver, dummy_replication):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def lookup_rows(request):
        return mockserver.make_response(YT_RESPONSE_YSON)

    response = taxi_archive_api.post(
        'v1/yt/lookup_rows',
        json={
            'query': [{'id': 'lookup_id'}],
            'replication_rule': {'name': 'repl-name-test', 'max_delay': 43200},
            'bson': True,
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'
    assert bson.BSON(response.content).decode()['items'] == [
        {'k1': {'k2': ['v1', 5, None]}, 'k3': 1, 'k4': 4.5, 'k5': None},
        {'kk': 'vv'},
    ]


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_request_yson(taxi_archive_api, mockserver, dummy_replication):
    @mockserver.json_handler('/yt/yt-test/api/v3/lookup_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/lookup_rows')
    def lookup_rows(request):
        return mockserver.make_response(YT_RESPONSE_YSON)

    response = taxi_archive_api.post(
        'v2/yt/lookup_rows',
        json={
            'query': [{'id': 'lookup_id'}],
            'replication_rule': {'name': 'repl-name-test', 'max_delay': 43200},
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/x-yt-yson-binary'
    assert response.content == b'[' + YT_RESPONSE_YSON + b']'


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_no_param_query(taxi_archive_api, dummy_replication):
    response = taxi_archive_api.post(
        'v1/yt/lookup_rows',
        json={'replication_rule': {'name': 'rule_name', 'max_delay': 0}},
    )
    assert response.status_code == 400


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_no_param_replication_rule(taxi_archive_api, dummy_replication):
    response = taxi_archive_api.post(
        'v1/yt/lookup_rows', json={'query': [{'id': 'lookup_id'}]},
    )
    assert response.status_code == 400


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_empty_param_query(taxi_archive_api, dummy_replication):
    response = taxi_archive_api.post(
        'v1/yt/lookup_rows',
        json={
            'query': [],
            'replication_rule': {'name': 'rule_name', 'max_delay': 0},
        },
    )
    assert response.status_code == 400


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_empty_param_replication_rule(taxi_archive_api, dummy_replication):
    response = taxi_archive_api.post(
        'v1/yt/lookup_rows',
        json={'query': [{'id': 'lookup_id'}], 'replication_rule': {}},
    )
    assert response.status_code == 400


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_not_updated_replication_rule(taxi_archive_api, dummy_replication):
    response = taxi_archive_api.post(
        'v1/yt/lookup_rows',
        json={
            'query': [{'id': 'lookup_id'}],
            'replication_rule': {
                'name': 'repl-name-not-updated',
                'max_delay': 43200,
            },
        },
    )

    assert response.status_code == 503


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_not_existed_replication_rule(taxi_archive_api, dummy_replication):
    response = taxi_archive_api.post(
        'v1/yt/lookup_rows',
        json={
            'query': [{'id': 'lookup_id'}],
            'replication_rule': {
                'name': 'repl-name-undefined',
                'max_delay': 43200,
            },
        },
    )

    assert response.status_code == 404
