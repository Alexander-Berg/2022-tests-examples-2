import pytest

import diff_proposal.components as diff_proposal_lib
from testsuite.mockserver import classes as mock_types


@pytest.mark.parametrize('st_ticket', ['TAXIREL-123', None])
@pytest.mark.parametrize(
    'title, slug',
    [
        pytest.param(
            'feat test_service: cool feature 15',
            'feat-test_service-cool-feature-15',
        ),
        pytest.param(
            'feat test_service: hello_world!;',
            'feat-test_service-hello_world',
        ),
    ],
)
async def test_generate_basic_info(
        call_cube_handle, diff_proposal_mock, st_ticket, title, slug,
):
    df_mock, df_sha = diff_proposal_mock(title=title)
    input_data = {'diff_proposal': df_mock.serialize()}

    if st_ticket:
        expected_branch_name = f'{st_ticket}-{slug}-{df_sha}'
        input_data['st_ticket'] = st_ticket
    else:
        expected_branch_name = f'{slug}-{df_sha}'

    await call_cube_handle(
        'GithubGenerateBasicInfo',
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
                    'user': df_mock.user,
                    'repo': df_mock.repo,
                    'changes_title': df_mock.title,
                    'base_branch_name': df_mock.base,
                    'head_branch_name': expected_branch_name,
                    'diff_proposal_sha': df_sha,
                },
                'status': 'success',
            },
        },
    )


@pytest.mark.parametrize(
    'refresh_diff_proposal_sha',
    [
        pytest.param(True, id='good_diff'),
        pytest.param(None, id='inconsistent_diff'),
    ],
)
async def test_create_blobs(
        call_cube_handle,
        sha1,
        base64,
        diff_proposal_mock,
        github_create_blob_mock,
        refresh_diff_proposal_sha,
):
    create_blob_mock = github_create_blob_mock()

    df_mock, df_sha = diff_proposal_mock(title='first title')
    df_mock.title = 'new title'

    if refresh_diff_proposal_sha:
        df_sha = diff_proposal_lib.sha1(df_mock)
        created_or_updated = (
            diff_proposal_lib.FileDiffState.CREATED_OR_UPDATED.value
        )
        content_expected = {
            'payload': {
                'blobs_sha_by_filepaths': {
                    file_diff.filepath: sha1(base64(file_diff.data))
                    for file_diff in df_mock.changes
                    if file_diff.state == created_or_updated
                },
            },
            'status': 'success',
        }
    else:
        content_expected = {
            'error_message': 'Diff proposal became inconsistent',
            'payload': {'blobs_sha_by_filepaths': {}},
            'status': 'failed',
        }

    input_data = {
        'user': df_mock.user,
        'repo': df_mock.user,
        'diff_proposal': df_mock.serialize(),
        'diff_proposal_sha': df_sha,
    }

    await call_cube_handle(
        'GithubCreateBlobs',
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
    if refresh_diff_proposal_sha:
        assert len(create_blob_mock.calls) == 2
    else:
        assert not create_blob_mock.calls


async def test_create_tree_from_blobs(
        call_cube_handle,
        sha1,
        base64,
        diff_proposal_mock,
        github_create_tree_mock,
):
    expected_tree_sha = sha1('treesha')
    content_expected = {
        'payload': {'tree_sha': expected_tree_sha},
        'status': 'success',
    }
    create_tree_mock = github_create_tree_mock(
        updated_node_count=2,
        deleted_node_count=1,
        new_tree_sha=expected_tree_sha,
    )

    df_mock, _ = diff_proposal_mock()

    created_or_updated = (
        diff_proposal_lib.FileDiffState.CREATED_OR_UPDATED.value
    )
    input_data = {
        'user': df_mock.user,
        'repo': df_mock.user,
        'diff_proposal': df_mock.serialize(),
        'base_tree_sha': sha1('basetreesha'),
        'blobs_sha_by_filepaths': {
            file_diff.filepath: sha1(base64(file_diff.data))
            for file_diff in df_mock.changes
            if file_diff.state == created_or_updated
        },
    }

    await call_cube_handle(
        'GithubCreateTreeFromBlobs',
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
    assert len(create_tree_mock.calls) == 1


@pytest.mark.parametrize(
    'cube_name, recipe, extra_job_vars',
    [
        pytest.param(
            'StartGithubMergeDiffProposalWithoutPR',
            'GithubMergeDiffProposalWithoutPR',
            {},
            id='without_pr',
        ),
        pytest.param(
            'StartGithubMergeDiffProposalWithPR',
            'GithubMergeDiffProposalWithPR',
            {'automerge': True, 'reviewers': ['spolischouck']},
            id='with_pr',
        ),
    ],
)
async def test_start_github_merge_diff_proposal(
        mock_task_processor,
        call_cube_handle,
        diff_proposal_mock,
        cube_name,
        recipe,
        extra_job_vars,
):
    st_ticket = 'TAXIREL-123'
    expected_job_id = 1

    @mock_task_processor('/v1/jobs/start/')
    def _job_start_mock(request: mock_types.MockserverRequest):
        return {'job_id': expected_job_id}

    df_mock, df_sha = diff_proposal_mock()

    input_data = {
        'diff_proposal': df_mock.serialize(),
        'initiator': 'spolischouck',
        'st_ticket': st_ticket,
    }
    expected_job_vars = {
        'diff_proposal': df_mock.serialize(),
        'st_ticket': st_ticket,
    }
    if extra_job_vars:
        input_data = {**input_data, **extra_job_vars}
        expected_job_vars = {**expected_job_vars, **extra_job_vars}

    task_id = 456
    job_id = 123
    content_expected = {
        'payload': {'job_id': expected_job_id},
        'status': 'success',
    }

    await call_cube_handle(
        cube_name,
        {
            'data_request': {
                'input_data': input_data,
                'job_id': job_id,
                'retries': 0,
                'status': 'in_progress',
                'task_id': task_id,
            },
            'content_expected': content_expected,
        },
    )
    tp_start_job_request = _job_start_mock.next_call()['request']
    assert tp_start_job_request.headers['X-Yandex-Login'] == 'spolischouck'
    assert tp_start_job_request.json == {
        'change_doc_id': (
            f'clownductor-{recipe}-{df_mock.user}-{df_mock.repo}-{df_sha}'
        ),
        'idempotency_token': (
            f'clownductor-{recipe}-{df_mock.user}-'
            f'{df_mock.repo}-{df_sha}-{task_id}'
        ),
        'job_vars': expected_job_vars,
        'provider_name': 'clownductor',
        'recipe_name': recipe,
    }
    assert not _job_start_mock.has_calls
