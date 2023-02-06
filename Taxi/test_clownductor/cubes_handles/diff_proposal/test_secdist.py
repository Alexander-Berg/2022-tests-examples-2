import pytest


EXPECTED_SECDIST_CHANGES_DATA = """{
    "postgresql_settings": {
        "databases": {
            {{ POSTGRES_TAXI_DEVOPS_CLOWNDUCTOR }}
        }
    },
    "settings_override": {
        "TVM_SERVICES": {
            "old_tvm_name": {{ TVM_TAXI_DEVOPS_OLD_TVM_NAME }}
        },
}
"""


@pytest.mark.parametrize(
    'cube_name, input_data, expected_payload, file_path',
    [
        pytest.param(
            'GenerateSecdistDiffProposal',
            {'service_id': 1, 'project_id': 1, 'skip_db': False},
            {},
            None,
            id='old_secdist_merging_flow',
        ),
        pytest.param(
            'GenerateSecdistDiffProposal',
            {'service_id': 1, 'project_id': 1, 'skip_db': False},
            {
                'diff_proposal': {
                    'user': 'taxi',
                    'repo': 'strongbox-conf-stable',
                    'title': 'feat clownductor: create secdist template',
                    'changes': [
                        {
                            'filepath': 'secdist/clownductor.tpl',
                            'state': 'created_or_updated',
                            'data': EXPECTED_SECDIST_CHANGES_DATA,
                        },
                    ],
                    'base': 'master',
                    'comment': (
                        'create secdist template and '
                        'append to strongbox config'
                    ),
                },
            },
            'strongbox-conf-stable/secdist/clownductor.tpl',
            marks=pytest.mark.features_on('use_new_secdist_merging_flow'),
            id='new_secdist_merging_flow_to_github',
        ),
        pytest.param(
            'GenerateSecdistDiffProposal',
            {'service_id': 1, 'project_id': 1, 'skip_db': False},
            {
                'diff_proposal': {
                    'user': 'arcadia',
                    'repo': 'taxi/infra/strongbox-conf-stable',
                    'title': 'feat clownductor: create secdist template',
                    'changes': [
                        {
                            'filepath': 'secdist/clownductor.tpl',
                            'state': 'created_or_updated',
                            'data': EXPECTED_SECDIST_CHANGES_DATA,
                        },
                    ],
                    'base': 'trunk',
                    'comment': (
                        'create secdist template and '
                        'append to strongbox config'
                    ),
                },
            },
            'taxi/infra/strongbox-conf-stable/secdist/clownductor.tpl',
            marks=pytest.mark.features_on(
                'use_new_secdist_merging_flow', 'use_arcadia_secdist_repo',
            ),
            id='new_secdist_merging_flow_to_arcadia',
        ),
        pytest.param(
            'GenerateSecdistDiffProposal',
            {'service_id': 2, 'project_id': 1, 'skip_db': False},
            {},
            'strongbox-conf-stable/secdist/dashboards.tpl',
            marks=pytest.mark.features_on('use_new_secdist_merging_flow'),
            id='pg_settings_already_exist_in_github',
        ),
        pytest.param(
            'GenerateSecdistDiffProposal',
            {'service_id': 2, 'project_id': 1, 'skip_db': False},
            {},
            'taxi/infra/strongbox-conf-stable/secdist/dashboards.tpl',
            marks=pytest.mark.features_on(
                'use_new_secdist_merging_flow', 'use_arcadia_secdist_repo',
            ),
            id='pg_settings_already_exist_in_arcadia',
        ),
        pytest.param(
            'GenerateSecdistDiffProposal',
            {
                'service_id': 1,
                'project_id': 1,
                'skip_db': False,
                'database': {'db_type': 'not_pgaas'},
            },
            {},
            'taxi/infra/strongbox-conf-stable/secdist/clownductor.tpl',
            marks=pytest.mark.features_on(
                'use_new_secdist_merging_flow', 'use_arcadia_secdist_repo',
            ),
            id='db_does_not_have_pgaas_type',
        ),
        pytest.param(
            'GenerateSecdistDiffProposal',
            {'service_id': 2, 'project_id': 1, 'skip_db': True},
            {},
            'taxi/infra/strongbox-conf-stable/secdist/dashboards.tpl',
            marks=pytest.mark.features_on(
                'use_new_secdist_merging_flow', 'use_arcadia_secdist_repo',
            ),
            id='skip_db_parameter_is_true',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init.sql'])
async def test_generate_secdist_diff_proposal(
        mockserver,
        patch_arc_read_file_with_path,
        patch_git_read_file_with_path,
        call_cube_handle,
        cube_name,
        input_data,
        expected_payload,
        file_path,
):
    @mockserver.json_handler('/strongbox/v1/templates/check/')
    async def _check_template(request):
        return {'is_valid': True}

    if file_path:
        if 'taxi' in file_path:
            patch_arc_read_file_with_path(path=file_path)
        else:
            patch_git_read_file_with_path(path=file_path)

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
            'content_expected': {
                'payload': expected_payload,
                'status': 'success',
            },
        },
    )
