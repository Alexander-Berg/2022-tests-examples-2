import json

import pytest

PATH_PREFIX = (
    'taxi/uservices/services/logistic-platform-processing/'
    'testsuite/tests_logistic_platform_processing/static/test_admin/'
)

DEFAULT_EMPLOYER = {
    'employer_type': 'default',
    'employer_code': 'new_employer',
    'employer_meta': {
        'default_inn': '9876543214',
        'ndd_route_policy': 'strizh_only',
        'registry': {'config_template': 'nespresso', 'separator': ','},
        'brand_name_new': {
            'brand_name_ru': 'тикток',
            'brand_name_eng': 'tiktok',
            'legal_name': 'some legal name',
            'brand_name_genitive': 'name in genitive',
        },
        'has_advanced_billing': True,
    },
}

DEFAULT_RESPONSE_FROM_LOGISTIC_PLATFORM = (
    'Response that will not be checked '
    'in uservices handlers, is only proxied to user'
)


@pytest.fixture(name='payload_storage')
def _payload_storage():
    class PayloadStorage:
        def __init__(self):
            self.payload = None

        def set_payload(self, new_payload):
            self.payload = new_payload

        def get_payload(self):
            return self.payload

    return PayloadStorage()


@pytest.fixture(name='mock_bg_info')
def _mock_bg_info(mockserver, load_json):
    @mockserver.json_handler('/logistic-platform-uservices/api/admin/bg/info')
    def mock_bg_info(request):
        return load_json('platform_responses/get_robots_info.json')

    return mock_bg_info


@pytest.fixture(name='mock_bg_upsert')
def _mock_bg_upsert(mockserver, payload_storage):
    @mockserver.json_handler(
        '/logistic-platform-uservices/api/admin/bg/upsert',
    )
    def mock_bg_upsert(request):
        assert request.json['backgrounds'] == [payload_storage.get_payload()]
        return mockserver.make_response()

    return mock_bg_upsert


@pytest.fixture(name='mock_platform_ds')
def _mock_platform_ds(mockserver, load, payload_storage):
    @mockserver.json_handler('/logistic-platform-uservices/platform/ds')
    def mock_platform_ds(request):
        request_data = request.get_data().decode('utf-8')
        response_xml = str()
        if payload_storage.get_payload() is not None:
            response_xml = payload_storage.get_payload()
        elif request_data.find('<request type="getOrdersStatus">') != -1:
            response_xml = load('platform_responses/ds_order_status.xml')
        elif request_data.find('<request type="getOrderHistory">') != -1:
            response_xml = load('platform_responses/ds_order_history.xml')
        elif request_data.find('<request type="createOrder">') != -1:
            response_xml = load('platform_responses/ds_create_order.xml')
        elif request_data.find('<request type="callCourier">') != -1:
            response_xml = DEFAULT_RESPONSE_FROM_LOGISTIC_PLATFORM
        else:
            raise ValueError('unsupported request')

        return mockserver.make_response(
            response=response_xml, content_type='application/xml',
        )

    return mock_platform_ds


def _get_robot_from_response(predicate):
    with open(
            PATH_PREFIX + 'platform_responses/get_robots_info.json', 'r',
    ) as json_file:
        robots = json.load(json_file)['rt_backgrounds']
        for robot in robots:
            if predicate(robot) is True:
                return robot
    return None


def _build_modify_command(command_id, **kwargs):
    return {
        'id': command_id,
        'arguments': [
            {'name': name, 'value': value} for name, value in kwargs.items()
        ],
    }


def _build_get_info_command(command_id, **kwargs):
    return {
        'data': {
            'id': command_id,
            'arguments': [
                {'name': name, 'value': value}
                for name, value in kwargs.items()
            ],
        },
    }


@pytest.mark.config(
    LOGISTIC_PLATFORM_CONTROL_COMMANDS_SETTINGS={
        'allow_platform_ds_commands': False,
    },
)
async def test_admin_developers_commands_schema_without_ds_commands(
        taxi_logistic_platform_processing, load_json,
):
    response = await taxi_logistic_platform_processing.get(
        '/admin/logistic-platform-processing/commands/schema',
    )
    assert response.status == 200
    assert response.json() == load_json('commands_schema_without_ds.json')


@pytest.mark.config(
    LOGISTIC_PLATFORM_CONTROL_COMMANDS_SETTINGS={
        'known_robots': ['robot_1', 'robot_2', 'robot_3'],
    },
)
async def test_admin_developers_commands_schema_robot_name_allowed_values(
        taxi_logistic_platform_processing,
):
    response = await taxi_logistic_platform_processing.get(
        '/admin/logistic-platform-processing/commands/schema',
    )
    assert response.status == 200
    for command_schema in response.json()['commands']:
        for argument_schema in command_schema['arguments']:
            if argument_schema['name'] == 'robot_name':
                assert argument_schema['allowed_values'] == [
                    'robot_1',
                    'robot_2',
                    'robot_3',
                ]


@pytest.mark.config(
    LOGISTIC_PLATFORM_CONTROL_COMMANDS_SETTINGS={
        'allow_platform_ds_commands': True,
    },
)
async def test_admin_developers_commands_schema_with_ds_commands(
        taxi_logistic_platform_processing, load_json,
):
    response = await taxi_logistic_platform_processing.get(
        '/admin/logistic-platform-processing/commands/schema',
    )
    assert response.status == 200
    commands_schema = load_json('commands_schema_without_ds.json')
    ds_commands_schema = load_json('commands_schema_ds_only.json')
    commands_schema['commands'] += ds_commands_schema
    assert response.json() == commands_schema


@pytest.mark.parametrize(
    'file_with_invalid_payload_from_platform, expected_status_code',
    [
        (None, 200),
        ('platform_responses/get_robots_info.json', 500),
        ('invalid_platform_responses/ds_order_history.xml', 500),
        ('invalid_platform_responses/ds_order_status.xml', 500),
    ],
)
async def test_admin_developers_commands_do__get_checkpoints(
        taxi_logistic_platform_processing,
        mockserver,
        load,
        payload_storage,
        mock_platform_ds,
        file_with_invalid_payload_from_platform,
        expected_status_code,
):
    if file_with_invalid_payload_from_platform is not None:
        payload_storage.set_payload(
            load(file_with_invalid_payload_from_platform),
        )
    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/get-info/developer',
        params={'environment': 'testing'},
        json=_build_get_info_command(
            'get_checkpoints',
            request_id='38ccaad0-29c3-4605-a87f-fc6bd77b767d',
        ),
    )
    assert response.status == expected_status_code
    if response.status == 200:
        assert response.json()['command_response'] == load(
            'commands/get_checkpoints.txt',
        )


@pytest.mark.parametrize(
    'table_name, expected_payload,',
    [
        (
            'some_table',
            {
                'bp_type': 'yt_dumper',
                'bp_name': 'some_table' + '_export',
                'bp_settings': {
                    'db_name': 'main-db',
                    'event_id_column': 'history_event_id',
                    'yt_cluster': 'hahn',
                    'table_name': 'some_table',
                },
            },
        ),
        (
            'employers_history',
            _get_robot_from_response(
                lambda robot: robot['bp_type'] == 'yt_dumper'
                and robot['bp_settings']['table_name'] == 'employers_history',
            ),
        ),
    ],
)
async def test_admin_developers_commands_do__create_export(
        taxi_logistic_platform_processing,
        mockserver,
        load_json,
        table_name,
        expected_payload,
        mock_bg_info,
        payload_storage,
        mock_bg_upsert,
):
    standart_export_robot_settings = {
        'db_define_schema': True,
        'optimize_for_scan': True,
        'yt_dir': '//home/taxi/testing/export/{}/{}'.format(
            'taxi-logistic-platform-testing', table_name,
        ),
        'quantum': 100000,
        'period': '10m',
    }
    expected_payload['bp_enabled'] = True
    expected_payload['bp_settings'].update(standart_export_robot_settings)
    payload_storage.set_payload(expected_payload)

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=_build_modify_command('create_export', table_name=table_name),
    )
    assert response.status == 200
    assert response.json()['command_response'] == 'OK'


@pytest.mark.parametrize(
    'robot_name, response_code, expected_payload,',
    [
        (
            'employers_history',
            200,
            _get_robot_from_response(
                lambda robot: robot['bp_name'] == 'employers_history',
            ),
        ),
        ('non_existent_name', 400, None),
    ],
)
async def test_admin_developers_commands_do__move_robot(
        taxi_logistic_platform_processing,
        mockserver,
        load_json,
        robot_name,
        response_code,
        expected_payload,
        mock_bg_info,
        payload_storage,
        mock_bg_upsert,
):
    if expected_payload is not None:
        host_filter = {'host_pattern': 'new_pattern'}
        expected_payload['bp_settings']['host_filter'].update(host_filter)
    payload_storage.set_payload(expected_payload)

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=_build_modify_command(
            'move_robot', robot_name=robot_name, host_pattern='new_pattern',
        ),
    )
    assert response.status == response_code
    if response.status == 200:
        assert response.json()['command_response'] == 'OK'


async def test_admin_developers_commands_do__disable_robot(
        taxi_logistic_platform_processing,
        mockserver,
        load_json,
        mock_bg_info,
        payload_storage,
        mock_bg_upsert,
):
    expected_payload = _get_robot_from_response(
        lambda robot: robot['bp_name'] == 'billing_payments_builder',
    )
    expected_payload['bp_enabled'] = False
    payload_storage.set_payload(expected_payload)

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=_build_modify_command(
            'disable_robot', robot_name='billing_payments_builder',
        ),
    )
    assert response.status == 200
    assert response.json()['command_response'] == 'OK'


async def test_admin_developers_commands_do__enable_robot(
        taxi_logistic_platform_processing,
        mockserver,
        load_json,
        mock_bg_info,
        payload_storage,
        mock_bg_upsert,
):
    expected_payload = _get_robot_from_response(
        lambda robot: robot['bp_name'] == 'events_journal_watcher-S7',
    )
    expected_payload['bp_enabled'] = True
    payload_storage.set_payload(expected_payload)

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=_build_modify_command(
            'enable_robot', robot_name='events_journal_watcher-S7',
        ),
    )
    assert response.status == 200
    assert response.json()['command_response'] == 'OK'


@pytest.mark.parametrize(
    'invalid_payload_from_platform, expected_status_code',
    [(None, 200), ('<is not valid xml file', 500)],
)
async def test_admin_developers_commands_do__create_market_express(
        taxi_logistic_platform_processing,
        mockserver,
        load,
        payload_storage,
        mock_platform_ds,
        invalid_payload_from_platform,
        expected_status_code,
):
    if invalid_payload_from_platform is not None:
        payload_storage.set_payload(invalid_payload_from_platform)

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=_build_modify_command('create_market_express_order'),
    )
    assert response.status == expected_status_code
    if response.status == 200:
        assert response.json()['command_response'] == (
            'a94de009-e2fc-4083-bc77-40122fa5ba4c\n'
            '504de009-e2fc-4083-bc77-40122fa5ba4c\n'
        )


async def test_admin_developers_commands_do__call_courier(
        taxi_logistic_platform_processing, mockserver, load, mock_platform_ds,
):

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=_build_modify_command(
            'call_courier', request_id='ae02d158-d962-4d8b-8ad1-9201ea5a5599',
        ),
    )
    assert response.status == 200
    assert (
        response.json()['command_response']
        == DEFAULT_RESPONSE_FROM_LOGISTIC_PLATFORM
    )


async def test_admin_developers_commands_do__update_robot(
        taxi_logistic_platform_processing,
        mockserver,
        load_json,
        payload_storage,
        mock_bg_upsert,
):
    any_robot = _get_robot_from_response(lambda robot: True)
    payload_storage.set_payload(any_robot)

    request_json = _build_modify_command(
        'update_robot', json=json.dumps(any_robot),
    )
    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=request_json,
    )
    assert response.status == 200
    assert response.json()['command_response'] == 'OK'

    request_json['arguments'][0]['value'] += 'non_valid_str'
    fail_response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=request_json,
    )
    assert fail_response.status == 400


@pytest.mark.parametrize(
    'robot_name, response_json',
    [
        (
            'billing_finalization',
            {
                'command_response': _get_robot_from_response(
                    lambda robot: robot['bp_name'] == 'billing_finalization',
                ),
            },
        ),
        (
            'nonexistent_robot',
            {'error_info': 'there is no nonexistent_robot robot'},
        ),
    ],
)
async def test_admin_developers_commands_do__get_robot_info(
        taxi_logistic_platform_processing,
        mockserver,
        load_json,
        mock_bg_info,
        robot_name,
        response_json,
):
    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/get-info/developer',
        params={'environment': 'testing'},
        json=_build_get_info_command('get_robot_info', robot_name=robot_name),
    )
    assert response.status == 200
    for key, value in response_json.items():
        assert response.json()[key] == value


async def test_admin_developers_commands_do__get_robots_info(
        taxi_logistic_platform_processing, mockserver, load_json, mock_bg_info,
):
    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/get-info/developer',
        params={'environment': 'testing'},
        json=_build_get_info_command('get_robots_info'),
    )
    assert response.status == 200
    assert (
        response.json()['command_response']
        == load_json('platform_responses/get_robots_info.json')[
            'rt_backgrounds'
        ]
    )


@pytest.mark.parametrize(
    'is_internal, request_id',
    [
        (True, 'ae02d158-d962-4d8b-8ad1-9201ea5a5599'),
        (False, 'ae02d158-d962-4d8b-8ad1-9201ea5a5599'),
        (True, 'not_uuid4'),
        (False, 'not_uuid4'),
    ],
)
async def test_admin_developers_commands_do__get_platform_statuses(
        taxi_logistic_platform_processing,
        mockserver,
        load_json,
        is_internal,
        request_id,
):
    response_from_platform = load_json(
        'platform_responses/get_platform_statuses.json',
    )

    @mockserver.json_handler(
        '/logistic-platform-uservices/api/b2b/platform/request/history',
    )
    def _b2b_request_history(request):
        assert is_internal is False
        if request_id == 'not_uuid4':
            return mockserver.make_response(
                status=500, response='{"message": "some_error"}',
            )
        return response_from_platform

    @mockserver.json_handler(
        '/logistic-platform-uservices/api/internal/platform/request/history',
    )
    def _internal_request_history(request):
        assert is_internal is True
        if request_id == 'not_uuid4':
            return mockserver.make_response(
                status=500, response='{"message": "some_error"}',
            )
        return response_from_platform

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/get-info/developer',
        params={'environment': 'testing'},
        json=_build_get_info_command(
            'get_platform_statuses',
            request_id=request_id,
            internal=is_internal,
        ),
    )
    assert response.status == 200
    response_json = response.json()

    if 'command_response' in response_json:
        assert response_json['command_response'] == response_from_platform
    else:
        assert response_json['error_info'] == {'message': 'some_error'}


@pytest.mark.parametrize(
    'is_internal, request_id',
    [
        (True, 'ae02d158-d962-4d8b-8ad1-9201ea5a5599'),
        (False, 'ae02d158-d962-4d8b-8ad1-9201ea5a5599'),
        (True, 'not_uuid4'),
        (False, 'not_uuid4'),
    ],
)
async def test_admin_developers_commands_do__get_platform_request(
        taxi_logistic_platform_processing,
        mockserver,
        load_json,
        is_internal,
        request_id,
):
    response_from_platform = load_json(
        'platform_responses/get_platform_request.json',
    )

    @mockserver.json_handler(
        '/logistic-platform-uservices/api/b2b/platform/request/info',
    )
    def _b2b_request_info(request):
        assert is_internal is False
        if request_id == 'not_uuid4':
            return mockserver.make_response(
                status=500, response='{"message": "another_error"}',
            )
        return response_from_platform

    @mockserver.json_handler(
        '/logistic-platform-uservices/api/internal/platform/request/info',
    )
    def _internal_request_info(request):
        assert is_internal is True
        if request_id == 'not_uuid4':
            return mockserver.make_response(
                status=500, response='{"message": "another_error"}',
            )
        return response_from_platform

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/get-info/developer',
        params={'environment': 'testing'},
        json=_build_get_info_command(
            'get_platform_request',
            request_id=request_id,
            internal=is_internal,
        ),
    )
    assert response.status == 200
    response_json = response.json()

    if 'command_response' in response_json:
        assert response_json['command_response'] == response_from_platform
    else:
        assert response_json['error_info'] == {'message': 'another_error'}


async def test_admin_developers_commands_do__deep_remove_request(
        taxi_logistic_platform_processing, mockserver,
):
    @mockserver.json_handler(
        '/logistic-platform-uservices/platform/requests/deep_remove',
    )
    def _deep_remove(request):
        return ''

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=_build_modify_command(
            'deep_remove_request',
            request_id='ae02d158-d962-4d8b-8ad1-9201ea5a5599',
        ),
    )
    assert response.status == 200
    assert response.json()['command_response'] == 'OK'


async def test_admin_developers_commands_do__create_employer(
        taxi_logistic_platform_processing, mockserver,
):
    @mockserver.json_handler(
        '/logistic-platform-uservices/api/admin/employer/create',
    )
    def _create_employer(request):
        assert request.json == DEFAULT_EMPLOYER
        return ''

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=_build_modify_command(
            'create_employer', employer_code='new_employer',
        ),
    )
    assert response.status == 200
    assert response.json()['command_response'] == 'OK'


async def test_admin_developers_commands_do__update_employer(
        taxi_logistic_platform_processing, mockserver,
):
    @mockserver.json_handler(
        '/logistic-platform-uservices/api/admin/employer/update',
    )
    def _update_employer(request):
        assert request.json == DEFAULT_EMPLOYER
        return ''

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=_build_modify_command(
            'update_employer', employer_code='new_employer',
        ),
    )
    assert response.status == 200
    assert response.json()['command_response'] == 'OK'


async def test_admin_developers_commands_do__add_robot(
        taxi_logistic_platform_processing,
        mockserver,
        load_json,
        payload_storage,
        mock_bg_upsert,
):
    expected_payload = {
        'bp_enabled': False,
        'bp_type': 'new_robot_type',
        'bp_name': 'new_robot_name',
        'bp_settings': {
            'bp_description': '',
            'groupping_attributes': [],
            'host_filter': {
                'fqdn_host_pattern': '',
                'ctype': '',
                'host_pattern': '',
            },
            'period': '1m',
            'freshness': '1m',
        },
    }
    payload_storage.set_payload(expected_payload)

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=_build_modify_command(
            'add_robot',
            robot_name='new_robot_name',
            robot_type='new_robot_type',
        ),
    )
    assert response.status == 200
    assert response.json()['command_response'] == 'OK'


@pytest.mark.parametrize(
    'table_name, expected_payload,',
    [
        (
            'some_table',
            {
                'bp_type': 'db_cleaner',
                'bp_name': 'some_table' + '_cleaner',
                'bp_settings': {
                    'max_age': 86400,
                    'pause_between_removes': 0,
                    'db_name': 'main-db',
                    'primary_key': 'history_event_id',
                    'timestamp_column': 'history_timestamp',
                    'timestamp_is_integer': True,
                    'table_name': 'some_table',
                },
            },
        ),
        (
            'node_reservations_history',
            _get_robot_from_response(
                lambda robot: robot['bp_type'] == 'db_cleaner'
                and robot['bp_settings']['table_name']
                == 'node_reservations_history',
            ),
        ),
    ],
)
async def test_admin_developers_commands_do__create_cleaner(
        taxi_logistic_platform_processing,
        mockserver,
        load_json,
        table_name,
        expected_payload,
        mock_bg_info,
        payload_storage,
        mock_bg_upsert,
):
    expected_payload['bp_enabled'] = False
    expected_payload['bp_settings']['period'] = '10m'
    payload_storage.set_payload(expected_payload)

    response = await taxi_logistic_platform_processing.post(
        '/admin/logistic-platform-processing/commands/do/modify/developer',
        params={'environment': 'testing'},
        json=_build_modify_command('create_cleaner', table_name=table_name),
    )
    assert response.status == 200
    assert response.json()['command_response'] == 'OK'
