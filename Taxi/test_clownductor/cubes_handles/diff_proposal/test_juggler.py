import pytest

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


@pytest.mark.parametrize(
    'cube_name, input_data, expected_payload',
    [
        pytest.param(
            'GenerateJugglerDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'branch_name': 'stable',
            },
            {},
            id='old_juggler_merging_flow',
        ),
        pytest.param(
            'GenerateJugglerDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'branch_name': 'stable',
            },
            {
                'diff_proposal': {
                    'user': 'taxi',
                    'repo': 'infra-cfg-juggler',
                    'base': 'master',
                    'title': 'feat clownductor: create Juggler config',
                    'comment': 'create Juggler config',
                    'changes': [
                        {
                            'filepath': (
                                'checks/rtc_taxi-devops_clownductor_stable'
                            ),
                            'data': EXPECTED_CHANGES_DATA,
                            'state': 'created_or_updated',
                        },
                    ],
                },
            },
            marks=pytest.mark.features_on('use_new_juggler_merging_flow'),
            id='new_juggler_merging_flow_to_github',
        ),
        pytest.param(
            'GenerateJugglerDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'branch_name': 'stable',
            },
            {
                'diff_proposal': {
                    'user': 'arcadia',
                    'repo': 'taxi/infra/infra-cfg-juggler',
                    'base': 'trunk',
                    'title': 'feat clownductor: create Juggler config',
                    'comment': 'create Juggler config',
                    'changes': [
                        {
                            'filepath': (
                                'checks/rtc_taxi-devops_clownductor_stable'
                            ),
                            'data': EXPECTED_CHANGES_DATA,
                            'state': 'created_or_updated',
                        },
                    ],
                },
            },
            marks=pytest.mark.features_on(
                'use_arcadia_juggler_repo', 'use_new_juggler_merging_flow',
            ),
            id='new_juggler_merging_flow_to_arcadia',
        ),
        pytest.param(
            'GenerateJugglerMdbDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'cluster_id': 'nanny',
            },
            {},
            id='old_juggler_mdb_merging_flow',
        ),
        pytest.param(
            'GenerateJugglerMdbDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'cluster_id': 'nanny',
            },
            {
                'diff_proposal': {
                    'user': 'taxi',
                    'repo': 'infra-cfg-juggler',
                    'base': 'master',
                    'title': 'feat clownductor: create Juggler config',
                    'comment': 'create Juggler config',
                    'changes': [
                        {
                            'filepath': (
                                'checks/pg_taxi-devops_clownductor_stable'
                            ),
                            'data': EXPECTED_MDB_CHANGES_DATA,
                            'state': 'created_or_updated',
                        },
                    ],
                },
            },
            marks=pytest.mark.features_on('use_new_juggler_merging_flow'),
            id='new_juggler_mdb_merging_flow_to_github',
        ),
        pytest.param(
            'GenerateJugglerMdbDiffProposal',
            {
                'project_name': 'taxi-devops',
                'service_name': 'clownductor',
                'env': 'stable',
                'cluster_id': 'nanny',
            },
            {
                'diff_proposal': {
                    'user': 'arcadia',
                    'repo': 'taxi/infra/infra-cfg-juggler',
                    'base': 'trunk',
                    'title': 'feat clownductor: create Juggler config',
                    'comment': 'create Juggler config',
                    'changes': [
                        {
                            'filepath': (
                                'checks/pg_taxi-devops_clownductor_stable'
                            ),
                            'data': EXPECTED_MDB_CHANGES_DATA,
                            'state': 'created_or_updated',
                        },
                    ],
                },
            },
            marks=pytest.mark.features_on(
                'use_arcadia_juggler_repo', 'use_new_juggler_merging_flow',
            ),
            id='new_juggler_mdb_merging_flow_to_arcadia',
        ),
        pytest.param(
            'GenerateDeleteJugglerDiffProposal',
            {'branch_id': 2},
            {
                'diff_proposal': {
                    'user': 'arcadia',
                    'repo': 'taxi/infra/infra-cfg-juggler',
                    'base': 'trunk',
                    'title': 'feat clownductor: delete Juggler config',
                    'comment': 'delete Juggler config',
                    'changes': [
                        {
                            'filepath': (
                                'checks/rtc_taxi-devops_clownductor_stable'
                            ),
                            'state': 'deleting',
                            'data': '',
                        },
                    ],
                },
                'new_service_ticket': 'TICKET-1',
            },
            id='delete_juggler_from_arcadia_is_on',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init.sql'])
async def test_juggler_merge_diff_proposal_with_pr(
        patch_arc_read_file,
        patch_github_single_file,
        call_cube_handle,
        cube_name,
        input_data,
        expected_payload,
):
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
