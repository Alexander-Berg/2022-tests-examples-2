import pytest


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.usefixtures(
    'mock_internal_tp',
    'strongbox_get_groups',
    'strongbox_get_secrets',
    'random_region',
    'create_file_change_proposal',
    'create_branch_fixture',
    'cube_job_get_information_update',
)
async def test_recipe_prepare_relocation_service(
        load_yaml,
        task_processor,
        tvm_info_mockserver,
        yav_mockserver,
        abk_configs_mockserver,
        run_job_with_meta,
        abc_nonofficial_mockserver,
        mock_github,
        patch_github_single_file,
        abc_mockserver,
        add_external_cubes,
):
    mock_github()
    abc_mockserver(services=True)
    yav_mockserver()
    tvm_info_mockserver()
    abk_configs_mockserver()
    abc_nonofficial_mockserver()
    patch_github_single_file(
        'services/test_service/service.yaml', 'test_service_relocate.yaml',
    )
    add_external_cubes()
    task_processor.load_recipe(
        load_yaml('recipes/AbcCreateTvmResource.yaml')['data'],
    )

    job = await task_processor.start_job(
        job_vars={
            'service_id': 1,
            'project': 'test_project',
            'service': 'test-service',
            'st_task': 'ELRUSO-QUEUE-1',
            'service_parent_slug': 'testprojecttestservice',
            'yp_quota': 'testprojecttestservice',
            'default_ops': ['yandex_distproducts_browserdev_mobile_taxi_mnt'],
            'default_developers': [],
            'default_managers': [],
            'superusers': ['elrusso'],
            'yt_topic': {
                'path': 'taxi/taxi-access-log',
                'permissions': ['WriteTopic'],
            },
            'abc_name': {
                'ru': 'test_project/test-service',
                'en': 'test_project/test-service',
            },
            'abc_description': {'ru': '', 'en': ''},
            'tvm_name': 'test-service',
            'override_testing_tvm_id': None,
            'override_stable_tvm_id': None,
            'relocation': True,
            'drive_types': [],
        },
        name='PrepareRelocationService',
        initiator='clownductor',
        idempotency_token='clowny_token1',
    )
    await run_job_with_meta(job)
    assert job.job_vars == {
        'service_id': 1,
        'project': 'test_project',
        'service': 'test-service',
        'st_task': 'ELRUSO-QUEUE-1',
        'service_parent_slug': 'testprojecttestservice',
        'default_ops': ['yandex_distproducts_browserdev_mobile_taxi_mnt'],
        'default_developers': [],
        'default_managers': [],
        'diff_proposal': None,
        'merge_diff_job_id': None,
        'superusers': ['elrusso'],
        'yt_topic': {
            'path': 'taxi/taxi-access-log',
            'permissions': ['WriteTopic'],
        },
        'artifact_name': 'taxi/test_service/$',
        'abc_name': {
            'ru': 'test_project/test-service',
            'en': 'test_project/test-service',
        },
        'abc_description': {'ru': '', 'en': ''},
        'tvm_name': 'test-service',
        'override_testing_tvm_id': None,
        'override_stable_tvm_id': None,
        'service_abc_full_name': {
            'en': 'test_project/test-service',
            'ru': 'test_project/test-service',
        },
        'yp_quota': 'testprojecttestservice',
        'service_abc_name': 'test_project/test-service',
        'service_abc_slug': 'testprojecttestservice',
        'service_prefix': 'taxi_test_service',
        'stable_tvm_id': '123456',
        'strongbox_prestable': 'production',
        'strongbox_stable': 'production',
        'strongbox_testing': 'testing',
        'strongbox_unstable': 'unstable',
        'testing_tvm_id': '123456',
        'testing_tvm_yav_id': 'sec-XXX',
        'relocation': True,
        'drive_types': [],
        'stable_tvm_resource_creation_job_id': 2,
        'testing_tvm_resource_creation_job_id': 3,
    }
