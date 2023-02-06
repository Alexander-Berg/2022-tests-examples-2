import pytest

import client_github.components as github

from clownductor.internal.utils.links import startrack


PULL_REQUEST_URL_MOCK = github.CreatePullRequestResult(
    html_url='https://github.yandex-team.ru/taxi/backend-py3/pull/100500',
    number=100500,
)


GENERAL_DATA_REQUEST = {
    'job_id': 1,
    'retries': 0,
    'status': 'in_progress',
    'task_id': 1,
}


@pytest.mark.parametrize(
    'custom_pr_title',
    [
        pytest.param('bugfix: blah blah', id='custom_pr_title'),
        pytest.param(None, id='default_pr_title'),
    ],
)
@pytest.mark.parametrize('comment', ['add new configs', None])
async def test_generate_pull_request_info(
        call_cube_handle, diff_proposal_mock, custom_pr_title, comment,
):
    df_mock, _ = diff_proposal_mock(comment=comment)
    st_ticket = 'TAXIREL-123'
    reviwers = ['spolischouck']
    input_data = {
        'diff_proposal': df_mock.serialize(),
        'pull_request_reviewers': reviwers,
        'st_ticket': st_ticket,
    }

    if custom_pr_title:
        input_data['pull_request_title'] = custom_pr_title
        expected_pr_title = custom_pr_title
    else:
        expected_pr_title = df_mock.title

    if comment:
        expected_pr_body = (
            f'{comment}\n\n'
            'Tests: сгенерировано автоматикой\n'
            f'Relates: [{st_ticket}]({startrack.ST_HOST}/{st_ticket})\n'
        )
    else:
        expected_pr_body = (
            'Tests: сгенерировано автоматикой\n'
            f'Relates: [{st_ticket}]({startrack.ST_HOST}/{st_ticket})\n'
        )

    await call_cube_handle(
        'GithubGeneratePullRequestInfo',
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
                    'pull_request_title': expected_pr_title,
                    'pull_request_body': expected_pr_body,
                    'pull_request_labels': [],
                    'pull_request_st_comment_props': {'summonees': reviwers},
                },
                'status': 'success',
            },
        },
    )


@pytest.mark.parametrize('pr_exists', [True, False])
async def test_create_pull_request(
        call_cube_handle,
        github_create_pull_request_mock,
        github_github_get_pull_requests_mock,
        diff_proposal_mock,
        pr_exists,
):

    expected_pr_number = 1
    expected_pr_url = 'test-pr-url'
    expected_head_branch = 'test-branch'
    df_mock, _ = diff_proposal_mock()

    if pr_exists:
        create_pull_request_mock = github_create_pull_request_mock(
            exc=github.AlreadyExistsError(status_code=422, content='test'),
        )
    else:
        create_pull_request_mock = github_create_pull_request_mock(
            expected_pr_number, expected_pr_url,
        )

    get_pull_requests_mock = github_github_get_pull_requests_mock(
        repo=df_mock.repo,
        base_branch=df_mock.base,
        head_branch=expected_head_branch,
        pr_url=expected_pr_url,
    )

    expected_pr_title = f'feat test_service: {df_mock.title}'
    expected_pr_body = 'cool description'
    input_data = {
        'user': df_mock.user,
        'repo': df_mock.repo,
        'base_branch_name': df_mock.base,
        'head_branch_name': expected_head_branch,
        'pull_request_title': expected_pr_title,
        'pull_request_body': expected_pr_body,
    }

    await call_cube_handle(
        'GithubCreatePullRequest',
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
                    'pull_request_id': expected_pr_number,
                    'pull_request_url': expected_pr_url,
                },
                'status': 'success',
            },
        },
    )
    assert len(create_pull_request_mock.calls) == 1
    assert len(get_pull_requests_mock.calls) == (1 if pr_exists else 0)


@pytest.mark.parametrize(
    'has_diff',
    [pytest.param(True, id='diff'), pytest.param(False, id='no_diff')],
)
async def test_create_pull_request_no_diff(
        call_cube_handle,
        github_create_pull_request_mock,
        diff_proposal_mock,
        has_diff,
):

    expected_pr_number = 1
    expected_pr_url = 'test-pr-url'
    expected_head_branch = 'test-branch'
    df_mock, _ = diff_proposal_mock()

    if not has_diff:
        create_pull_request_mock = github_create_pull_request_mock(
            exc=github.NoDiffError(status_code=422, content='test'),
        )
        expected_payload = {'pull_request_id': None, 'pull_request_url': None}
    else:
        create_pull_request_mock = github_create_pull_request_mock(
            expected_pr_number, expected_pr_url,
        )
        expected_payload = {
            'pull_request_id': expected_pr_number,
            'pull_request_url': expected_pr_url,
        }

    expected_pr_title = f'feat test_service: {df_mock.title}'
    expected_pr_body = 'cool description'
    input_data = {
        'user': df_mock.user,
        'repo': df_mock.repo,
        'base_branch_name': df_mock.base,
        'head_branch_name': expected_head_branch,
        'pull_request_title': expected_pr_title,
        'pull_request_body': expected_pr_body,
    }

    await call_cube_handle(
        'GithubCreatePullRequest',
        {
            'data_request': {
                'input_data': input_data,
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            'content_expected': {
                'payload': expected_payload,
                'status': 'success',
            },
        },
    )
    assert len(create_pull_request_mock.calls) == 1


@pytest.mark.parametrize(
    'skip',
    [
        pytest.param(False, id='valid_params_need_work'),
        pytest.param(True, id='empty_params_not_need_work'),
    ],
)
@pytest.mark.parametrize(
    'pr_is_mergeable',
    [
        pytest.param(True, id='mergable'),
        pytest.param(False, id='not_mergable'),
    ],
)
async def test_wait_status_mergeable_pr(
        call_cube_handle, github_get_pull_request_mock, skip, pr_is_mergeable,
):
    if not skip:
        expected_pr_number = PULL_REQUEST_URL_MOCK.number
        expected_pr_url = PULL_REQUEST_URL_MOCK.html_url
        expected_st_comment = (
            'PR is ready to review.\n'
            f'Approve and merge (({expected_pr_url} PR #{expected_pr_number}))'
        )

        if pr_is_mergeable:
            content_expected = {
                'payload': {'st_comment': expected_st_comment},
                'status': 'success',
            }
        else:
            content_expected = {
                'payload': {'st_comment': None},
                'status': 'in_progress',
                'sleep_duration': 30,
            }
    else:
        expected_pr_number = None
        expected_pr_url = None
        content_expected = {
            'payload': {'st_comment': 'PR is skipped.\n'},
            'status': 'success',
        }

    input_data = {
        'gh_user': 'taxi',
        'pull_request_repo': 'backend-py3',
        'pull_request_id': expected_pr_number,
        'pull_request_url': expected_pr_url,
    }

    get_pull_request_mock = github_get_pull_request_mock(
        number=expected_pr_number,
        pr_url=expected_pr_url,
        mergeable=pr_is_mergeable,
    )

    await call_cube_handle(
        'GithubWaitStatusMergeablePR',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': content_expected,
        },
    )

    assert len(get_pull_request_mock.calls) == (1 if not skip else 0)


@pytest.mark.parametrize(
    'skip',
    [
        pytest.param(False, id='valid_params_need_work'),
        pytest.param(True, id='empty_params_not_need_work'),
    ],
)
@pytest.mark.parametrize(
    'pr_is_merged, pr_state',
    [
        pytest.param(False, 'open', id='wait_for_merge'),
        pytest.param(True, 'closed', id='merged'),
        pytest.param(False, 'closed', id='closed'),
    ],
)
async def test_wait_merge_pr(
        call_cube_handle,
        github_get_pull_request_mock,
        skip,
        pr_is_merged,
        pr_state,
):
    if not skip:
        expected_pr_number = PULL_REQUEST_URL_MOCK.number
        expected_pr_url = PULL_REQUEST_URL_MOCK.html_url
        expected_st_comment = (
            f'(({expected_pr_url} PR #{expected_pr_number})) is merged.'
        )

        if pr_is_merged:
            content_expected = {
                'payload': {
                    'pull_request_state': pr_state,
                    'st_comment': expected_st_comment,
                },
                'status': 'success',
            }
        else:
            if pr_state == 'open':
                content_expected = {
                    'payload': {
                        'pull_request_state': None,
                        'st_comment': None,
                    },
                    'status': 'in_progress',
                    'sleep_duration': 30,
                }
            else:
                content_expected = {
                    'payload': {
                        'pull_request_state': None,
                        'st_comment': None,
                    },
                    'status': 'failed',
                    'error_message': (
                        f'Pull request #{expected_pr_number} is closed'
                    ),
                }
    else:
        expected_pr_number = None
        expected_pr_url = None
        content_expected = {
            'payload': {'pull_request_state': None, 'st_comment': None},
            'status': 'success',
        }

    input_data = {
        'gh_user': 'taxi',
        'pull_request_repo': 'backend-py3',
        'pull_request_id': expected_pr_number,
        'pull_request_url': expected_pr_url,
    }

    get_pull_request_mock = github_get_pull_request_mock(
        number=expected_pr_number,
        pr_url=expected_pr_url,
        merged=pr_is_merged,
        state=github.PullRequestState(pr_state),
    )

    await call_cube_handle(
        'GithubWaitMergePR',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': content_expected,
        },
    )

    assert len(get_pull_request_mock.calls) == (1 if not skip else 0)
