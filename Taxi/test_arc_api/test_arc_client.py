import copy

import grpc
import pytest

from yandex.arc.api.public import repo_pb2

from arc_api import components as arc_api
from arc_api import types


FILE_CONTENT_CHUNKS = (b'Test ', b'text')
FILE_CONTENT_MOCK = b''.join(FILE_CONTENT_CHUNKS)


@pytest.mark.parametrize(
    'expected_error, server_error',
    [
        pytest.param(None, None, id='success'),
        pytest.param(
            arc_api.NotFoundError,
            types.ServerErrorMock(
                grpc.StatusCode.INVALID_ARGUMENT,
                'arc/server/public.cpp:330: Can\'t parse revision: '
                '{ Code: NoSuchBranch Message: "NoSuchBranch" } NoSuchBranch',
            ),
            id='invalid_branch',
        ),
        pytest.param(
            arc_api.NotFoundError,
            types.ServerErrorMock(
                grpc.StatusCode.NOT_FOUND, 'file not found in revision',
            ),
            id='no_such_file',
        ),
        pytest.param(
            arc_api.NotFoundError,
            types.ServerErrorMock(
                grpc.StatusCode.NOT_FOUND,
                'arc/server/public.cpp:362: id not found '
                '853cb0f6a5888d6ecfe2c7acc6a90d42af85b89c',
            ),
            id='invalid_commit_oid',
        ),
    ],
)
async def test_read_file(
        mock,
        arc_mockserver,
        patch_file_service,
        library_context,
        expected_error,
        server_error,
):
    expected_path = 'README.md'
    expected_revision = '853cb0f6a5888d6ecfe2c7acc6a90d42af85b89c'

    @mock
    def _read_file(request: repo_pb2.ReadFileRequest, context):
        assert request.Revision == expected_revision
        assert request.Path == expected_path

        if server_error:
            context.set_code(server_error.status)
            context.set_details(server_error.details)
            return

        yield repo_pb2.ReadFileResponse(
            Header=repo_pb2.ReadFileResponse.ReadFileHeader(
                Oid='853cb0f6a5888d6ecfe2c7acc6a90d42af85b89c',
                FileSize=len(FILE_CONTENT_MOCK),
            ),
        )
        for chunk in FILE_CONTENT_CHUNKS:
            yield repo_pb2.ReadFileResponse(Data=chunk)

    file_service_mock = patch_file_service(read_file=_read_file)
    arc_mockserver(file_service_mock)

    call = library_context.arc_api.read_file(
        path=expected_path, revision=expected_revision,
    )
    if not expected_error:
        response = await call
        assert (
            response.header.oid == '853cb0f6a5888d6ecfe2c7acc6a90d42af85b89c'
        )
        assert response.header.file_size == len(FILE_CONTENT_MOCK)
        assert response.content == FILE_CONTENT_MOCK
    else:
        with pytest.raises(expected_error):
            await call

    assert len(_read_file.calls) == 1


@pytest.mark.parametrize(
    'expected_revision, expected_error, server_error',
    [
        pytest.param(
            'users/robot-taxi-clown-tst/test-arc-api',
            None,
            None,
            id='valid_revision',
        ),
        pytest.param(
            'users/robot-taxi-clown-tst/test-arc-api',
            arc_api.NotFoundError,
            types.ServerErrorMock(
                grpc.StatusCode.INVALID_ARGUMENT,
                'arc/server/public.cpp:330: Can\'t parse revision: '
                '{ Code: NoSuchBranch Message: "NoSuchBranch" } NoSuchBranch',
            ),
            id='invalid_revision',
        ),
        pytest.param(
            '853cb0f6a5888d6ecfe2c7acc6a90d42af85b89c',
            arc_api.NotFoundError,
            types.ServerErrorMock(
                grpc.StatusCode.NOT_FOUND,
                'arc/server/public.cpp:362: id not found '
                '853cb0f6a5888d6ecfe2c7acc6a90d42af85b89c',
            ),
            id='invalid_commit_oid',
        ),
    ],
)
async def test_get_commit(
        patch_arc_get_commit,
        arc_commit_mock,
        library_context,
        _try_call,
        expected_revision,
        expected_error,
        server_error,
):
    expected_commit = arc_commit_mock
    get_commit_mock = patch_arc_get_commit(
        revision=expected_revision,
        commit=expected_commit,
        server_error=server_error,
    )

    call = library_context.arc_api.get_commit(revision=expected_revision)
    commit = await _try_call(call, expected_error)
    if commit:
        assert commit == expected_commit

    get_commit_mock_request = get_commit_mock.calls.pop().pop('request')
    assert get_commit_mock_request == repo_pb2.GetCommitRequest(
        Revision=expected_revision,
    )
    assert not get_commit_mock.calls


@pytest.mark.parametrize(
    'expected_error, server_error',
    [
        pytest.param(None, None, id='success'),
        pytest.param(
            arc_api.NotFoundError,
            types.ServerErrorMock(
                grpc.StatusCode.NOT_FOUND,
                'arc/server/public.cpp:1101: Branch not found.',
            ),
            id='branch_not_found',
        ),
        pytest.param(
            arc_api.AlreadyExistsError,
            types.ServerErrorMock(
                grpc.StatusCode.ALREADY_EXISTS,
                'arc/server/public.cpp:1131: Commit does not change anything',
            ),
            id='nothing_to_commit',
        ),
    ],
)
async def test_create_commit(
        patch_arc_create_commit,
        arc_commit_mock,
        library_context,
        _try_call,
        expected_error,
        server_error,
):
    expected_commit = copy.deepcopy(arc_commit_mock)
    expected_user = 'robot-taxi-clown-tst'
    expected_branch = 'test-arc-api'
    expected_path = 'path/to/file.yaml'
    expected_data = FILE_CONTENT_MOCK
    expected_message = expected_commit.Message

    if server_error:
        create_commit_mock = patch_arc_create_commit(
            responses=[
                types.ResponseMock(
                    message=repo_pb2.CommitFileResponse(),
                    server_error=server_error,
                ),
            ],
        )
    else:
        create_commit_mock = patch_arc_create_commit(
            responses=[
                types.ResponseMock(
                    message=repo_pb2.CommitFileResponse(
                        Commit=expected_commit,
                    ),
                ),
            ],
        )

    call = library_context.arc_api.create_commit(
        user=expected_user,
        branch=expected_branch,
        path=expected_path,
        data=expected_data,
        message=expected_message,
    )
    commit = await _try_call(call, expected_error)
    if not expected_error:
        assert commit == expected_commit

    create_commit_mock_request = create_commit_mock.calls.pop().pop('request')
    assert create_commit_mock_request == repo_pb2.CommitFileRequest(
        Branch=f'users/{expected_user}/{expected_branch}',
        Path=expected_path,
        Data=expected_data,
        Message=expected_message,
    )
    assert not create_commit_mock.calls


@pytest.mark.parametrize(
    'expected_error, server_error',
    [
        pytest.param(None, None, id='success'),
        pytest.param(
            arc_api.NotFasForwardError,
            types.ServerErrorMock(
                grpc.StatusCode.FAILED_PRECONDITION,
                'arc/server/public.cpp:1543: Not fast forward',
            ),
            id='not_fast_forward_error',
        ),
        pytest.param(
            arc_api.AuthorizationError,
            types.ServerErrorMock(
                grpc.StatusCode.PERMISSION_DENIED,
                'arc/server/public.cpp:1543: Create & fast-forward are '
                'forbidden for ref=users/robot-taxi-clown/test-arc-api '
                'user=robot-taxi-clown-tst',
            ),
            id='auth_error',
        ),
    ],
)
async def test_set_reference(
        patch_arc_set_reference,
        library_context,
        _try_call,
        expected_error,
        server_error,
):
    expected_user = 'robot-taxi-clown-tst'
    expected_branch_name = 'test-arc-api'
    expected_commit_oid = '5930328f6a0d43ab51aab3eff415d6e0753bf92f'
    set_ref_mock = patch_arc_set_reference(
        responses=[
            types.ResponseMock(
                message=repo_pb2.SetRefResponse(), server_error=server_error,
            ),
        ],
    )

    call = library_context.arc_api.set_reference(
        user=expected_user,
        name=expected_branch_name,
        commit_oid=expected_commit_oid,
    )
    await _try_call(call, expected_error)

    set_ref_mock_request = set_ref_mock.calls.pop().pop('request')
    assert set_ref_mock_request == repo_pb2.SetRefRequest(
        Branch=f'users/{expected_user}/{expected_branch_name}',
        CommitOid=expected_commit_oid,
    )
    assert not set_ref_mock.calls


@pytest.mark.parametrize(
    'expected_error, server_error',
    [
        pytest.param(None, None, id='success'),
        pytest.param(
            arc_api.AuthorizationError,
            types.ServerErrorMock(
                grpc.StatusCode.UNAUTHENTICATED,
                'invalid auth: Unauthorized: Blackbox error',
            ),
            id='auth_error',
        ),
        pytest.param(
            arc_api.AuthorizationError,
            types.ServerErrorMock(
                grpc.StatusCode.PERMISSION_DENIED,
                'arc/server/public.cpp:1669: Delete of ref=users/robot-taxi-'
                'clown/test-branch is forbidden for user=robot-taxi-clown-tst',
            ),
            id='auth_error',
        ),
        pytest.param(
            arc_api.NotFoundError,
            types.ServerErrorMock(
                grpc.StatusCode.UNKNOWN,
                'arc/server/public.cpp:1669: TStatus_ECode_NoSuchBranch'
                ' no such branch',
            ),
            id='not_found_error',
        ),
        pytest.param(
            arc_api.Conflict,
            types.ServerErrorMock(
                grpc.StatusCode.ABORTED,
                'arc/server/public.cpp:1669: Expected '
                'f929792c2e1ea8ea1847926ecccab02ebc1a342a but ref is '
                '7d4e2498bea8f1e59e099f8b323d77ebaab9a059',
            ),
            id='conflict_error',
        ),
    ],
)
async def test_delete_reference(
        patch_arc_delete_reference,
        library_context,
        _try_call,
        expected_error,
        server_error,
):
    expected_user = 'robot-taxi-clown-tst'
    expected_branch_name = 'test-branch'
    expected_commit_oid = 'f929792c2e1ea8ea1847926ecccab02ebc1a342a'
    delete_ref_mock = patch_arc_delete_reference(
        responses=[
            types.ResponseMock(
                message=repo_pb2.DeleteRefResponse(),
                server_error=server_error,
            ),
        ],
    )

    call = library_context.arc_api.delete_reference(
        user=expected_user,
        name=expected_branch_name,
        commit_oid=expected_commit_oid,
    )

    await _try_call(call, expected_error)

    delete_ref_mock_request = delete_ref_mock.calls.pop().pop('request')
    assert delete_ref_mock_request == repo_pb2.DeleteRefRequest(
        Branch=f'users/{expected_user}/{expected_branch_name}',
        ExpectedCommitOid=expected_commit_oid,
    )
    assert not delete_ref_mock.calls
