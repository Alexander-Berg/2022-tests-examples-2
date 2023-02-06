from google.protobuf import any_pb2 as ap2
from kikimr.public.api.protos import ydb_operation_pb2 as yop2
from kikimr.public.api.protos import ydb_status_codes_pb2 as ysc2
import pytest

from logbroker.public.api.protos import common_pb2 as cp2


@pytest.mark.parametrize('cube_name', ['LogbrokerTvmGrantPermissionsCube'])
@pytest.mark.config(CLOWNDUCTOR_FEATURES={'logbroker_grant_permissions': True})
async def test_post_logbroker_cube(
        web_app_client,
        web_context,
        cube_name,
        load_json,
        load,
        start_logbroker_server,
        logbroker_server_handler,
):
    @logbroker_server_handler('ExecuteModifyCommands')
    def _execute_modify_commands_mock(request, context):
        assert repr(request) == load('expected_lb_request')

        operation = yop2.Operation(id='iddqd')

        return cp2.ExecuteModifyCommandsResponse(operation=operation)

    @logbroker_server_handler('GetOperation')
    def _get_operation_mock(request, context):
        assert repr(request) == 'id: "iddqd"\n'

        operation = yop2.Operation(
            id='iddqd',
            ready=True,
            status=ysc2.StatusIds.SUCCESS,  # pylint: disable=E1101
            result=ap2.Any(value=b'success result'),
        )

        return yop2.GetOperationResponse(operation=operation)

    await start_logbroker_server()

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']

    assert _execute_modify_commands_mock.times_called == 1
    assert _get_operation_mock.times_called == 1
