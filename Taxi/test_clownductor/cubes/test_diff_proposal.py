import pytest

from clownductor.internal.tasks import cubes

EXPECTED_CHANGES_DATA = (
    """
---
host: taxi_clownductor_stable
type: rtc
multichildren:
- taxi_clownductor_pre_stable
- taxi_clownductor_stable
templates:
- template: core-files
- template: forced-logrotate-count
- template: hejmdal-bad-rps
- template: hejmdal-cutres-draft-notify
- template: hejmdal-rtc-net-usage
- template: hejmdal-rtc-oom
- template: hejmdal-rtc-resource-usage
- template: hejmdal-timings
- template: hejmdal-rtc-timings-cpu-aggregation
- template: iptruler
- template: pilorama
- template: ping-handle-status
- template: push-client
- template: taxi_strongbox
- template: unispace
- template: vhost-499
- template: vhost-500
- template: virtual-meta
""".lstrip()
)

EXPECTED_MDB_CHANGES_DATA = (
    """
---
host: pg_taxi-devops_clownductor_stable
multichildren:
- db_nanny
templates:
- template: hejmdal-pg
""".lstrip()
)

EXPECTED_YASM_CHANGES_DATA = """{%- set shards = {
 'clownductor_db': {'cid': 'clownductor_cluster', 'ns': 'taxi'},
 'api_over_data_metrics': {'cid': 'mdbc33dno610dqk4mrk1', 'ns': 'taxi.ns1'},
 'exists_db': {'cid': 'some_cluster', 'ns': 'taxi.ns2'},
 'exists_db2': {'cid': 'some_cluster', 'ns': 'taxi.ns3'}
}
%}
"""

EXPECTED_STRONGBOX_CHANGES_DATA = """{
    "settings_override": {
        "TVM_SERVICES": {
            "some_tvm_name": {{ TVM_TAXI_DEVOPS_SOME_TVM_NAME }}
        }
    }
}
"""

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
    'cube_name, input_data, expected_payload',
    [
        pytest.param(
            'GenerateYasmDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'branch_name': 'stable',
                'cluster_id': 'clownductor_cluster',
                'db_name': 'clownductor_db',
            },
            {'diff_proposal': None},
            id='old_yasm_merging_flow',
        ),
        pytest.param(
            'GenerateYasmDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'branch_name': 'stable',
                'cluster_id': 'clownductor_cluster',
                'db_name': 'clownductor_db',
            },
            {
                'diff_proposal': {
                    'user': 'taxi',
                    'repo': 'infra-cfg-yasm',
                    'title': (
                        'feat clownductor: create YASM config for '
                        'db clownductor_db in '
                        'cluster clownductor_cluster'
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
                'cluster_id': 'clownductor_cluster',
                'db_name': 'clownductor_db',
            },
            {
                'diff_proposal': {
                    'user': 'arcadia',
                    'repo': 'taxi/infra/infra-cfg-yasm',
                    'title': (
                        'feat clownductor: create YASM config for '
                        'db clownductor_db in '
                        'cluster clownductor_cluster'
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
            {'diff_proposal': None},
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
            {'diff_proposal': None},
            marks=pytest.mark.features_on('use_new_yasm_merging_flow'),
            id='config_already_exists_in_github',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init.sql'])
async def test_generate_yasm_diff_proposal(
        load,
        patch_arc_read_file,
        patch_github_single_file,
        web_context,
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

    cube = cubes.CUBES[cube_name](
        web_context,
        {
            'id': 1,
            'job_id': 1,
            'sleep_until': 0,
            'input_mapping': {},
            'retries': 0,
            'status': 'in_progress',
        },
        input_data,
        [],
        None,
    )

    await cube.update()
    assert cube.success
    assert cube.data['payload'] == expected_payload


@pytest.fixture(name='mock_st_comments')
def _mock_st_comments(mockserver):
    @mockserver.json_handler('/startrek/issues/TICKET-1/comments')
    @mockserver.json_handler('/startrek/issues/TICKET-2/comments')
    def _comments(request):
        return {}


@pytest.mark.parametrize(
    'cube_name, input_data, expected_payload, file_path',
    [
        pytest.param(
            'GenerateSecdistDiffProposal',
            {'service_id': 1, 'project_id': 1, 'skip_db': False},
            {'diff_proposal': None},
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
            {'diff_proposal': None},
            'strongbox-conf-stable/secdist/dashboards.tpl',
            marks=pytest.mark.features_on('use_new_secdist_merging_flow'),
            id='pg_settings_already_exist_in_github',
        ),
        pytest.param(
            'GenerateSecdistDiffProposal',
            {'service_id': 2, 'project_id': 1, 'skip_db': False},
            {'diff_proposal': None},
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
            {'diff_proposal': None},
            'taxi/infra/strongbox-conf-stable/secdist/clownductor.tpl',
            marks=pytest.mark.features_on(
                'use_new_secdist_merging_flow', 'use_arcadia_secdist_repo',
            ),
            id='db_does_not_have_pgaas_type',
        ),
        pytest.param(
            'GenerateSecdistDiffProposal',
            {'service_id': 2, 'project_id': 1, 'skip_db': True},
            {'diff_proposal': None},
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
        load,
        patch_arc_read_file_with_path,
        patch_git_read_file_with_path,
        web_context,
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

    cube = cubes.CUBES[cube_name](
        web_context,
        {
            'id': 1,
            'job_id': 1,
            'sleep_until': 0,
            'input_mapping': {},
            'retries': 0,
            'status': 'in_progress',
        },
        input_data,
        [],
        None,
    )

    await cube.update()
    assert cube.success
    assert cube.data['payload'] == expected_payload
