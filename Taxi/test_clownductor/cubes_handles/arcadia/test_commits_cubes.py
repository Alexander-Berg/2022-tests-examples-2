import copy
import hashlib
import itertools

import grpc
import pytest

from arc_api import types
from yandex.arc.api.public import repo_pb2


GENERAL_DATA_REQUEST = {
    'job_id': 1,
    'retries': 0,
    'status': 'in_progress',
    'task_id': 1,
}


TRANSLATIONS = {
    'tickets.arcadia_check_files_comment': {
        'ru': 'Bad files: {not_found_files}',
    },
}


@pytest.mark.parametrize(
    'branch_name, expected_branch_name',
    [
        ('trunk', 'trunk'),
        ('test-branch', 'users/robot-taxi-clown/test-branch'),
    ],
)
async def test_fetch_latest_commit(
        patch_arc_get_commit,
        call_cube_handle,
        arc_commit_mock,
        branch_name,
        expected_branch_name,
):
    expected_commit = arc_commit_mock
    get_commit_mock = patch_arc_get_commit(
        revision=expected_branch_name, commit=expected_commit,
    )

    input_data = {
        'user': 'robot-taxi-clown',
        'branch_name': branch_name,
        'approve_required': False,
        'robot_for_ship': None,
    }

    await call_cube_handle(
        'ArcadiaFetchLatestCommit',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': {
                'payload': {'commit_oid': expected_commit.Oid},
                'status': 'success',
            },
        },
    )

    get_commit_mock_request = get_commit_mock.calls.pop().pop('request')
    assert get_commit_mock_request == repo_pb2.GetCommitRequest(
        Revision=expected_branch_name,
    )
    assert not get_commit_mock.calls


async def test_fail_cube_arcadia_commit_files(
        arc_mockserver,
        patch_commit_service,
        patch_arc_create_commit,
        patch_arc_get_commit,
        call_cube_handle,
        arc_commit_mock,
        diff_proposal_mock,
):
    expected_message = 'test'
    expected_branch = 'test-branch'
    filepath = 'path/to/file.yaml'
    file = {
        'filepath': filepath,
        'state': 'created_or_updated',
        'data': 'Content1',
    }
    df_mock, _ = diff_proposal_mock(
        user='robot-taxi-clown', repo='taxi/backend-py3', changes=[file],
    )
    input_data = {
        'user': df_mock.user,
        'repo': df_mock.repo,
        'message': expected_message,
        'branch_name': expected_branch,
        'diff_proposal': df_mock.serialize(),
        'diff_proposal_sha': 'failed_case_sha',
    }
    await call_cube_handle(
        'ArcadiaCommitFiles',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': {
                'payload': {
                    'commits_oid_by_filepaths': {},
                    'last_commit_oid': None,
                },
                'error_message': 'Diff proposal became inconsistent',
                'status': 'failed',
            },
        },
    )


@pytest.mark.parametrize('commit_exists', [True, False])
async def test_commit_single_file(
        arc_mockserver,
        patch_commit_service,
        patch_arc_create_commit,
        patch_arc_get_commit,
        call_cube_handle,
        arc_commit_mock,
        diff_proposal_mock,
        commit_exists,
):
    expected_message = 'test'
    expected_branch = 'test-branch'
    filepath = 'path/to/file.yaml'
    file = {
        'filepath': filepath,
        'state': 'created_or_updated',
        'data': 'Content1',
    }
    df_mock, df_sha = diff_proposal_mock(
        user='robot-taxi-clown', repo='taxi/backend-py3', changes=[file],
    )
    input_data = {
        'user': df_mock.user,
        'repo': df_mock.repo,
        'message': expected_message,
        'branch_name': expected_branch,
        'diff_proposal': df_mock.serialize(),
        'diff_proposal_sha': df_sha,
        'approve_required': False,
        'robot_for_ship': None,
    }

    expected_commit = arc_commit_mock
    expected_commit.Oid = hashlib.sha1(filepath.encode('utf-8')).hexdigest()
    expected_commit.Message = expected_message
    expected_commit.Author = df_mock.user
    expected_filepath = f'{df_mock.repo}/{filepath}'
    commits_oid_by_filepaths = {expected_filepath: expected_commit.Oid}

    if commit_exists:
        create_commit_mock = patch_arc_create_commit(
            init_mockserver=False,
            responses=[
                types.ResponseMock(
                    message=repo_pb2.CommitFileResponse(),
                    server_error=types.ServerErrorMock(
                        grpc.StatusCode.ALREADY_EXISTS,
                        (
                            'arc/server/public.cpp:1131: '
                            'Commit does not change anything'
                        ),
                    ),
                ),
            ],
        )
    else:
        create_commit_mock = patch_arc_create_commit(
            init_mockserver=False,
            responses=[
                types.ResponseMock(
                    message=repo_pb2.CommitFileResponse(
                        Commit=expected_commit,
                    ),
                ),
            ],
        )

    get_commit_mock = patch_arc_get_commit(
        revision=f'users/{df_mock.user}/{expected_branch}',
        commit=expected_commit,
        init_mockserver=False,
    )
    commit_service_mock = patch_commit_service(
        commit_file=create_commit_mock, get_commit=get_commit_mock,
    )
    arc_mockserver(commit_service_mock)

    await call_cube_handle(
        'ArcadiaCommitFiles',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': {
                'payload': {
                    'commits_oid_by_filepaths': commits_oid_by_filepaths,
                    'last_commit_oid': expected_commit.Oid,
                },
                'status': 'success',
            },
        },
    )

    create_commit_mock_request = create_commit_mock.calls.pop().pop('request')
    assert create_commit_mock_request == repo_pb2.CommitFileRequest(
        Branch=f'users/{df_mock.user}/{expected_branch}',
        Path=expected_filepath,
        Data=file['data'].encode('utf-8'),
        Message=expected_message,
    )
    assert not create_commit_mock.calls

    assert len(get_commit_mock.calls) == (1 if commit_exists else 0)


async def test_commit_several_files(
        patch_arc_create_commit,
        call_cube_handle,
        arc_commit_mock,
        diff_proposal_mock,
):
    expected_message = 'test'
    expected_branch = 'test-branch'
    changes = [
        {
            'filepath': 'path/to/file.yaml',
            'state': 'created_or_updated',
            'data': 'Content1',
        },
        {
            'filepath': 'path/to/file2.yaml',
            'state': 'created_or_updated',
            'data': 'Content2',
        },
        {
            'filepath': 'path/to/file3.yaml',
            'state': 'created_or_updated',
            'data': 'Content3',
        },
    ]

    df_mock, df_sha = diff_proposal_mock(
        user='robot-taxi-clown', repo='taxi/backend-py3', changes=changes,
    )
    input_data = {
        'user': df_mock.user,
        'repo': df_mock.repo,
        'message': expected_message,
        'branch_name': expected_branch,
        'diff_proposal': df_mock.serialize(),
        'diff_proposal_sha': df_sha,
        'approve_required': False,
        'robot_for_ship': None,
    }

    commits_oid_by_filepaths = {}
    requests = []
    responses = []
    last_commit_oid = None
    expect_committed_files = []

    for file in df_mock.changes:
        filepath = f'{df_mock.repo}/{file.filepath}'
        expect_committed_files.append(filepath)

        req = repo_pb2.CommitFileRequest(
            Branch=f'users/{df_mock.user}/{expected_branch}',
            Path=filepath,
            Data=file.data.encode('utf-8'),
            Message=expected_message,
        )
        requests.append(req)

        commit = copy.deepcopy(arc_commit_mock)
        commit.Oid = hashlib.sha1(filepath.encode('utf-8')).hexdigest()
        commit.Message = expected_message
        commit.Author = df_mock.user
        resp = types.ResponseMock(
            message=repo_pb2.CommitFileResponse(Commit=commit),
        )
        responses.append(resp)

        commits_oid_by_filepaths[filepath] = commit.Oid
        last_commit_oid = commit.Oid

    create_commit_mock = patch_arc_create_commit(responses=responses)
    last_payload = None

    for retry_count, filepath in enumerate(expect_committed_files):
        if retry_count == len(expect_committed_files) - 1:
            expected_state = {'status': 'success'}
        else:
            expected_state = {'sleep_duration': 1, 'status': 'in_progress'}

        json_data = {
            'data_request': {
                **GENERAL_DATA_REQUEST,
                'retries': retry_count,
                'input_data': input_data,
            },
            'content_expected': {
                'payload': {
                    'commits_oid_by_filepaths': {
                        path: oid
                        for path, oid in commits_oid_by_filepaths.items()
                        if path in expect_committed_files[: retry_count + 1]
                    },
                    'last_commit_oid': commits_oid_by_filepaths[
                        expect_committed_files[: retry_count + 1][-1]
                    ],
                },
                **expected_state,
            },
        }
        if last_payload is not None:
            json_data['data_request']['payload'] = last_payload

        cube_response = await call_cube_handle('ArcadiaCommitFiles', json_data)
        last_payload = (await cube_response.json())['payload']

    assert last_commit_oid

    for call, expected_request in itertools.zip_longest(
            create_commit_mock.calls, requests,
    ):
        assert call['request'] == expected_request

    assert not create_commit_mock.calls


@pytest.mark.translations(clownductor=TRANSLATIONS)
@pytest.mark.features_on('check_arcadia_deleting_files')
@pytest.mark.usefixtures('mock_arc_client', 'st_get_ticket')
async def test_check_files(
        mock,
        patch_file_service,
        call_cube_handle,
        diff_proposal_mock,
        arc_mockserver,
):
    @mock
    def _read_file(request, context):
        assert request.Revision == 'trunk'
        filepath = request.Path
        if filepath == 'taxi/backend-py3/path/to/file2.yaml':
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('file not found in revision')
            return
        if filepath == 'taxi/backend-py3/path/to/file3.yaml':
            data = 'data'
            yield repo_pb2.ReadFileResponse(
                Header=repo_pb2.ReadFileResponse.ReadFileHeader(
                    Oid='853cb0f6a5888d6ecfe2c7acc6a90d42af85b89c',
                    FileSize=len(data),
                ),
            )
            yield repo_pb2.ReadFileResponse(Data=bytes(data, 'utf-8'))
        else:
            raise RuntimeError(f'Unexpected file {filepath}')

    file_service_mock = patch_file_service(read_file=_read_file)
    arc_mockserver(file_service_mock)

    changes = [
        {
            'filepath': 'path/to/file.yaml',
            'state': 'created_or_updated',
            'data': 'Content1',
        },
        {'filepath': 'path/to/file2.yaml', 'state': 'deleting', 'data': ''},
        {'filepath': 'path/to/file3.yaml', 'state': 'deleting', 'data': ''},
    ]

    df_mock, df_sha = diff_proposal_mock(
        user='robot-taxi-clown', repo='taxi/backend-py3', changes=changes,
    )
    input_data = {
        'repo': df_mock.repo,
        'st_task': 'TAXIMOCK-001',
        'diff_proposal': df_mock.serialize(),
        'diff_proposal_sha': df_sha,
    }
    expected_df = df_mock.serialize()
    del expected_df['changes'][1]

    json_data = {
        'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
        'content_expected': {
            'payload': {
                'check_files_comment_props': {'summonees': []},
                'check_files_comment_skip': False,
                'check_files_comment_text': 'Bad files: - path/to/file2.yaml',
                'diff_proposal': expected_df,
                'diff_proposal_sha': (
                    '20f479f8e5204ecd2b1d24b2dd5f33d1ea444611'
                ),
            },
            'status': 'success',
        },
    }
    await call_cube_handle('ArcadiaCheckFiles', json_data)
