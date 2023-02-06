# pylint: disable=too-many-lines
import json

from kikimr.public.api.protos import ydb_operation_pb2 as yop2
from kikimr.public.api.protos import ydb_status_codes_pb2 as ysc2
import pytest

from logbroker.public.api.protos import common_pb2 as cp2
from logbroker.public.api.protos import config_manager_pb2 as cmp2


@pytest.fixture(name='mock_safe_render')
def mock_safe_render_fixture(load_json, mock_strongbox):
    def _impl(response_fname):
        @mock_strongbox('/v1/secrets/safe_render/')
        def _mock_strongbox(request):
            return {
                'data': json.dumps(
                    load_json(response_fname)[request.query['service_name']][
                        request.query['env']
                    ],
                ),
            }

        return _mock_strongbox

    return _impl


@pytest.fixture(name='mock_clown')
def mock_clown_fixture(load_json, mock_clownductor, mock_safe_render):
    @mock_clownductor('/v1/branches', prefix=True)
    def _mock_branches(request):
        assert request.query['branch_id'] == '777'

        return load_json('branches_response_simple.json')

    @mock_clownductor('/v1/services', prefix=True)
    def _mock_services(request):
        assert request.query['service_id'] == '666'

        return load_json('services_response_simple.json')

    @mock_clownductor('/v1/projects', prefix=True)
    def _mock_projects(request):
        assert request.query['name'] == 'some_project'

        return load_json('projects_response_simple.json')

    mock_safe_render('strongbox_response_simple.json')


@pytest.mark.parametrize(
    [
        'expected_emc_request',
        'expected_emc_times_called',
        'emc_response',
        'expected_dp_times_called',
        'topic_already_exists',
        'branches_response',
        'expected_branches_times_called',
        'services_response',
        'expected_services_times_called',
        'projects_response',
        'expected_projects_times_called',
        'strongbox_response',
        'expected_strongbox_times_called',
        'expected_response_code',
        'expected_response',
    ],
    [
        pytest.param(
            'expected_execute_commands_request_simple.txt',
            1,
            yop2.Operation(id='iddqd'),
            1,
            False,
            'branches_response_simple.json',
            1,
            'services_response_simple.json',
            1,
            'projects_response_simple.json',
            1,
            'strongbox_response_simple.json',
            1,
            200,
            {
                'operations': [
                    {'id': 'iddqd', 'logbroker_installation': '__default__'},
                ],
            },
            id='happy path',
        ),
        pytest.param(
            'expected_execute_commands_request_stable.txt',
            1,
            yop2.Operation(id='iddqd'),
            1,
            False,
            'branches_response_stable.json',
            1,
            'services_response_simple.json',
            1,
            'projects_response_simple.json',
            1,
            'strongbox_response_simple.json',
            1,
            200,
            {
                'operations': [
                    {'id': 'iddqd', 'logbroker_installation': '__default__'},
                ],
            },
            marks=pytest.mark.config(
                LOGS_FROM_YT_FEATURES={'configure_logbroker_production': True},
            ),
            id='happy path at stable',
        ),
        pytest.param(
            None,
            0,
            None,
            0,
            False,
            'branches_response_stable.json',
            1,
            None,
            0,
            None,
            0,
            None,
            0,
            200,
            {'operations': []},
            id=(
                'happy path at stable, but '
                'configure_logbroker_production feature disabled'
            ),
        ),
        pytest.param(
            None,
            0,
            None,
            0,
            False,
            'branches_response_simple.json',
            1,
            'services_response_simple.json',
            1,
            'projects_response_simple.json',
            1,
            'strongbox_response_malformed.json',
            1,
            400,
            {
                'message': (
                    'some_service testing secdist parse error: '
                    'secret is required property'
                ),
                'code': 'SECDIST_ERROR',
            },
            id='wrong secdist schema',
        ),
        pytest.param(
            None,
            0,
            None,
            0,
            False,
            'branches_response_simple.json',
            1,
            'services_response_simple.json',
            1,
            'projects_response_simple.json',
            1,
            'strongbox_response_no_tvm_ids.json',
            1,
            400,
            {
                'message': (
                    'some_service testing secdist '
                    'settings_override.TVM_SERVICES is empty, push-client '
                    'won\'t be able to send logs'
                ),
                'code': 'SECDIST_ERROR',
            },
            id='no tvm ids in secdist',
        ),
        pytest.param(
            'expected_execute_commands_request_multiple_tvm_ids.txt',
            1,
            yop2.Operation(id='iddqd'),
            1,
            False,
            'branches_response_simple.json',
            1,
            'services_response_simple.json',
            1,
            'projects_response_simple.json',
            1,
            'strongbox_response_multiple_tvm_ids.json',
            1,
            200,
            {
                'operations': [
                    {'id': 'iddqd', 'logbroker_installation': '__default__'},
                ],
            },
            id=(
                'unable to define single tvm, granting WriteTopic '
                'to all tvms from secdist'
            ),
        ),
        pytest.param(
            None,
            0,
            None,
            0,
            False,
            'branches_response_simple.json',
            1,
            'services_response_empty.json',
            1,
            None,
            0,
            None,
            0,
            400,
            {
                'message': 'Failed to retrieve service from clownductor',
                'code': 'CLOWNDUCTOR_ERROR',
            },
            id='clownductor service not found',
        ),
        pytest.param(
            None,
            0,
            None,
            0,
            False,
            'branches_response_simple.json',
            1,
            'services_response_no_project_name.json',
            1,
            None,
            0,
            None,
            0,
            400,
            {
                'message': 'Failed to retrieve project_name from clownductor',
                'code': 'CLOWNDUCTOR_ERROR',
            },
            id='clownductor returned no project_name',
        ),
        pytest.param(
            None,
            0,
            None,
            1,
            False,
            'branches_response_simple.json',
            1,
            'services_response_no_abc_service.json',
            1,
            'projects_response_simple.json',
            1,
            'strongbox_response_simple.json',
            1,
            400,
            {
                'message': (
                    'Can\'t determine `Responsible` for '
                    'topic: taxi/taxi-test-access-log'
                ),
                'code': 'BAD_SERVICE_STATE',
            },
            id='clownductor returned no abc_service',
        ),
        pytest.param(
            'expected_commands_request_simple_wo_create_topic.txt',
            1,
            yop2.Operation(id='iddqd'),
            1,
            True,
            'branches_response_simple.json',
            1,
            'services_response_no_abc_service.json',
            1,
            'projects_response_simple.json',
            1,
            'strongbox_response_simple.json',
            1,
            200,
            {
                'operations': [
                    {'id': 'iddqd', 'logbroker_installation': '__default__'},
                ],
            },
            id='clownductor returned no abc_service, but topic already exists',
        ),
        pytest.param(
            None,
            0,
            None,
            0,
            False,
            'branches_response_simple.json',
            1,
            'services_response_simple.json',
            1,
            'projects_response_empty.json',
            1,
            None,
            0,
            400,
            {
                'message': 'Failed to retrieve project from clownductor',
                'code': 'CLOWNDUCTOR_ERROR',
            },
            id='clownductor project not found',
        ),
        pytest.param(
            None,
            0,
            None,
            1,
            False,
            'branches_response_simple.json',
            1,
            'services_response_simple.json',
            1,
            'projects_response_no_abc_service.json',
            1,
            'strongbox_response_simple.json',
            1,
            400,
            {
                'message': (
                    'Can\'t determine `ABC service` for '
                    'topic: taxi/taxi-test-access-log'
                ),
                'code': 'BAD_SERVICE_STATE',
            },
            id='clownductor returned no abc_service',
        ),
        pytest.param(
            'expected_commands_request_simple_wo_create_topic.txt',
            1,
            yop2.Operation(id='iddqd'),
            1,
            True,
            'branches_response_simple.json',
            1,
            'services_response_simple.json',
            1,
            'projects_response_no_abc_service.json',
            1,
            'strongbox_response_simple.json',
            1,
            200,
            {
                'operations': [
                    {'id': 'iddqd', 'logbroker_installation': '__default__'},
                ],
            },
            id='clownductor returned no abc_service, but topic already exists',
        ),
        pytest.param(
            'expected_execute_commands_request_simple.txt',
            1,
            yop2.Operation(id='', ready=True),
            1,
            False,
            'branches_response_simple.json',
            1,
            'services_response_simple.json',
            1,
            'projects_response_simple.json',
            1,
            'strongbox_response_simple.json',
            1,
            500,
            {
                'message': 'ExecuteModifyCommands failed',
                'code': 'LOGBROKER_ERROR',
            },
            id='lb created no active operation',
        ),
        pytest.param(
            None,
            0,
            None,
            0,
            False,
            'branches_response_unstable.json',
            1,
            None,
            0,
            None,
            0,
            None,
            0,
            200,
            {'operations': []},
            id='No topics for env, no unnecessary queries',
        ),
    ],
)
@pytest.mark.config(
    TVM_SERVICES={
        'logbroker': 762,
        'custom_logbroker': 639,
        'logs-from-yt': 581,
    },
    TVM_RULES=[
        {'src': 'logs-from-yt', 'dst': 'logbroker'},
        {'src': 'logs-from-yt', 'dst': 'custom_logbroker'},
    ],
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm')
async def test_configure_simple(
        web_app_client,
        mock_clownductor,
        mock_safe_render,
        load,
        load_json,
        start_logbroker_server,
        logbroker_server_handler,
        expected_emc_request,
        expected_emc_times_called,
        emc_response,
        expected_dp_times_called,
        topic_already_exists,
        branches_response,
        expected_branches_times_called,
        services_response,
        expected_services_times_called,
        projects_response,
        expected_projects_times_called,
        strongbox_response,
        expected_strongbox_times_called,
        expected_response_code,
        expected_response,
):
    @logbroker_server_handler('ExecuteModifyCommands')
    def _mock_emc(request, context):
        assert repr(request) == load(expected_emc_request)

        return cp2.ExecuteModifyCommandsResponse(operation=emc_response)

    @logbroker_server_handler('DescribePath')
    def _mock_describe_path(request, context):
        if topic_already_exists:
            response = cmp2.DescribePathResponse(
                operation=yop2.Operation(
                    # pylint: disable=E1101
                    id='some_id',
                    ready=True,
                    status=ysc2.StatusIds.SUCCESS,
                ),
            )
            # pylint: disable=E1101
            response.operation.result.Pack(cmp2.DescribePathResult())

            return response

        return cmp2.DescribePathResponse(
            operation=yop2.Operation(
                # pylint: disable=E1101
                id='some_id',
                ready=True,
                status=ysc2.StatusIds.NOT_FOUND,
            ),
        )

    await start_logbroker_server()

    @mock_clownductor('/v1/branches', prefix=True)
    def _mock_branches(request):
        assert request.query['branch_id'] == '777'

        return load_json(branches_response)

    @mock_clownductor('/v1/services', prefix=True)
    def _mock_services(request):
        assert request.query['service_id'] == '666'

        return load_json(services_response)

    @mock_clownductor('/v1/projects', prefix=True)
    def _mock_projects(request):
        assert request.query['name'] == 'some_project'

        return load_json(projects_response)

    _mock_safe_render = mock_safe_render(strongbox_response)

    response = await web_app_client.post(
        '/v1/logbroker/configure',
        json={
            'main_alias': {
                'clownductor_branch': {'service_id': 666, 'branch_id': 777},
                'logbroker_configuration': {
                    'topic_writers': [
                        {
                            'service_environment': 'testing',
                            'topic_path': 'taxi/taxi-test-access-log',
                            'logbroker_installation': '__default__',
                        },
                        {
                            'service_environment': 'production',
                            'topic_path': 'taxi/taxi-access-log',
                            'logbroker_installation': '__default__',
                        },
                    ],
                },
            },
        },
    )

    assert response.status == expected_response_code
    assert await response.json() == expected_response

    assert _mock_emc.times_called == expected_emc_times_called
    assert _mock_safe_render.times_called == expected_strongbox_times_called
    assert _mock_branches.times_called == expected_branches_times_called
    assert _mock_services.times_called == expected_services_times_called
    assert _mock_projects.times_called == expected_projects_times_called
    assert _mock_describe_path.times_called == expected_dp_times_called


@pytest.mark.config(
    TVM_SERVICES={
        'logbroker': 762,
        'custom_logbroker': 639,
        'logs-from-yt': 581,
    },
    TVM_RULES=[
        {'src': 'logs-from-yt', 'dst': 'logbroker'},
        {'src': 'logs-from-yt', 'dst': 'custom_logbroker'},
    ],
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm', 'mock_clown')
async def test_configure_multiple_installations(
        web_app_client,
        mock_clownductor,
        load,
        load_json,
        start_logbroker_server,
        logbroker_server_handler,
):
    @logbroker_server_handler(
        'ExecuteModifyCommands', installation='__default__',
    )
    def _mock_emc_default(request, context):
        assert repr(request) == load(
            'expected_execute_commands_request_simple.txt',
        )

        return cp2.ExecuteModifyCommandsResponse(
            operation=yop2.Operation(id='default_installation_id'),
        )

    @logbroker_server_handler(
        'ExecuteModifyCommands', installation='custom_installation',
    )
    def _mock_emc_custom(request, context):
        assert repr(request) == load(
            'expected_execute_commands_request_custom_installation.txt',
        )

        return cp2.ExecuteModifyCommandsResponse(
            operation=yop2.Operation(id='custom_installation_id'),
        )

    @logbroker_server_handler('DescribePath', installation='__default__')
    def _mock_describe_path_default(request, context):
        return cmp2.DescribePathResponse(
            operation=yop2.Operation(
                # pylint: disable=E1101
                id='some_id',
                ready=True,
                status=ysc2.StatusIds.NOT_FOUND,
            ),
        )

    @logbroker_server_handler(
        'DescribePath', installation='custom_installation',
    )
    def _mock_describe_path_custom(request, context):
        return cmp2.DescribePathResponse(
            operation=yop2.Operation(
                # pylint: disable=E1101
                id='some_id',
                ready=True,
                status=ysc2.StatusIds.NOT_FOUND,
            ),
        )

    await start_logbroker_server()

    response = await web_app_client.post(
        '/v1/logbroker/configure',
        json={
            'main_alias': {
                'clownductor_branch': {'service_id': 666, 'branch_id': 777},
                'logbroker_configuration': {
                    'topic_writers': [
                        {
                            'service_environment': 'testing',
                            'topic_path': 'taxi/taxi-test-access-log',
                            'logbroker_installation': '__default__',
                        },
                        {
                            'service_environment': 'production',
                            'topic_path': 'taxi/taxi-access-log',
                            'logbroker_installation': '__default__',
                        },
                        {
                            'service_environment': 'testing',
                            'topic_path': 'taxi/taxi-logs-from-yt',
                            'logbroker_installation': 'custom_installation',
                        },
                    ],
                },
            },
        },
    )

    assert response.status == 200
    assert await response.json() == {
        'operations': [
            {
                'id': 'default_installation_id',
                'logbroker_installation': '__default__',
            },
            {
                'id': 'custom_installation_id',
                'logbroker_installation': 'custom_installation',
            },
        ],
    }

    assert _mock_emc_default.times_called == 1
    assert _mock_emc_custom.times_called == 1
    assert _mock_describe_path_default.times_called == 1
    assert _mock_describe_path_custom.times_called == 1


@pytest.mark.config(
    TVM_SERVICES={
        'logbroker': 762,
        'custom_logbroker': 639,
        'logs-from-yt': 581,
    },
    TVM_RULES=[
        {'src': 'logs-from-yt', 'dst': 'logbroker'},
        {'src': 'logs-from-yt', 'dst': 'custom_logbroker'},
    ],
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm', 'mock_clown')
async def test_configure_topic_already_exists(
        web_app_client,
        mock_clownductor,
        load,
        load_json,
        start_logbroker_server,
        logbroker_server_handler,
):
    @logbroker_server_handler('ExecuteModifyCommands')
    def _mock_emc(request, context):
        assert repr(request) == load(
            'expected_execute_commands_request_topic_already_exists.txt',
        )

        return cp2.ExecuteModifyCommandsResponse(
            operation=yop2.Operation(id='id'),
        )

    @logbroker_server_handler('DescribePath', installation='__default__')
    def _mock_describe_path(request, context):
        if request.path.path == 'taxi/taxi-test-access-log':
            response = cmp2.DescribePathResponse(
                operation=yop2.Operation(
                    # pylint: disable=E1101
                    id='some_id',
                    ready=True,
                    status=ysc2.StatusIds.SUCCESS,
                ),
            )
            # pylint: disable=E1101
            response.operation.result.Pack(cmp2.DescribePathResult())

            return response

        return cp2.ExecuteModifyCommandsResponse(
            operation=yop2.Operation(
                # pylint: disable=E1101
                id='some_id',
                ready=True,
                status=ysc2.StatusIds.NOT_FOUND,
            ),
        )

    await start_logbroker_server()

    response = await web_app_client.post(
        '/v1/logbroker/configure',
        json={
            'main_alias': {
                'clownductor_branch': {'service_id': 666, 'branch_id': 777},
                'logbroker_configuration': {
                    'topic_writers': [
                        {
                            'service_environment': 'testing',
                            'topic_path': 'taxi/taxi-test-access-log',
                            'logbroker_installation': '__default__',
                        },
                        {
                            'service_environment': 'testing',
                            'topic_path': 'taxi/taxi-access-log',
                            'logbroker_installation': '__default__',
                        },
                        {
                            'service_environment': 'production',
                            'topic_path': 'taxi/taxi-access-log',
                            'logbroker_installation': '__default__',
                        },
                    ],
                },
            },
        },
    )

    assert response.status == 200
    assert await response.json() == {
        'operations': [{'id': 'id', 'logbroker_installation': '__default__'}],
    }

    assert _mock_emc.times_called == 1
    assert _mock_describe_path.times_called == 2


@pytest.mark.config(
    TVM_SERVICES={
        'logbroker': 762,
        'custom_logbroker': 639,
        'logs-from-yt': 581,
    },
    TVM_RULES=[
        {'src': 'logs-from-yt', 'dst': 'logbroker'},
        {'src': 'logs-from-yt', 'dst': 'custom_logbroker'},
    ],
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.parametrize(
    [
        'main_alias',
        'services_response',
        'topic_already_exists',
        'expected_response_code',
        'expected_response',
    ],
    [
        pytest.param(
            None,
            'services_response_settings_conflict.json',
            False,
            400,
            {
                'message': 'Topic settings conflict',
                'code': 'CONFIGURATION_ERROR',
            },
            id='multiple secondary aliases with different topic_settings',
        ),
        pytest.param(
            None,
            'services_response_settings_conflict.json',
            True,
            200,
            {
                'operations': [
                    {'id': 'id', 'logbroker_installation': '__default__'},
                ],
            },
            id=(
                'multiple secondary aliases with different topic_settings, '
                'but topic already exists, so no topic_settings needed'
            ),
        ),
        pytest.param(
            None,
            'services_response_no_settings_conflict.json',
            False,
            200,
            {
                'operations': [
                    {'id': 'id', 'logbroker_installation': '__default__'},
                ],
            },
            id='test sanity check',
        ),
        pytest.param(
            {
                'clownductor_branch': {'service_id': 666, 'branch_id': 228},
                'logbroker_configuration': {
                    'topic_writers': [
                        {
                            'service_environment': 'testing',
                            'topic_path': 'taxi/taxi-test-access-log',
                            'logbroker_installation': '__default__',
                        },
                    ],
                },
            },
            'services_response_settings_conflict.json',
            False,
            200,
            {
                'operations': [
                    {'id': 'id', 'logbroker_installation': '__default__'},
                ],
            },
            id=(
                'multiple secondary aliases with different topic_settings, '
                'but main_alias is present, so its\' settings are used'
            ),
        ),
    ],
)
async def test_configure_topic_settings_conflict(
        web_app_client,
        mock_clownductor,
        mock_safe_render,
        load,
        load_json,
        start_logbroker_server,
        logbroker_server_handler,
        main_alias,
        services_response,
        topic_already_exists,
        expected_response_code,
        expected_response,
):
    @logbroker_server_handler('ExecuteModifyCommands')
    def _mock_emc(request, context):
        return cp2.ExecuteModifyCommandsResponse(
            operation=yop2.Operation(id='id'),
        )

    @logbroker_server_handler('DescribePath', installation='__default__')
    def _mock_describe_path(request, context):
        if topic_already_exists:
            response = cmp2.DescribePathResponse(
                operation=yop2.Operation(
                    # pylint: disable=E1101
                    id='some_id',
                    ready=True,
                    status=ysc2.StatusIds.SUCCESS,
                ),
            )
            # pylint: disable=E1101
            response.operation.result.Pack(cmp2.DescribePathResult())

            return response

        return cp2.ExecuteModifyCommandsResponse(
            operation=yop2.Operation(
                # pylint: disable=E1101
                id='some_id',
                ready=True,
                status=ysc2.StatusIds.NOT_FOUND,
            ),
        )

    @mock_clownductor('/v1/branches', prefix=True)
    def _mock_branches(request):
        return load_json('branches_response_settings_conflict.json')[
            request.query['branch_id']
        ]

    @mock_clownductor('/v1/services', prefix=True)
    def _mock_services(request):
        return load_json(services_response)[request.query['service_id']]

    @mock_clownductor('/v1/projects', prefix=True)
    def _mock_projects(request):
        assert request.query['name'] == 'some_project'

        return load_json('projects_response_simple.json')

    mock_safe_render('strongbox_response_settings_conflict.json')

    await start_logbroker_server()

    request_json = {
        'aliases': [
            {
                'clownductor_branch': {'service_id': 666, 'branch_id': 777},
                'logbroker_configuration': {
                    'topic_writers': [
                        {
                            'service_environment': 'testing',
                            'topic_path': 'taxi/taxi-test-access-log',
                            'logbroker_installation': '__default__',
                        },
                    ],
                },
            },
            {
                'clownductor_branch': {'service_id': 1666, 'branch_id': 1777},
                'logbroker_configuration': {
                    'topic_writers': [
                        {
                            'service_environment': 'testing',
                            'topic_path': 'taxi/taxi-test-access-log',
                            'logbroker_installation': '__default__',
                        },
                    ],
                },
            },
        ],
    }
    if main_alias is not None:
        request_json['main_alias'] = main_alias

    response = await web_app_client.post(
        '/v1/logbroker/configure', json=request_json,
    )

    assert response.status == expected_response_code
    assert await response.json() == expected_response

    assert _mock_describe_path.times_called == 1


@pytest.mark.parametrize(
    ['lb_response', 'expected_response'],
    [
        (
            yop2.Operation(id='777', ready=False),
            {
                'operations': [
                    {
                        'id': '777',
                        'logbroker_installation': '__default__',
                        'ready': False,
                    },
                ],
            },
        ),
        (
            yop2.Operation(
                # pylint: disable=E1101
                id='777',
                ready=True,
                status=ysc2.StatusIds.SUCCESS,
            ),
            {
                'operations': [
                    {
                        'id': '777',
                        'logbroker_installation': '__default__',
                        'ready': True,
                        'success': True,
                    },
                ],
            },
        ),
        (
            yop2.Operation(
                # pylint: disable=E1101
                id='777',
                ready=True,
                status=ysc2.StatusIds.ABORTED,
            ),
            {
                'operations': [
                    {
                        'id': '777',
                        'logbroker_installation': '__default__',
                        'ready': True,
                        'success': False,
                        'message': 'id: "777"\nready: true\nstatus: ABORTED\n',
                    },
                ],
            },
        ),
    ],
)
async def test_configure_status_simple(
        taxi_logs_from_yt_web,
        mock_clownductor,
        load,
        load_json,
        start_logbroker_server,
        logbroker_server_handler,
        lb_response,
        expected_response,
):
    @logbroker_server_handler('GetOperation')
    def _mock_get_operation(request, context):
        assert repr(request) == 'id: "777"\n'

        return yop2.GetOperationResponse(operation=lb_response)

    await start_logbroker_server()

    response = await taxi_logs_from_yt_web.post(
        '/v1/logbroker/configure/status',
        json={
            'operations': [
                {'id': '777', 'logbroker_installation': '__default__'},
            ],
        },
    )

    assert response.status == 200
    assert await response.json() == expected_response

    assert _mock_get_operation.times_called == 1


async def test_configure_status_multiple_installations(
        taxi_logs_from_yt_web,
        mock_clownductor,
        load,
        load_json,
        start_logbroker_server,
        logbroker_server_handler,
):
    @logbroker_server_handler('GetOperation', installation='__default__')
    def _mock_lb_default(request, context):
        assert repr(request) == 'id: "777"\n'

        return yop2.GetOperationResponse(
            operation=yop2.Operation(id='777', ready=False),
        )

    @logbroker_server_handler(
        'GetOperation', installation='custom_installation',
    )
    def _mock_lb_custom(request, context):
        assert repr(request) == 'id: "776"\n'

        return yop2.GetOperationResponse(
            operation=yop2.Operation(id='776', ready=False),
        )

    await start_logbroker_server()

    response = await taxi_logs_from_yt_web.post(
        '/v1/logbroker/configure/status',
        json={
            'operations': [
                {'id': '777', 'logbroker_installation': '__default__'},
                {'id': '776', 'logbroker_installation': 'custom_installation'},
            ],
        },
    )

    assert response.status == 200
    assert await response.json() == {
        'operations': [
            {
                'id': '777',
                'logbroker_installation': '__default__',
                'ready': False,
            },
            {
                'id': '776',
                'logbroker_installation': 'custom_installation',
                'ready': False,
            },
        ],
    }

    assert _mock_lb_default.times_called == 1
    assert _mock_lb_custom.times_called == 1
