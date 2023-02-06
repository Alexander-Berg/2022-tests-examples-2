import bson
import pytest

from taxi.clients import audit as client_audit


@pytest.mark.parametrize(
    'data, expected_data_filename',
    [
        ({'query': {}}, 'expected_logs_list.json'),
        (
            {
                'query': {},
                'sort': [{'field': 'timestamp', 'direction': 'desc'}],
            },
            'expected_logs_list_sort_timestamp_desc.json',
        ),
        (
            {'query': {}, 'sort': [{'field': 'id', 'direction': 'desc'}]},
            'expected_logs_list_sort_id_desc.json',
        ),
        ({'query': {}, 'limit': 1}, 'expected_logs_list_limit_1.json'),
        (
            {'query': {'actions': ['action_1', 'action_2']}},
            'expected_logs_list_query_actions.json',
        ),
        (
            {'query': {'id_till': '000000000000000000000003'}},
            'expected_logs_list_query_id_till.json',
        ),
        (
            {
                'query': {
                    'arguments_ids': [
                        '000000000000000000000003',
                        'argument_id',
                    ],
                },
                'sort': [{'field': 'timestamp', 'direction': 'asc'}],
            },
            'expected_logs_list_query_arguments_ids.json',
        ),
        ({'query': {'arguments_ids': []}}, 'expected_empty_logs_list.json'),
        ({'query': {}, 'fields': []}, 'expected_logs_empty_projections.json'),
        (
            {'query': {}, 'fields': ['arguments._id']},
            'expected_logs_projections.json',
        ),
        pytest.param(
            {
                'query': {
                    'date_from': '2018-01-30T20:00:00+03:00',
                    'system_name': 'tplatform',
                },
                'limit': 1,
            },
            'expected_logs_pg_only.json',
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={
                    'writing_flow': 'postgres_only',
                    'reading_flow': 'postgres_only',
                },
            ),
            id='test pg only',
        ),
    ],
)
@pytest.mark.pgsql('audit_events', files=['test_robot_logs.sql'])
async def test_retrieve_logs_response(
        data, expected_data_filename, web_app_client, load_json, web_context,
):
    await web_context.refresh_caches()
    expected_data = load_json(expected_data_filename)
    response = await web_app_client.request(
        'POST', '/v1/robot/logs/retrieve/', json=data, params={}, headers={},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_data


@pytest.mark.config(
    AUDIT_LOG_SIZE_SETTINGS={
        'max_size': 417,
        'actions': {'__default__': ['response', 'request', 'summary']},
        'mock_phrase': '**Too long size bson doc, max_size: {max_size}b**',
        'enable_feature': True,
    },
)
@pytest.mark.parametrize(
    'created_log_json, status',
    [
        ('test_create_mongo_request.json', 200),
        ('test_exist_request.json', 409),
        ('test_big_size_request.json', 200),
        ('test_create_new_pg_request.json', 404),
        ('test_create_exist_action_pg_request.json', 200),
        ('test_big_size_request_pg.json', 200),
        ('test_exist_pg_request.json', 409),
        ('test_validation_platform_namespace.json', 200),
        pytest.param(
            'test_tariff_editor_mongo.json',
            200,
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={
                    'writing_flow': 'mongo_only',
                    'reading_flow': 'mongo_only',
                },
            ),
        ),
        pytest.param(
            'test_tariff_editor_pg.json',
            200,
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={
                    'writing_flow': 'postgres_only',
                    'reading_flow': 'postgres_only',
                },
            ),
        ),
        pytest.param(
            'test_tariff_editor_mongo_and_pg.json',
            200,
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={
                    'writing_flow': 'mongo_and_postgres',
                    'reading_flow': 'mongo_only',
                },
            ),
        ),
        pytest.param(
            'test_tariff_editor_mongo_and_pg.json',
            200,
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={
                    'writing_flow': 'mongo_and_postgres',
                    'reading_flow': 'postgres_only',
                },
            ),
        ),
        pytest.param(
            'test_no_system_name_mongo.json',
            200,
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={
                    'writing_flow': 'mongo_only',
                    'reading_flow': 'mongo_only',
                },
            ),
        ),
        pytest.param(
            'test_no_system_name_pg.json',
            200,
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={
                    'writing_flow': 'postgres_only',
                    'reading_flow': 'postgres_only',
                },
            ),
        ),
    ],
)
@pytest.mark.pgsql('audit_events', files=['test_create_logs.sql'])
async def test_create_log_response(
        web_app_client,
        created_log_json,
        status,
        patch,
        load_json,
        pgsql,
        mongo,
        web_context,
):
    case_data = load_json(created_log_json)
    request_data = case_data['request_data']
    expected_data = case_data.get('expected_data')
    response = await web_app_client.request(
        'POST', f'/v1/robot/logs/', json=request_data, params={}, headers={},
    )

    assert response.status == status
    if response.status == 200:
        response_json = await response.json()
        log_id = response_json['id']
        system_name = request_data.get('system_name')
        if not system_name:
            system_name = client_audit.TARIFF_EDITOR_SYSTEM_NAME
        if system_name == client_audit.TARIFF_EDITOR_SYSTEM_NAME:
            writing_flow = web_context.config.AUDIT_DB_SETTINGS[
                client_audit.AUDIT_DB_WRITING_FLOW
            ]
            if writing_flow == client_audit.AUDIT_DB_MONGO_ONLY:
                await check_mongo_log(expected_data, log_id, mongo)
            elif writing_flow == client_audit.AUDIT_DB_POSTGRES_ONLY:
                await check_pg_log(
                    request_data, system_name, pgsql, log_id, web_context,
                )
            elif writing_flow == client_audit.AUDIT_DB_MONGO_AND_POSTGRES:
                reading_flow = web_context.config.AUDIT_DB_SETTINGS[
                    client_audit.AUDIT_DB_READING_FLOW
                ]
                if reading_flow == client_audit.AUDIT_DB_POSTGRES_ONLY:
                    request_data['id'] = log_id
                await check_mongo_log(expected_data, log_id, mongo)
                if reading_flow == client_audit.AUDIT_DB_MONGO_ONLY:
                    log_id = f'{system_name}:{log_id}'
                await check_pg_log(
                    request_data, system_name, pgsql, log_id, web_context,
                )
        else:
            await check_pg_log(
                request_data, system_name, pgsql, log_id, web_context,
            )


async def check_mongo_log(expected_data, log_id, mongo):
    if ':' in log_id:
        log_id = log_id.split(':')[-1]
    data = {'_id': bson.ObjectId(log_id)}
    log = await mongo.log_admin.find_one(data)
    assert log == expected_data


async def check_pg_log(created_data, system_name, pgsql, log_id, web_context):
    platform_namespace = created_data.get('tplatform_namespace')
    assert log_id.startswith(f'{system_name}:')
    cursor = pgsql['audit_events'].cursor()
    query = f'SELECT * from audit_events.logs where id = \'{log_id}\';'
    cursor.execute(query)
    result = [row for row in cursor]
    assert len(result) == 1
    assert len(result[0]) == 12
    args = result[0][7]
    assert isinstance(args, dict)
    assert result[0][10] == platform_namespace
    request_id = created_data.get('request_id')
    if request_id == 'test_big_size_document':
        assert args == {
            'response': '**Too long size bson doc, max_size: 417b**',
        }
    else:
        assert result[0][8] == 'arg_id'
    action = created_data['action']
    cached_system = web_context.systems_cache.get_by_name(system_name)
    system_id = cached_system.id_
    query_kwargs = {'action': action, 'system_id': system_id}
    query, args = web_context.sqlt('actions/fetch.sqlt', query_kwargs)
    async with web_context.pg.master_pool.acquire() as conn:
        rows = await conn.fetch(query, *args)
    result = [row for row in rows]
    assert len(result) == 1


@pytest.mark.parametrize(
    'data, expected_response',
    [
        pytest.param(
            {
                'query': {
                    'action': 'exists_action',
                    'actions': ['exists_action'],
                    'system_name': 'exists_system',
                    'ticket_queue': 'ticket',
                    'ticket': 'ticket-1',
                    'id': 'exist_log_1',
                },
                'secondary': True,
                'sort': [{'field': 'id', 'direction': 'desc'}],
                'fields': ['id', 'login', 'arguments', 'system_name'],
            },
            [
                {
                    'arguments': {
                        '_id': '1',
                        'body': {'a': 'wat?'},
                        'request': {'home_zone': 'ru'},
                    },
                    'id': 'exist_log_1',
                    'login': 'deoevgen',
                    'system_name': 'exists_system',
                },
            ],
        ),
        pytest.param(
            {
                'query': {'system_name': 'exists_system'},
                'secondary': False,
                'limit': 1,
                'skip': 1,
                'fields': ['id', 'login', 'arguments', 'system_name'],
            },
            [
                {
                    'arguments': {'_id': '2', 'body': {'a': 'wat?'}},
                    'id': 'exist_log_2',
                    'login': 'deoevgen',
                    'system_name': 'exists_system',
                },
            ],
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={'reading_flow': 'postgres_only'},
            ),
        ),
        pytest.param(
            {
                'query': {
                    'system_name': 'tplatform',
                    'tplatform_namespace': 'taxi',
                },
            },
            [
                {
                    'action': 'exists_action',
                    'arguments': {},
                    'id': 'exist_log_3',
                    'login': 'antonvasyuk',
                    'object_id': 'create_test_logins_3',
                    'request_id': 'exist_request_id_3',
                    'system_name': 'tplatform',
                    'ticket': 'ticket-2',
                    'timestamp': '2022-01-14T17:00:00+03:00',
                    'tplatform_namespace': 'taxi',
                    'revision': 3,
                },
            ],
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={'reading_flow': 'postgres_only'},
            ),
        ),
        pytest.param(
            {
                'older_than_revision': 4,
                'query': {'system_name': 'exists_system'},
            },
            [],
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={'reading_flow': 'postgres_only'},
            ),
            id='test revision, empty response',
        ),
        pytest.param(
            {
                'older_than_revision': 1,
                'query': {'system_name': 'exists_system'},
                'limit': 1000,
            },
            [
                {
                    'action': 'exists_action',
                    'arguments': {'_id': '2', 'body': {'a': 'wat?'}},
                    'id': 'exist_log_2',
                    'login': 'deoevgen',
                    'object_id': 'create_test_logins_2',
                    'request_id': 'exist_request_id_2',
                    'revision': 2,
                    'system_name': 'exists_system',
                    'ticket': 'ticket-1',
                    'timestamp': '2020-11-28T03:00:00+03:00',
                },
            ],
            marks=pytest.mark.config(
                AUDIT_DB_SETTINGS={'reading_flow': 'postgres_only'},
            ),
            id='test revision',
        ),
    ],
)
@pytest.mark.pgsql('audit_events', files=['test_robot_logs.sql'])
async def test_robot_logs_response(web_app_client, data, expected_response):
    response = await web_app_client.request(
        'POST', '/v1/robot/logs/retrieve/', json=data, params={}, headers={},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response
