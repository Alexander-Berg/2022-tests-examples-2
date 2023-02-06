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
                    'target_names': ['repl-name-1'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 0},
                        {'client_name': 'yt-repl', 'current_delay': 100000},
                    ],
                },
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-2'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 0},
                        {'client_name': 'yt-repl', 'current_delay': 100000},
                    ],
                },
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-3'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 100000},
                        {'client_name': 'yt-repl', 'current_delay': 0},
                    ],
                },
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-4'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 100000},
                        {'client_name': 'yt-repl', 'current_delay': 0},
                    ],
                },
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-5'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 0},
                        {'client_name': 'yt-repl-1', 'current_delay': 0},
                    ],
                },
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-6'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 0},
                        {'client_name': 'yt-repl-2', 'current_delay': 0},
                    ],
                },
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-7'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 100000},
                        {'client_name': 'yt-repl', 'current_delay': 100000},
                    ],
                },
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-8'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 100000},
                        {'client_name': 'yt-repl', 'current_delay': 100000},
                    ],
                },
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-9'],
                    'clients_delays': [
                        {'client_name': 'yt-test-1', 'current_delay': 0},
                        {'client_name': 'yt-repl-1', 'current_delay': 0},
                    ],
                },
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-10'],
                    'clients_delays': [
                        {'client_name': 'yt-test-2', 'current_delay': 0},
                        {'client_name': 'yt-repl-2', 'current_delay': 0},
                    ],
                },
                {
                    'table_path': 'collections/tmp',
                    'target_names': ['repl-name-both'],
                    'clients_delays': [
                        {'client_name': 'yt-test', 'current_delay': 0},
                        {'client_name': 'yt-repl', 'current_delay': 0},
                    ],
                },
            ],
        }


@pytest.mark.parametrize(
    'yt_replication_rules, archive_api_response',
    [
        (
            [
                {'name': 'repl-name-1', 'max_delay': 43200},
                {'name': 'repl-name-2', 'max_delay': 43200},
            ],
            {'source': 'yt-test', 'items': [{'from': 'yt-test-cluster'}]},
        ),
        (
            [
                {'name': 'repl-name-3', 'max_delay': 43200},
                {'name': 'repl-name-4', 'max_delay': 43200},
            ],
            {'source': 'yt-repl', 'items': [{'from': 'yt-repl-cluster'}]},
        ),
        (
            [
                {'name': 'repl-name-5', 'max_delay': 43200},
                {'name': 'repl-name-6', 'max_delay': 43200},
            ],
            {'source': 'yt-test', 'items': [{'from': 'yt-test-cluster'}]},
        ),
    ],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_request(
        taxi_archive_api,
        mockserver,
        dummy_replication,
        yt_replication_rules,
        archive_api_response,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/select_rows')
    def select_rows_test(request):
        return {'from': 'yt-test-cluster'}

    @mockserver.json_handler('/yt/yt-repl/api/v3/select_rows')
    def select_rows_repl(request):
        return {'from': 'yt-repl-cluster'}

    response = taxi_archive_api.post(
        'v1/yt/select_rows',
        json={
            'query': {
                'query_string': '* FROM [//home/taxi/collections/tmp] LIMIT 1',
            },
            'replication_rules': yt_replication_rules,
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json() == archive_api_response


@pytest.mark.parametrize(
    'query_string, query_params, query_result',
    [
        (
            '* FROM [//home/taxi/table/path] LIMIT 100',
            [],
            '* FROM [//home/taxi/table/path] LIMIT 100',
        ),
        (
            '* FROM %t LIMIT 100',
            ['//home/taxi/table/path'],
            '* FROM [//home/taxi/table/path] LIMIT 100',
        ),
        (
            '* FROM %t LIMIT 100',
            ['//home/taxi/table/path', 'unused_param'],
            '* FROM [//home/taxi/table/path] LIMIT 100',
        ),
        (
            '* FROM %t LIMIT 100',
            ['//home/taxi/table/path', 100],
            '* FROM [//home/taxi/table/path] LIMIT 100',
        ),
        (
            '* FROM %t LIMIT 100',
            ['//home/taxi/table/path', 100.5],
            '* FROM [//home/taxi/table/path] LIMIT 100',
        ),
        (
            '* FROM %t LIMIT 100',
            ['//home/taxi/table/path', False],
            '* FROM [//home/taxi/table/path] LIMIT 100',
        ),
        (
            '* FROM %t LIMIT %p',
            ['//home/taxi/table/path', 100],
            '* FROM [//home/taxi/table/path] LIMIT 100',
        ),
        (
            '* FROM %t WHERE column = %p LIMIT %p',
            ['//home/taxi/table/path', 'value', 100],
            '* FROM [//home/taxi/table/path] WHERE column = "value" LIMIT 100',
        ),
        (
            '* FROM %t WHERE column = %p LIMIT %p',
            ['//home/taxi/table/path', True, 100],
            '* FROM [//home/taxi/table/path] WHERE column = true LIMIT 100',
        ),
        (
            '* FROM %t WHERE column = %p LIMIT %p',
            ['//home/taxi/table/path', 10, 100],
            '* FROM [//home/taxi/table/path] WHERE column = 10 LIMIT 100',
        ),
        (
            '* FROM %t WHERE column = %p LIMIT %p',
            ['//home/taxi/table/path', 10.5, 100],
            '* FROM [//home/taxi/table/path] WHERE column = 10.50000 '
            'LIMIT 100',
        ),
        (
            '* FROM %t WHERE column IN %p',
            ['//home/taxi/table/path', []],
            '* FROM [//home/taxi/table/path] WHERE column IN ()',
        ),
        (
            '* FROM %t WHERE column IN %p',
            ['//home/taxi/table/path', ['1']],
            '* FROM [//home/taxi/table/path] WHERE column IN ("1")',
        ),
        (
            '* FROM %t WHERE column IN %p',
            ['//home/taxi/table/path', ['1', '2', '3']],
            '* FROM [//home/taxi/table/path] WHERE column IN ("1", "2", "3")',
        ),
        (
            '* FROM %t WHERE column IN %p',
            ['//home/taxi/table/path', [1, 2, 3]],
            '* FROM [//home/taxi/table/path] WHERE column IN (1, 2, 3)',
        ),
        (
            '* FROM %t WHERE column IN %p',
            ['//home/taxi/table/path', [1, 6576030061]],
            '* FROM [//home/taxi/table/path] WHERE column IN (1, 6576030061)',
        ),
        (
            '* FROM %t WHERE column IN %p',
            ['//home/taxi/table/path', [1, '2', 3.5, True]],
            (
                '* FROM [//home/taxi/table/path] WHERE column IN '
                '(1, "2", 3.50000, true)'
            ),
        ),
        (
            '* FROM %t WHERE column IN %p',
            ['//home/taxi/table/path', [['1', '2'], ['3', '4']]],
            (
                '* FROM [//home/taxi/table/path] WHERE column IN '
                '(("1", "2"), ("3", "4"))'
            ),
        ),
        (
            '* FROM %t WHERE column IN %p',
            ['//home/taxi/table/path', [1.5, 2.5, 3.5]],
            (
                '* FROM [//home/taxi/table/path] WHERE column IN '
                '(1.50000, 2.50000, 3.50000)'
            ),
        ),
        (
            '* FROM %t WHERE column IN %p',
            ['//home/taxi/table/path', [False, True]],
            '* FROM [//home/taxi/table/path] WHERE column IN (false, true)',
        ),
        (
            '* FROM %t WHERE column = %p LIMIT %p',
            ['//home/taxi/table/path', 'va"lue', 100],
            '* FROM [//home/taxi/table/path] WHERE column = "va\\"lue" '
            'LIMIT 100',
        ),
        (
            '* FROM %t WHERE col%%umn = %p LIMIT %p',
            ['//home/taxi/table/path', 'value', 100],
            '* FROM [//home/taxi/table/path] WHERE col%umn = "value" '
            'LIMIT 100',
        ),
        (
            '* FROM [//home/taxi/table/path] WHERE c%%c = cc LIMIT 100',
            [],
            '* FROM [//home/taxi/table/path] WHERE c%c = cc LIMIT 100',
        ),
        (
            '* FROM [//home/taxi/table/path] WHERE c%%%%c = cc LIMIT 100',
            [],
            '* FROM [//home/taxi/table/path] WHERE c%%c = cc LIMIT 100',
        ),
    ],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_request_parametrized(
        taxi_archive_api,
        mockserver,
        dummy_replication,
        query_string,
        query_params,
        query_result,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/select_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/select_rows')
    def select_rows_repl(request):
        request_query = json.loads(request.headers['X-YT-Parameters'])['query']
        assert request_query == query_result
        return {'yt': 'response'}

    response = taxi_archive_api.post(
        'v1/yt/select_rows',
        json={
            'query': {
                'query_string': query_string,
                'query_params': query_params,
            },
            'replication_rules': [{'name': 'repl-name-both'}],
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json()['items'] == [{'yt': 'response'}]


@pytest.mark.parametrize(
    'query_string, query_params',
    [
        ('* FROM %t LIMIT 100', []),
        ('* FROM %p LIMIT 100', []),
        ('* FROM %q LIMIT 100', []),
        ('* FROM % LIMIT 100', []),
        ('%%% FROM [//home/taxi/table/path] LIMIT 100', []),
        ('* FROM %t LIMIT 100 %', ['//home/taxi/table/path']),
        ('* FROM %t LIMIT 100', ['//home/taxi/ta"ble/path']),
        ('* FROM %t LIMIT 100', ['//home/taxi/ta[ble/path']),
        ('* FROM %t LIMIT 100', ['//home/taxi/ta]ble/path']),
    ],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_wrong_request_parametrized(
        taxi_archive_api,
        mockserver,
        dummy_replication,
        query_string,
        query_params,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/select_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/select_rows')
    def select_rows_repl(request):
        assert False

    response = taxi_archive_api.post(
        'v1/yt/select_rows',
        json={
            'query': {
                'query_string': query_string,
                'query_params': query_params,
            },
            'replication_rules': [{'name': 'repl-name-both'}],
        },
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    'yt_replication_rules',
    [([{'name': 'repl-name-7', 'max_delay': 0}]), ([{'name': 'repl-name-7'}])],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_any_delay(
        taxi_archive_api, mockserver, dummy_replication, yt_replication_rules,
):
    @mockserver.json_handler('/yt/yt-test/api/v3/select_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/select_rows')
    def select_rows_repl(request):
        return {'from': 'yt'}

    response = taxi_archive_api.post(
        'v1/yt/select_rows',
        json={
            'query': {
                'query_string': '* FROM [//home/taxi/collections/tmp] LIMIT 1',
            },
            'replication_rules': yt_replication_rules,
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
    @mockserver.json_handler('/yt/yt-test/api/v3/select_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/select_rows')
    def select_rows(request):
        return mockserver.make_response()

    response = taxi_archive_api.post(
        'v1/yt/select_rows',
        json={
            'query': {
                'query_string': '* FROM [//home/taxi/collections/tmp] LIMIT 1',
            },
            'replication_rules': [{'name': 'repl-name-1', 'max_delay': 43200}],
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json() == {'source': 'yt-test', 'items': []}


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_parallel_requests(taxi_archive_api, mockserver, dummy_replication):
    @mockserver.json_handler('/yt/yt-test/api/v3/select_rows')
    def select_rows_test(request):
        return {'from': 'yt'}

    @mockserver.json_handler('/yt/yt-repl/api/v3/select_rows')
    def select_rows_repl(request):
        return {'from': 'yt'}

    response = taxi_archive_api.post(
        'v1/yt/select_rows',
        json={
            'query': {
                'query_string': '* FROM [//home/taxi/collections/tmp] LIMIT 1',
            },
            'replication_rules': [{'name': 'repl-name-1', 'max_delay': 0}],
            'parallel_requests': 1,
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json()['items'] == [{'from': 'yt'}]

    assert select_rows_test.times_called + select_rows_repl.times_called == 1


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
    @mockserver.json_handler('/yt/yt-test/api/v3/select_rows')
    def select_rows_yt_test(request):
        yt_parameters = json.loads(request.headers['X-YT-Parameters'])
        assert yt_parameters['timeout'] == (1000 if from_request else 2000)
        return {'from': 'yt'}

    @mockserver.json_handler('/yt/yt-repl/api/v3/select_rows')
    def select_rows_yt_repl(request):
        yt_parameters = json.loads(request.headers['X-YT-Parameters'])
        assert yt_parameters['timeout'] == (1000 if from_request else 10000)
        return {'from': 'yt'}

    request_json = {
        'query': {
            'query_string': '* FROM [//home/taxi/collections/tmp] LIMIT 1',
        },
        'replication_rules': [{'name': 'repl-name-1', 'max_delay': 0}],
    }
    if from_request:
        request_json['yt_timeout_ms'] = 1000

    response = taxi_archive_api.post('v1/yt/select_rows', json=request_json)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json()['items'] == [{'from': 'yt'}]

    assert select_rows_yt_test.wait_call()
    assert select_rows_yt_repl.wait_call()


@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_correct_request_bson(taxi_archive_api, mockserver, dummy_replication):
    @mockserver.json_handler('/yt/yt-test/api/v3/select_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/select_rows')
    def select_rows(request):
        return mockserver.make_response(YT_RESPONSE_YSON)

    response = taxi_archive_api.post(
        'v1/yt/select_rows',
        json={
            'query': {
                'query_string': '* FROM [//home/taxi/collections/tmp] LIMIT 1',
            },
            'replication_rules': [{'name': 'repl-name-1', 'max_delay': 43200}],
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
    @mockserver.json_handler('/yt/yt-test/api/v3/select_rows')
    @mockserver.json_handler('/yt/yt-repl/api/v3/select_rows')
    def select_rows(request):
        return mockserver.make_response(YT_RESPONSE_YSON)

    response = taxi_archive_api.post(
        'v2/yt/select_rows',
        json={
            'query': {
                'query_string': '* FROM [//home/taxi/collections/tmp] LIMIT 1',
            },
            'replication_rules': [{'name': 'repl-name-1', 'max_delay': 43200}],
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/x-yt-yson-binary'
    assert response.content == b'[' + YT_RESPONSE_YSON + b']'


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_no_param_query(taxi_archive_api, yt_client, dummy_replication):
    response = taxi_archive_api.post(
        'v1/yt/select_rows',
        json={'replication_rules': [{'name': 'rule_name', 'max_delay': 0}]},
    )
    assert response.status_code == 400


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_no_param_replication_rules(
        taxi_archive_api, yt_client, dummy_replication,
):
    response = taxi_archive_api.post(
        'v1/yt/select_rows', json={'query': {'query_string': 'query'}},
    )
    assert response.status_code == 400


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_empty_param_query(taxi_archive_api, yt_client, dummy_replication):
    response = taxi_archive_api.post(
        'v1/yt/select_rows',
        json={
            'query': {},
            'replication_rules': [{'name': 'rule_name', 'max_delay': 0}],
        },
    )
    assert response.status_code == 400


@pytest.mark.now('2018-02-16T15:00:00Z')
def test_empty_param_replication_rules(
        taxi_archive_api, yt_client, dummy_replication,
):
    response = taxi_archive_api.post(
        'v1/yt/select_rows',
        json={'query': {'query_string': 'query'}, 'replication_rules': []},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'yt_replication_rules',
    [
        (
            [
                {'name': 'repl-name-7', 'max_delay': 43200},
                {'name': 'repl-name-8', 'max_delay': 43200},
            ]
        ),
        (
            [
                {'name': 'repl-name-9', 'max_delay': 43200},
                {'name': 'repl-name-10', 'max_delay': 43200},
            ]
        ),
    ],
)
@pytest.mark.config(YT_HOSTS_UPDATE_ENABLED=True)
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_wrong_replication_rules(
        taxi_archive_api, yt_replication_rules, dummy_replication,
):
    response = taxi_archive_api.post(
        'v1/yt/select_rows',
        json={
            'query': {
                'query_string': '* FROM [//home/taxi/collections/tmp] LIMIT 1',
            },
            'replication_rules': yt_replication_rules,
        },
    )

    assert response.status_code == 503
