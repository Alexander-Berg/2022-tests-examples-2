import pytest


EXPECTED_YASM_CHANGES_DATA = """{%- set shards = {
 'clownductor-db': {'cid': 'clownductor-cluster', 'ns': 'taxi'},
 'api_over_data_metrics': {'cid': 'mdbc33dno610dqk4mrk1', 'ns': 'taxi.ns1'},
 'exists_db': {'cid': 'some_cluster', 'ns': 'taxi.ns2'},
 'exists_db2': {'cid': 'some_cluster', 'ns': 'taxi.ns3'}
}
%}
"""


@pytest.mark.parametrize(
    'cube_name, input_data, expected_payload',
    [
        pytest.param(
            'GenerateYasmDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'branch_name': 'stable',
                'cluster_id': 'clownductor-cluster',
                'db_name': 'clownductor-db',
            },
            {},
            id='old_yasm_merging_flow',
        ),
        pytest.param(
            'GenerateYasmDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'branch_name': 'stable',
                'cluster_id': 'clownductor-cluster',
                'db_name': 'clownductor-db',
            },
            {
                'diff_proposal': {
                    'user': 'taxi',
                    'repo': 'infra-cfg-yasm',
                    'title': (
                        'feat clownductor: create YASM config '
                        'for db clownductor-db in '
                        'cluster clownductor-cluster'
                    ),
                    'changes': [
                        {
                            'filepath': 'configs/postgres.yml',
                            'state': 'created_or_updated',
                            'data': EXPECTED_YASM_CHANGES_DATA,
                        },
                    ],
                    'base': 'master',
                    'comment': 'create YASM config',
                },
            },
            marks=pytest.mark.features_on('use_new_yasm_merging_flow'),
            id='new_yasm_merging_flow_to_github',
        ),
        pytest.param(
            'GenerateYasmDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'branch_name': 'stable',
                'cluster_id': 'clownductor-cluster',
                'db_name': 'clownductor-db',
            },
            {
                'diff_proposal': {
                    'user': 'arcadia',
                    'repo': 'taxi/infra/infra-cfg-yasm',
                    'title': (
                        'feat clownductor: create YASM config '
                        'for db clownductor-db in '
                        'cluster clownductor-cluster'
                    ),
                    'changes': [
                        {
                            'filepath': 'configs/postgres.yml',
                            'state': 'created_or_updated',
                            'data': EXPECTED_YASM_CHANGES_DATA,
                        },
                    ],
                    'base': 'trunk',
                    'comment': 'create YASM config',
                },
            },
            marks=pytest.mark.features_on(
                'use_new_yasm_merging_flow', 'use_arcadia_yasm_repo',
            ),
            id='new_yasm_merging_flow_to_arcadia',
        ),
        pytest.param(
            'GenerateYasmDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'branch_name': 'stable',
                'cluster_id': 'some_cluster',
                'db_name': 'exists_db',
            },
            {},
            marks=pytest.mark.features_on(
                'use_new_yasm_merging_flow', 'use_arcadia_yasm_repo',
            ),
            id='config_already_exists_in_arcadia',
        ),
        pytest.param(
            'GenerateYasmDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'branch_name': 'stable',
                'cluster_id': 'some_cluster',
                'db_name': 'exists_db',
            },
            {},
            marks=pytest.mark.features_on('use_new_yasm_merging_flow'),
            id='config_already_exists_in_github',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init.sql'])
async def test_merge_yasm_diff_proposal_with_pr(
        patch_arc_read_file,
        patch_github_single_file,
        call_cube_handle,
        cube_name,
        input_data,
        expected_payload,
):
    patch_arc_read_file(
        path='taxi/infra/infra-cfg-yasm/configs/postgres.config',
        filename='postgres.config',
    )
    patch_github_single_file(
        path='infra-cfg-yasm/configs/postgres.config',
        filename='postgres.config',
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
            'content_expected': {
                'payload': expected_payload,
                'status': 'success',
            },
        },
    )
