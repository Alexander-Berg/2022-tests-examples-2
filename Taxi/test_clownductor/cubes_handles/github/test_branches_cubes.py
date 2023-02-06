import pytest

from client_github import components as github


@pytest.mark.parametrize(
    'error',
    [
        pytest.param(None, id='success'),
        pytest.param(
            github.NotFoundError(status_code=404, content='test'), id='error',
        ),
    ],
)
async def test_create_branch(
        call_cube_handle,
        sha1,
        github_create_reference_mock,
        diff_proposal_mock,
        error,
):
    expected_commit_sha = sha1('newcommitsha')
    if error is None:
        create_reference_mock = github_create_reference_mock(
            commit_sha=expected_commit_sha,
        )
        content_expected = {
            'payload': {'commit_sha': expected_commit_sha},
            'status': 'success',
        }
    else:
        create_reference_mock = github_create_reference_mock(exc=error)
        content_expected = {
            'payload': {'commit_sha': None},
            'status': 'in_progress',
            'sleep_duration': 30,
        }

    df_mock, _ = diff_proposal_mock()
    input_data = {
        'user': df_mock.user,
        'repo': df_mock.repo,
        'base_commit_sha': 'basecommitsha',
        'branch_name': 'test-branch',
    }

    await call_cube_handle(
        'GithubCreateBranch',
        {
            'data_request': {
                'input_data': input_data,
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            'content_expected': content_expected,
        },
    )
    assert len(create_reference_mock.calls) == 1


async def test_move_branch_head(
        call_cube_handle,
        sha1,
        github_update_reference_mock,
        diff_proposal_mock,
):
    update_reference_mock = github_update_reference_mock()
    df_mock, _ = diff_proposal_mock()
    input_data = {
        'user': df_mock.user,
        'repo': df_mock.repo,
        'branch_name': 'test-branch',
        'commit_sha': sha1('commitsha'),
    }

    await call_cube_handle(
        'GithubMoveBranchHead',
        {
            'data_request': {
                'input_data': input_data,
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            'content_expected': {'status': 'success'},
        },
    )
    assert len(update_reference_mock.calls) == 1


async def test_merge_branch(
        call_cube_handle, github_merge_branch_object_mock, diff_proposal_mock,
):
    expected_head_branch_name = 'test-branch'
    merge_branch_object_mock = github_merge_branch_object_mock(
        head_branch_name=expected_head_branch_name,
    )
    df_mock, _ = diff_proposal_mock()
    input_data = {
        'user': df_mock.user,
        'repo': df_mock.repo,
        'base_branch_name': df_mock.base,
        'head_branch_name': expected_head_branch_name,
    }

    await call_cube_handle(
        'GithubMergeBranch',
        {
            'data_request': {
                'input_data': input_data,
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            'content_expected': {
                'payload': {
                    'merge_sha': 'e3443502b8fd692b789f9af514b335bce53f0667',
                },
                'status': 'success',
            },
        },
    )
    assert len(merge_branch_object_mock.calls) == 1


async def test_delete_branch(
        call_cube_handle, github_delete_reference_mock, diff_proposal_mock,
):
    expected_head_branch_name = 'test-branch'
    delete_reference_mock = github_delete_reference_mock(
        branch_name=expected_head_branch_name,
    )
    df_mock, _ = diff_proposal_mock()
    input_data = {
        'user': df_mock.user,
        'repo': df_mock.repo,
        'branch_name': expected_head_branch_name,
    }

    await call_cube_handle(
        'GithubDeleteBranch',
        {
            'data_request': {
                'input_data': input_data,
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            'content_expected': {'status': 'success'},
        },
    )
    assert len(delete_reference_mock.calls) == 1
