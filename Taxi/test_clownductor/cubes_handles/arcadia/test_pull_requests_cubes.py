import pytest

from arcanum_api import components as arcanum_api
from generated.models import arcanum as arcanum_models

from clownductor.internal.utils.links import startrack


GENERAL_DATA_REQUEST = {
    'job_id': 1,
    'retries': 0,
    'status': 'in_progress',
    'task_id': 1,
}


@pytest.mark.parametrize(
    'custom_pr_title',
    [
        pytest.param('fix clownductor: blah blah', id='custom_pr_title'),
        pytest.param(None, id='default_pr_title'),
    ],
)
@pytest.mark.parametrize('comment', ['add new configs', None])
@pytest.mark.parametrize(
    'st_ticket',
    [
        pytest.param('TAXIREL-123', id='st_ticket_is_not_None'),
        pytest.param(None, id='st_ticket_is_None'),
    ],
)
async def test_generate_pull_request_info(
        call_cube_handle,
        diff_proposal_mock,
        custom_pr_title,
        comment,
        st_ticket,
):
    df_mock, _ = diff_proposal_mock(comment=comment)
    reviewers = ['spolischouck']
    input_data = {
        'diff_proposal': df_mock.serialize(),
        'st_ticket': st_ticket,
        'pull_request_reviewers': reviewers,
    }

    if custom_pr_title:
        input_data['pull_request_title'] = custom_pr_title
        expected_pr_title = custom_pr_title
    else:
        expected_pr_title = df_mock.title

    if comment and st_ticket:
        expected_pr_body = (
            f'{comment}\n\n'
            'Tests: сгенерировано автоматикой\n'
            f'Relates: [{st_ticket}]({startrack.ST_HOST}/{st_ticket})\n'
        )
    elif comment:
        expected_pr_body = f'{comment}\n\nTests: сгенерировано автоматикой\n'
    elif st_ticket:
        expected_pr_body = (
            'Tests: сгенерировано автоматикой\n'
            f'Relates: [{st_ticket}]({startrack.ST_HOST}/{st_ticket})\n'
        )
    else:
        expected_pr_body = 'Tests: сгенерировано автоматикой\n'

    await call_cube_handle(
        'ArcadiaGeneratePullRequestInfo',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': {
                'payload': {
                    'pull_request_title': expected_pr_title,
                    'pull_request_body': expected_pr_body,
                    'pull_request_st_comment_props': {'summonees': reviewers},
                },
                'status': 'success',
            },
        },
    )


@pytest.mark.parametrize('automerge', [True, False, None])
async def test_create_pull_request(
        call_cube_handle,
        arcanum_create_pull_request_mock,
        diff_proposal_mock,
        automerge,
):
    expected_pr_number = 123
    expected_pr_url = 'test-pr-url'
    expected_head_branch = 'test-branch'
    expected_pr_title = 'feat test_service: cool feature'
    expected_pr_body = 'cool description'
    expected_automerge_type = (
        arcanum_api.AutoMergeType.ON_SATISFIED_REQUIREMENTS
        if automerge
        else arcanum_api.AutoMergeType.DISABLED
    )
    df_mock, _ = diff_proposal_mock(title=expected_pr_title)

    create_pull_request_mock = arcanum_create_pull_request_mock(
        pr_number=expected_pr_number, pr_url=expected_pr_url,
    )

    input_data = {
        'user': df_mock.user,
        'base_branch_name': df_mock.base,
        'head_branch_name': expected_head_branch,
        'pull_request_title': expected_pr_title,
        'pull_request_body': expected_pr_body,
        'approve_required': False,
        'robot_for_ship': None,
    }
    if automerge is not None:
        input_data['automerge'] = automerge

    await call_cube_handle(
        'ArcadiaCreatePullRequest',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': {
                'payload': {
                    'pull_request_id': expected_pr_number,
                    'pull_request_url': expected_pr_url,
                },
                'status': 'success',
            },
        },
    )
    assert create_pull_request_mock.calls == [
        {
            'args': (),
            'kwargs': {
                'user': df_mock.user,
                'base': df_mock.base,
                'head': expected_head_branch,
                'title': expected_pr_title,
                'description': expected_pr_body,
                'automerge': expected_automerge_type,
            },
        },
    ]


@pytest.mark.parametrize(
    'pr_status, pr_has_bad_status',
    [
        ('open', False),
        ('uploading', False),
        ('merging', False),
        ('merged', False),
        ('conflicts', True),
        ('errors', True),
        ('discarding', True),
        ('discarded', True),
        ('fatal_error', True),
    ],
)
@pytest.mark.parametrize(
    'is_mergeable, checks_filename',
    [
        pytest.param(True, 'all_checks_satisfied.json'),
        pytest.param(False, 'some_checks_in_progress.json'),
    ],
)
async def test_wait_status_mergeable_pr(
        call_cube_handle,
        arcanum_get_review_request_mock,
        load_json,
        pr_status,
        pr_has_bad_status,
        is_mergeable,
        checks_filename,
):
    expected_pr_number = 123
    expected_pr_url = 'test-pr-url'
    expected_st_comment = (
        'PR is ready to review.\n'
        f'Approve and merge (({expected_pr_url} PR #{expected_pr_number}))'
    )
    checks = [
        arcanum_models.Check.deserialize(check_data, allow_extra=True)
        for check_data in load_json(checks_filename)
    ]

    get_review_request_mock = arcanum_get_review_request_mock(
        pr_number=expected_pr_number,
        pr_url=expected_pr_url,
        full_status=arcanum_api.PullRequestStatus(pr_status),
        checks=checks,
    )

    input_data = {
        'pull_request_id': expected_pr_number,
        'pull_request_url': expected_pr_url,
        'approve_required': False,
        'robot_for_ship': None,
    }
    if pr_has_bad_status:
        content_expected = {
            'payload': {'st_comment': None},
            'status': 'failed',
            'error_message': (
                f'PR #{expected_pr_number} in bad terminal status: {pr_status}'
            ),
        }
    else:
        if is_mergeable:
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

    await call_cube_handle(
        'ArcadiaWaitStatusMergeablePR',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': content_expected,
        },
    )
    request = get_review_request_mock.next_call()['request']
    assert request.path == '/arcanum/api/v1/review-requests/123'
    assert request.query == {'fields': 'checks,full_status,id,url'}
    assert not get_review_request_mock.has_calls


@pytest.mark.parametrize(
    'pr_status, pr_has_bad_status',
    [
        ('open', False),
        ('uploading', False),
        ('merging', False),
        ('merged', False),
        ('conflicts', True),
        ('errors', True),
        ('discarding', True),
        ('discarded', True),
        ('fatal_error', True),
    ],
)
async def test_wait_merge_pr(
        call_cube_handle,
        arcanum_get_pull_request_mock,
        pr_status,
        pr_has_bad_status,
):
    expected_pr_number = 123
    expected_pr_url = 'test-pr-url'
    expected_st_comment = (
        f'(({expected_pr_url} PR #{expected_pr_number})) is merged.'
    )

    get_pull_request_mock = arcanum_get_pull_request_mock(
        pr_number=expected_pr_number,
        pr_url=expected_pr_url,
        status=arcanum_api.PullRequestStatus(pr_status),
    )

    input_data = {
        'pull_request_id': expected_pr_number,
        'pull_request_url': expected_pr_url,
        'approve_required': False,
        'robot_for_ship': None,
    }
    if pr_has_bad_status:
        content_expected = {
            'payload': {'pull_request_state': None, 'st_comment': None},
            'status': 'failed',
            'error_message': (
                f'PR #{expected_pr_number} in bad terminal status: {pr_status}'
            ),
        }
    else:
        if pr_status == 'merged':
            content_expected = {
                'payload': {
                    'pull_request_state': pr_status,
                    'st_comment': expected_st_comment,
                },
                'status': 'success',
            }
        else:
            content_expected = {
                'payload': {'pull_request_state': None, 'st_comment': None},
                'sleep_duration': 30,
                'status': 'in_progress',
            }

    await call_cube_handle(
        'ArcadiaWaitMergePullRequest',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': content_expected,
        },
    )
    assert get_pull_request_mock.calls == [
        {
            'args': (),
            'kwargs': {
                'return_additional_fields': ['status'],
                'number': expected_pr_number,
            },
        },
    ]
