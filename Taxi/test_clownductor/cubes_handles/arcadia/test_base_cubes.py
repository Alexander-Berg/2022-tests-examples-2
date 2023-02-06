import pytest

from testsuite.mockserver import classes as mock_types


GENERAL_DATA_REQUEST = {
    'job_id': 1,
    'retries': 0,
    'status': 'in_progress',
    'task_id': 1,
}


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
        simple_secdist, call_cube_handle, diff_proposal_mock, title, slug,
):
    df_mock, df_sha = diff_proposal_mock(title=title)
    st_ticket = 'TAXIREL-123'
    expected_user = 'robot-taxi'
    expected_branch_name = f'{st_ticket}-{slug}-{df_sha}'

    simple_secdist['ROBOT_CREDENTIALS'].update({'login': expected_user})
    input_data = {'diff_proposal': df_mock.serialize(), 'st_ticket': st_ticket}
    content_expected = {
        'status': 'success',
        'payload': {
            'user': expected_user,
            'repo': df_mock.repo,
            'changes_title': df_mock.title,
            'base_branch_name': df_mock.base,
            'head_branch_name': expected_branch_name,
            'diff_proposal_sha': df_sha,
        },
    }

    await call_cube_handle(
        'ArcadiaGenerateBasicInfo',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': content_expected,
        },
    )


async def test_start_arcadia_merge_diff_proposal(
        mock_task_processor, call_cube_handle, diff_proposal_mock,
):
    expected_job_id = 123
    expected_task_id = 456
    st_ticket = 'TAXIREL-123'
    recipe_name = 'ArcadiaMergeDiffProposalWithPR'

    @mock_task_processor('/v1/jobs/start/')
    def _job_start_mock(request: mock_types.MockserverRequest):
        return {'job_id': expected_job_id}

    df_mock, df_sha = diff_proposal_mock(user='arcadia')

    input_data = {
        'diff_proposal': df_mock.serialize(),
        'initiator': 'spolischouck',
        'st_ticket': st_ticket,
        'automerge': True,
        'reviewers': ['spolischouck'],
    }
    expected_job_vars = {
        'diff_proposal': df_mock.serialize(),
        'st_ticket': st_ticket,
        'automerge': True,
        'reviewers': ['spolischouck'],
        'approve_required': False,
        'robot_for_ship': None,
    }

    content_expected = {
        'payload': {'job_id': expected_job_id},
        'status': 'success',
    }

    await call_cube_handle(
        'StartArcadiaMergeDiffProposalWithPR',
        {
            'data_request': {
                **GENERAL_DATA_REQUEST,
                'input_data': input_data,
                'task_id': expected_task_id,
            },
            'content_expected': content_expected,
        },
    )

    tp_start_job_request = _job_start_mock.next_call()['request']
    assert tp_start_job_request.headers['X-Yandex-Login'] == 'spolischouck'
    assert tp_start_job_request.json == {
        'change_doc_id': (
            f'clownductor-{recipe_name}-{df_mock.user}-{df_mock.repo}-{df_sha}'
        ),
        'idempotency_token': (
            f'clownductor-{recipe_name}-{df_mock.user}-'
            f'{df_mock.repo}-{df_sha}-{expected_task_id}'
        ),
        'job_vars': expected_job_vars,
        'provider_name': 'clownductor',
        'recipe_name': recipe_name,
    }
    assert not _job_start_mock.has_calls
