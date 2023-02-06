import grpc
import pytest

from arc_api import types as arc_types
from yandex.arc.api.public import repo_pb2


GENERAL_DATA_REQUEST = {
    'job_id': 1,
    'retries': 0,
    'status': 'in_progress',
    'task_id': 1,
}


async def test_create_branch(patch_arc_set_reference, call_cube_handle):
    expected_commit_oid = '5930328f6a0d43ab51aab3eff415d6e0753bf92f'
    user = 'robot-taxi-clown'
    branch = 'test-branch'
    set_ref_mock = patch_arc_set_reference(
        responses=[arc_types.ResponseMock(message=repo_pb2.SetRefResponse())],
    )

    input_data = {
        'user': user,
        'branch_name': branch,
        'commit_oid': expected_commit_oid,
        'approve_required': False,
        'robot_for_ship': None,
    }

    await call_cube_handle(
        'ArcadiaCreateBranch',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': {
                'payload': {'commit_oid': expected_commit_oid},
                'status': 'success',
            },
        },
    )

    set_ref_mock_request = set_ref_mock.calls.pop().pop('request')
    assert set_ref_mock_request == repo_pb2.SetRefRequest(
        Branch=f'users/{user}/{branch}', CommitOid=expected_commit_oid,
    )
    assert not set_ref_mock.calls


@pytest.mark.parametrize(
    'server_error',
    [
        pytest.param(None, id='success'),
        pytest.param(
            arc_types.ServerErrorMock(
                grpc.StatusCode.UNKNOWN,
                'arc/server/public.cpp:1669: TStatus_ECode_NoSuchBranch'
                ' no such branch',
            ),
            id='already_deleted',
        ),
    ],
)
async def test_delete_branch(
        patch_arc_delete_reference, call_cube_handle, server_error,
):
    expected_commit_oid = '5930328f6a0d43ab51aab3eff415d6e0753bf92f'
    expected_branch_name = 'test-branch'
    expected_user = 'robot-taxi-clown-tst'
    input_data = {
        'user': expected_user,
        'branch_name': expected_branch_name,
        'commit_oid': expected_commit_oid,
        'approve_required': False,
        'robot_for_ship': None,
    }

    delete_ref_mock = patch_arc_delete_reference(
        responses=[
            arc_types.ResponseMock(
                message=repo_pb2.DeleteRefResponse(),
                server_error=server_error,
            ),
        ],
    )

    await call_cube_handle(
        'ArcadiaDeleteBranch',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': {'status': 'success'},
        },
    )

    delete_ref_mock_request = delete_ref_mock.calls.pop().pop('request')
    assert delete_ref_mock_request == repo_pb2.DeleteRefRequest(
        Branch=f'users/{expected_user}/{expected_branch_name}',
        ExpectedCommitOid=expected_commit_oid,
    )
    assert not delete_ref_mock.calls
