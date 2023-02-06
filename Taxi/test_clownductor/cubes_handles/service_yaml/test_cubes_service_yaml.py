import pytest

import diff_proposal.components as diff_lib


GENERAL_DATA_REQUEST = {
    'job_id': 1,
    'retries': 0,
    'status': 'in_progress',
    'task_id': 1,
}


@pytest.mark.parametrize(
    'owner, repo, base',
    [
        pytest.param(
            'taxi',
            'uservices',
            'develop',
            marks=pytest.mark.pgsql(
                'clownductor', files=['test_service_in_github.sql'],
            ),
            id='service_yaml_in_github',
        ),
        pytest.param(
            'arcadia',
            'taxi/uservices/services/test_service',
            'trunk',
            marks=pytest.mark.pgsql(
                'clownductor', files=['test_service_in_arcadia.sql'],
            ),
            id='service_yaml_in_arcadia',
        ),
    ],
)
@pytest.mark.parametrize(
    'service_yaml_content',
    [
        pytest.param('test_test:\n  test', id='new_content'),
        pytest.param(None, id='no_new_content'),
    ],
)
async def test_generate_basic_info(
        call_cube_handle,
        diff_proposal_mock,
        service_yaml_content,
        owner,
        repo,
        base,
):
    title = 'feat test_service: change service.yaml'
    if service_yaml_content is not None:
        changes = [
            {
                'filepath': 'service.yaml',
                'data': service_yaml_content,
                'state': diff_lib.FileDiffState.CREATED_OR_UPDATED.value,
            },
        ]
        diff_proposal, _ = diff_proposal_mock(
            user=owner,
            repo=repo,
            base=base,
            title=title,
            changes=changes,
            comment=(
                'Update service.yaml during job'
                f'#{GENERAL_DATA_REQUEST["job_id"]}'
            ),
        )
        expected_payload = {'diff_proposal': diff_proposal.serialize()}
    else:
        expected_payload = {}

    input_data = {'service_id': 1, 'content': service_yaml_content}
    content_expected = {'status': 'success', 'payload': expected_payload}

    await call_cube_handle(
        'GenerateServiceYamlChanges',
        {
            'data_request': {**GENERAL_DATA_REQUEST, 'input_data': input_data},
            'content_expected': content_expected,
        },
    )
