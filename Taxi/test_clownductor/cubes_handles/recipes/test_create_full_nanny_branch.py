import pytest


@pytest.fixture(name='assert_job_vars')
def _assert_job_vars(assert_job_variables):
    def _wrapper(job_vars, job_name, job_id):
        return assert_job_variables(
            job_vars, job_name, job_id, 'expected_job_vars.json',
        )

    return _wrapper


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.usefixtures(
    'mock_internal_tp',
    'mock_strongbox',
    'random_region',
    'create_branch_fixture',
    'cube_job_get_information_update',
    'create_file_change_proposal',
    'dashboards_mockserver',
)
@pytest.mark.features_on('give_root_access', 'use_dashboards_upload_graphs')
async def test_recipe_create_full_nanny_branch(
        task_processor,
        run_job_with_meta,
        mock_github,
        strongbox_get_groups,
        patch_github_single_file,
        st_create_comment,
        assert_job_vars,
):
    patch_github_single_file(
        'services/test_service/service.yaml', 'test_service.yaml',
    )
    mock_github()

    job = await task_processor.start_job(
        job_vars={
            'project_id': 1,
            'service_id': 1,
            'branch_id': 2,
            'needs_balancers': False,
            'user': 'elrusso',
            'is_uservices': False,
            'env': 'stable',
            'branch_name': 'stable',
            'st_ticket': 'ElRusso-008',
            'description': 'stable branch branch',
            'branch_params': {
                'cpu': 512,
                'ram': 4096,
                'root_size': 512,
                'instances': [1, 1, 1],
                'work_dir': 128,
                'volumes': [],
                'regions': ['sas', 'man', 'vla'],
                'root_bandwidth_guarantee_mb_per_sec': 2,
                'root_bandwidth_limit_mb_per_sec': 4,
                'network_bandwidth_guarantee_mb_per_sec': 0,
            },
            'nested': True,
            'create_unstable_entrypoint': False,
            'protocol': 'http',
            'fqdn_suffix': None,
            'pre_deploy_job_id': None,
        },
        name='CreateFullNannyBranch',
        initiator='clownductor',
        idempotency_token='clowny_token1',
    )
    await run_job_with_meta(job)

    for (service_name, job_id) in task_processor.jobs:
        job_vars = task_processor.job(job_id).job_vars
        assert_job_vars(job_vars, service_name, job_id)

    assert len(st_create_comment.calls) == 4
    assert strongbox_get_groups.times_called == 1
