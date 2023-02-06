import pytest


EXPECTED_STRONGBOX_CHANGES_DATA = """{
    "settings_override": {
        "TVM_SERVICES": {
            "some_tvm_name": {{ TVM_TAXI_DEVOPS_SOME_TVM_NAME }}
        }
    }
}
"""


@pytest.fixture(name='mock_st_comments')
def _mock_st_comments(mockserver):
    @mockserver.json_handler('/startrek/issues/TICKET-1/comments')
    def _comments(request):
        return {}


@pytest.mark.parametrize(
    'cube_name, input_data, expected_payload, '
    'file_path, is_success, error_message',
    [
        pytest.param(
            'GenerateStrongboxDiffProposal',
            {
                'service_id': 1,
                'project': 'taxi-devops',
                'tvm_name': 'some_tvm_name',
            },
            {},
            None,
            True,
            None,
            id='old_strongbox_merging_flow',
        ),
        pytest.param(
            'GenerateStrongboxDiffProposal',
            {
                'st_task': 'TICKET-1',
                'service_id': 1,
                'project': 'taxi-devops',
                'tvm_name': 'some_tvm_name',
            },
            {
                'diff_proposal': {
                    'user': 'taxi',
                    'repo': 'strongbox-conf-stable',
                    'title': (
                        'feat clownductor: create strongbox secdist template'
                    ),
                    'changes': [
                        {
                            'filepath': 'secdist/clownductor.tpl',
                            'state': 'created_or_updated',
                            'data': EXPECTED_STRONGBOX_CHANGES_DATA,
                        },
                    ],
                    'base': 'master',
                    'comment': 'create Strongbox config',
                },
            },
            None,
            True,
            None,
            marks=pytest.mark.features_on('use_new_strongbox_merging_flow'),
            id='new_strongbox_merging_flow_to_github_stable',
        ),
        pytest.param(
            'GenerateStrongboxDiffProposal',
            {
                'service_id': 1,
                'project': 'taxi-devops',
                'tvm_name': 'some_tvm_name',
                'strongbox_env': 'testing',
            },
            {
                'diff_proposal': {
                    'user': 'taxi',
                    'repo': 'strongbox-conf-testing',
                    'title': (
                        'feat clownductor: create strongbox secdist template'
                    ),
                    'changes': [
                        {
                            'filepath': 'secdist/clownductor.tpl',
                            'state': 'created_or_updated',
                            'data': EXPECTED_STRONGBOX_CHANGES_DATA,
                        },
                    ],
                    'base': 'master',
                    'comment': 'create Strongbox config',
                },
            },
            None,
            True,
            None,
            marks=pytest.mark.features_on('use_new_strongbox_merging_flow'),
            id='new_strongbox_merging_flow_to_github_testing',
        ),
        pytest.param(
            'GenerateStrongboxDiffProposal',
            {
                'service_id': 1,
                'project': 'taxi-devops',
                'tvm_name': 'some_tvm_name',
            },
            {
                'diff_proposal': {
                    'user': 'arcadia',
                    'repo': 'taxi/infra/strongbox-conf-stable',
                    'title': (
                        'feat clownductor: create strongbox secdist template'
                    ),
                    'changes': [
                        {
                            'filepath': 'secdist/clownductor.tpl',
                            'state': 'created_or_updated',
                            'data': EXPECTED_STRONGBOX_CHANGES_DATA,
                        },
                    ],
                    'base': 'trunk',
                    'comment': 'create Strongbox config',
                },
            },
            None,
            True,
            None,
            marks=pytest.mark.features_on(
                'use_new_strongbox_merging_flow', 'use_arcadia_strongbox_repo',
            ),
            id='new_strongbox_merging_flow_to_arcadia_stable',
        ),
        pytest.param(
            'GenerateStrongboxDiffProposal',
            {
                'service_id': 1,
                'project': 'taxi-devops',
                'tvm_name': 'some_tvm_name',
                'strongbox_env': 'unstable',
            },
            {
                'diff_proposal': {
                    'user': 'arcadia',
                    'repo': 'taxi/infra/strongbox-conf-unstable',
                    'title': (
                        'feat clownductor: create strongbox secdist template'
                    ),
                    'changes': [
                        {
                            'filepath': 'secdist/clownductor.tpl',
                            'state': 'created_or_updated',
                            'data': EXPECTED_STRONGBOX_CHANGES_DATA,
                        },
                    ],
                    'base': 'trunk',
                    'comment': 'create Strongbox config',
                },
            },
            None,
            True,
            None,
            marks=pytest.mark.features_on(
                'use_new_strongbox_merging_flow', 'use_arcadia_strongbox_repo',
            ),
            id='new_strongbox_merging_flow_to_arcadia_unstable',
        ),
        pytest.param(
            'GenerateStrongboxDiffProposal',
            {
                'service_id': 1,
                'project': 'taxi-devops',
                'tvm_name': 'old_tvm_name',
            },
            {},
            'strongbox-conf-stable/secdist/clownductor.tpl',
            True,
            None,
            marks=pytest.mark.features_on('use_new_strongbox_merging_flow'),
            id='tvm_of_the_service_already_exists_in_github',
        ),
        pytest.param(
            'GenerateStrongboxDiffProposal',
            {
                'service_id': 1,
                'project': 'taxi-devops',
                'tvm_name': 'old_tvm_name',
            },
            {},
            'taxi/infra/strongbox-conf-stable/secdist/clownductor.tpl',
            True,
            None,
            marks=pytest.mark.features_on(
                'use_new_strongbox_merging_flow', 'use_arcadia_strongbox_repo',
            ),
            id='tvm_of_the_service_already_exists_in_arcadia',
        ),
        pytest.param(
            'GenerateStrongboxDiffProposal',
            {
                'service_id': 1,
                'project': 'taxi-devops',
                'tvm_name': 'new_tvm_name',
            },
            {},
            'strongbox-conf-stable/secdist/clownductor.tpl',
            False,
            'Impossible to change existed tvm secret '
            'for taxi-devops-clownductor',
            marks=pytest.mark.features_on('use_new_strongbox_merging_flow'),
            id='strongbox_template_already_exists_in_github',
        ),
        pytest.param(
            'GenerateStrongboxDiffProposal',
            {
                'service_id': 1,
                'project': 'taxi-devops',
                'tvm_name': 'new_tvm_name',
            },
            {},
            'taxi/infra/strongbox-conf-stable/secdist/clownductor.tpl',
            False,
            'Impossible to change existed tvm secret '
            'for taxi-devops-clownductor',
            marks=pytest.mark.features_on(
                'use_new_strongbox_merging_flow', 'use_arcadia_strongbox_repo',
            ),
            id='strongbox_template_already_exists_in_arcadia',
        ),
        pytest.param(
            'GenerateDeleteStrongboxDiffProposal',
            {'service_id': 1, 'strongbox_env': 'testing'},
            {
                'diff_proposal': {
                    'user': 'arcadia',
                    'repo': 'taxi/infra/strongbox-conf-testing',
                    'base': 'trunk',
                    'title': (
                        'feat clownductor: delete strongbox secdist config'
                    ),
                    'comment': 'delete Strongbox config',
                    'changes': [
                        {
                            'filepath': 'secdist/clownductor.tpl',
                            'state': 'deleting',
                            'data': '',
                        },
                    ],
                },
                'new_service_ticket': 'TICKET-1',
            },
            'taxi/infra/strongbox-conf-stable/secdist/clownductor.tpl',
            True,
            None,
            marks=pytest.mark.features_on('delete_strongbox_from_arcadia'),
            id='delete_strongbox_template_from_arcadia_is_on',
        ),
        pytest.param(
            'GenerateDeleteStrongboxDiffProposal',
            {'service_id': 1},
            {'new_service_ticket': None},
            None,
            True,
            None,
            id='delete_strongbox_template_from_arcadia_is_off',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init.sql'])
async def test_merge_strongbox_diff_proposal_with_pr(
        mock_st_comments,
        load,
        patch_arc_read_file_with_path,
        patch_git_read_file_with_path,
        web_context,
        call_cube_handle,
        cube_name,
        input_data,
        expected_payload,
        file_path,
        is_success,
        error_message,
):
    patch_arc_read_file_with_path(path=file_path)
    patch_git_read_file_with_path(path=file_path)

    content_expected = {
        'payload': expected_payload,
        'status': 'success' if is_success else 'failed',
    }
    content_expected.update(
        {} if is_success else {'error_message': error_message},
    )

    await call_cube_handle(
        cube_name,
        {
            'data_request': {
                'input_data': input_data,
                'status': 'in_progress',
                'task_id': 1,
                'job_id': 1,
                'retries': 0,
            },
            'content_expected': content_expected,
        },
    )
