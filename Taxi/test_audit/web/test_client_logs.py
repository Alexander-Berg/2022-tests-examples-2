import pytest


@pytest.mark.parametrize(
    'data, query, expected_data_filename',
    [
        pytest.param(
            {}, {}, 'expected_default_params.json', id='check default params',
        ),
        pytest.param(
            {'system_name': 'tplatform'},
            {},
            'expected_logs_list.json',
            id='check list',
        ),
        pytest.param(
            {'limit': 1, 'system_name': 'tplatform'},
            {},
            'expected_logs_list_limit_1.json',
            id='check limit=1',
        ),
        pytest.param(
            {'skip': 1, 'system_name': 'tplatform'},
            {},
            'expected_logs_list_skip_1.json',
            id='check skip',
        ),
        pytest.param(
            {'query': {'exclude': ['set_tariff']}, 'system_name': 'tplatform'},
            {},
            'expected_logs_list_query_exclude.json',
            id='query exclude',
        ),
        pytest.param(
            {
                'query': {
                    'exclude': ['set_tariff'],
                    'actions': ['set_tariff'],
                },
                'system_name': 'tplatform',
            },
            {},
            'expected_logs_list_for_action.json',
            id='list for action',
        ),
        pytest.param(
            {'query': {'object_id': 'test_', 'actions': ['action_3']}},
            {},
            'expected_logs_list_for_regex.json',
            id='logs list for regex',
        ),
        pytest.param(
            {
                'system_name': 'system_audit',
                'query': {
                    'exclude': ['delete_value'],
                    'actions': ['update_value'],
                    'login': 'deoevgen',
                },
            },
            {},
            'test_exclude.json',
            id='test exclude',
        ),
        pytest.param(
            {
                'system_name': 'system_audit',
                'query': {'object_id': 'create_test_logins'},
            },
            {},
            'test_object_id.json',
            id='object id',
        ),
        pytest.param(
            {
                'system_name': 'system_audit',
                'query': {
                    'date_from': '2020-11-28T12:12:12.000+0300',
                    'date_till': '2020-11-29T12:00:00.000+0300',
                },
            },
            {},
            'test_date.json',
            id='check date',
        ),
        pytest.param(
            {'system_name': 'system_audit', 'limit': 2, 'skip': 2},
            {},
            'test_skip.json',
            id='test skip data',
        ),
        pytest.param(
            {'system_name': 'tplatform', 'query': {'actions': ['set_tariff']}},
            {'tplatform_namespace': 'taxi'},
            'test_tplatform_namespace.json',
            id='tplatform namespace check filters',
        ),
        pytest.param(
            {'query': {'actions': ['set_tariff']}},
            {'tplatform_namespace': 'taxi'},
            'test_tplatform_namespace.json',
            id='tplatform namespace check actions',
        ),
        pytest.param(
            {
                'system_name': 'tplatform',
                'query': {'exclude': ['set_tariff', 'delete_value']},
            },
            {'tplatform_namespace': 'taxi'},
            'expected_logs_list_pg_query_exclude.json',
            id='list pg query exclude',
        ),
    ],
)
@pytest.mark.pgsql('audit_events', files=['test_retrieve_logs.sql'])
async def test_retrieve_logs_response(
        data, query, expected_data_filename, web_app_client, load_json,
):
    expected_data = load_json(expected_data_filename)
    response = await web_app_client.request(
        'POST', '/v1/client/logs/retrieve/', json=data, params=query,
    )
    assert response.status == 200
    response_json = await response.json()
    response_json.sort(key=lambda x: x['id'])
    expected_data.sort(key=lambda x: x['id'])
    assert response_json == expected_data


async def test_retrieve_logs_403_response(web_app_client):
    response = await web_app_client.request(
        'POST',
        '/v1/client/logs/retrieve/',
        json={'system_name': 'tariff-editor'},
        params={'tplatform_namespace': 'taxi'},
    )
    assert response.status == 403
    response_json = await response.json()
    expected = {
        'status': 'error',
        'message': 'Access to non-tplatform logs is forbidden',
        'code': 'ACCESS_FORBIDDEN',
    }
    assert response_json == expected


@pytest.mark.parametrize(
    'query, data, expected_data_filename',
    [
        ({'log_id': 'object_id'}, {}, 'expected_pg_log_retrieve.json'),
        (
            {'log_id': 'object_id_7'},
            {'tplatform_namespace': 'taxi'},
            'expected_pg_log_with_namespace_retrieve.json',
        ),
    ],
)
@pytest.mark.config(AUDIT_FEATURES={'diff': True})
@pytest.mark.pgsql('audit_events', files=['test_retrieve_logs.sql'])
async def test_retrieve_pg_log_response(
        web_app_client, load_json, query, data, expected_data_filename,
):
    expected_data = load_json(expected_data_filename)
    response = await web_app_client.request(
        'GET', f'/v1/client/logs/retrieve/', json=data, params=query,
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_data


@pytest.mark.pgsql('audit_events', files=['test_retrieve_logs.sql'])
async def test_retrieve_log_403_response(web_app_client):
    response = await web_app_client.request(
        'GET',
        '/v1/client/logs/retrieve/',
        params={'log_id': 'object_id_8', 'tplatform_namespace': 'taxi'},
    )
    assert response.status == 403
    response_json = await response.json()
    expected = {
        'status': 'error',
        'message': 'Access to non-tplatform logs is forbidden',
        'code': 'ACCESS_FORBIDDEN',
    }
    assert response_json == expected


async def test_retrieve_log_404_response(web_app_client):
    response = await web_app_client.request(
        'GET',
        '/v1/client/logs/retrieve/',
        params={'log_id': '100000000000000000000000'},
    )
    assert response.status == 404
    response_json = await response.json()
    expected = {
        'status': '404',
        'message': 'Audit log not found',
        'code': 'not_found',
    }
    assert response_json == expected


@pytest.mark.parametrize(
    'data, expected_data',
    [
        pytest.param(
            {
                'date_from': '2020-11-02',
                'date_to': '2020-12-02',
                'action': 'set_tariff',
            },
            'Number logs: 0\r\n'
            'Startup parameter\r\n'
            'Action: set_tariff\r\n'
            'Start date: 2020-11-02 03:00:00+03:00\r\n'
            'Ending date: 2020-12-03 03:00:00+03:00\r\n'
            'Change time;Ticket;Login;Record id;Action;Key;'
            'Key description;Additionally;Value\r\n',
            id='request mongo export',
        ),
        pytest.param(
            {
                'date_from': '2020-11-02',
                'date_to': '2020-12-02',
                'action': 'set_tariff',
                'system_name': 'tplatform',
            },
            'Number logs: 1\r\n'
            'Startup parameter\r\n'
            'Action: set_tariff\r\n'
            'Start date: 2020-11-02 03:00:00+03:00\r\n'
            'Ending date: 2020-12-03 03:00:00+03:00\r\n'
            'Change time;Ticket;Login;Record id;Action;Key;'
            'Key description;Additionally;Value\r\n'
            '2020-11-30 15:00:00+03:00;ticket-2;'
            'vstimchenko;object_id_6;set_tariff;body.a;'
            ';some_object;wat??\r\n',
            id='request postgres export',
        ),
        pytest.param(
            {
                'date_from': '2020-11-02',
                'date_to': '2020-12-02',
                'action': 'set_tariff',
            },
            'Number logs: 0\r\n'
            'Startup parameter\r\n'
            'Action: set_tariff\r\n'
            'Start date: 2020-11-02 03:00:00+03:00\r\n'
            'Ending date: 2020-12-03 03:00:00+03:00\r\n'
            'Change time;Ticket;Login;Record id;Action;Key;'
            'Key description;Additionally;Value\r\n',
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={'reading_flow': 'mongo_only'},
            ),
            id='request mongo export with no system name',
        ),
        pytest.param(
            {
                'date_from': '2020-11-02',
                'date_to': '2020-12-02',
                'action': 'set_tariff',
            },
            'Number logs: 0\r\n'
            'Startup parameter\r\n'
            'Action: set_tariff\r\n'
            'Start date: 2020-11-02 03:00:00+03:00\r\n'
            'Ending date: 2020-12-03 03:00:00+03:00\r\n'
            'Change time;Ticket;Login;Record id;Action;Key;'
            'Key description;Additionally;Value\r\n',
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={'reading_flow': 'postgres_only'},
            ),
            id='request postgres export with no system name',
        ),
    ],
)
@pytest.mark.pgsql('audit_events', files=['test_retrieve_logs.sql'])
async def test_logs_export_response(web_app_client, data, expected_data):
    response = await web_app_client.request(
        'POST', '/v1/client/logs/export_to_csv/', json=data,
    )
    assert response.status == 200
    assert expected_data == await response.text()
