import pytest

from testsuite.mockserver import classes as mock_types


GENERAL_DATA_REQUEST = {
    'job_id': 1,
    'retries': 0,
    'status': 'in_progress',
    'task_id': 1,
}


@pytest.mark.parametrize(
    'owner, recipe_name',
    [
        pytest.param(
            'arcadia', 'ArcadiaMergeDiffProposalWithPR', id='arcadia',
        ),
        pytest.param('taxi', 'GithubMergeDiffProposalWithPR', id='github'),
    ],
)
async def test_merge_diff_proposal_with_pr(
        mock_task_processor,
        call_cube_handle,
        diff_proposal_mock,
        owner,
        recipe_name,
):
    expected_tp_job_id = 123
    expected_task_id = 456
    st_ticket = 'TAXIREL-123'
    reviewers = ['spolischouck']

    @mock_task_processor('/v1/jobs/start/')
    def _job_start_mock(request: mock_types.MockserverRequest):
        return {'job_id': expected_tp_job_id}

    df_mock, df_sha = diff_proposal_mock(user=owner)

    input_data = {
        'diff_proposal': df_mock.serialize(),
        'initiator': 'spolischouck',
        'st_ticket': st_ticket,
        'automerge': True,
        'reviewers': reviewers,
    }
    expected_job_vars = {
        'diff_proposal': df_mock.serialize(),
        'st_ticket': st_ticket,
        'automerge': True,
        'reviewers': reviewers,
    }

    if recipe_name.startswith('Arcadia'):
        expected_job_vars.update(
            {'approve_required': False, 'robot_for_ship': None},
        )

    content_expected = {
        'payload': {'job_id': expected_tp_job_id},
        'status': 'success',
    }

    await call_cube_handle(
        'MetaStartDiffProposalWithPR',
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
        'provider_name': 'clownductor',
        'recipe_name': recipe_name,
        'job_vars': expected_job_vars,
        'change_doc_id': (
            f'clownductor-{recipe_name}-{df_mock.user}-{df_mock.repo}-{df_sha}'
        ),
        'idempotency_token': (
            f'clownductor-{recipe_name}-{df_mock.user}-'
            f'{df_mock.repo}-{df_sha}-{expected_task_id}'
        ),
    }
    assert not _job_start_mock.has_calls
