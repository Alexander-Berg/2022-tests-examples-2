from google.protobuf import any_pb2 as ap2
from kikimr.public.api.protos import ydb_operation_pb2 as yop2
from kikimr.public.api.protos import ydb_status_codes_pb2 as ysc2
import pytest

from logbroker.public.api.protos import common_pb2 as cp2

from clownductor.internal.tasks import cubes

ERROR_RESPONSE = """id: "iddqd"
ready: true
status: BAD_REQUEST
result {
  value: "failed result"
}
"""


def task_data(name):
    return {
        'id': 123,
        'job_id': 456,
        'name': name,
        'sleep_until': 0,
        'input_mapping': {},
        'output_mapping': {},
        'payload': {},
        'retries': 0,
        'status': 'in_progress',
        'error_message': None,
        'created_at': 0,
        'updated_at': 0,
    }


@pytest.mark.parametrize(
    [
        'error',
        'expected_execute_modify_commands_times_called',
        'expected_get_operation_times_called',
    ],
    [(False, 1, 1), (True, 1, 0)],
)
@pytest.mark.parametrize(
    'grant_testing, expected_lb_request',
    [
        pytest.param(
            False,
            'expected_lb_request',
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={
                    'logbroker_grant_permissions': True,
                    'logbroker_grant_permissions_testing': False,
                },
            ),
        ),
        pytest.param(
            True,
            'expected_lb_request_testing',
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={
                    'logbroker_grant_permissions': True,
                    'logbroker_grant_permissions_testing': True,
                },
            ),
        ),
    ],
)
async def test_logbroker_grant_permissions(
        web_context,
        load,
        error,
        grant_testing,
        start_logbroker_server,
        logbroker_server_handler,
        expected_lb_request,
        expected_execute_modify_commands_times_called,
        expected_get_operation_times_called,
):
    @logbroker_server_handler('ExecuteModifyCommands')
    def _execute_modify_commands_mock(request, context):
        assert repr(request) == load(expected_lb_request)

        operation = yop2.Operation(id='iddqd')
        if error:
            operation = yop2.Operation(
                id='iddqd',
                ready=True,
                status=ysc2.StatusIds.BAD_REQUEST,  # pylint: disable=E1101
                result=ap2.Any(value=b'failed result'),
            )

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

    cube = cubes.CUBES['LogbrokerTvmGrantPermissionsCube'](
        web_context,
        task_data('LogbrokerTvmGrantPermissionsCube'),
        {'stable_tvm_id': 31122019, 'testing_tvm_id': 31122020},
        [],
        None,
    )
    await cube.update()

    assert cube.success is not error

    assert (
        _execute_modify_commands_mock.times_called
        == expected_execute_modify_commands_times_called
    )
    assert (
        _get_operation_mock.times_called == expected_get_operation_times_called
    )

    if error:
        assert cube.data['error_message'] == ERROR_RESPONSE
    else:
        assert cube.data['payload'] == {'operation_id': 'iddqd'}
