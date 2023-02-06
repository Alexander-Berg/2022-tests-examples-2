import pytest


@pytest.mark.features_on(
    'on_change_service_yaml', 'use_dashboards_upload_graphs',
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.config(
    CLOWNDUCTOR_STARTREK_CLOSE_ACTIONS={
        'TAXIREL': {
            'open': 'closed',
            'readyForRelease': 'close',
            'testing': 'closed',
        },
    },
    CLOWNDUCTOR_MAP_PROJECTS_BY_QOUTA_PARAMS={
        'test_project': {
            'use_single_abc_on_db': True,
            'use_single_abc_on_db_in_job': True,
        },
        '__default__': {
            'use_single_abc_on_db': False,
            'use_single_abc_on_db_in_job': False,
        },
    },
)
@pytest.mark.usefixtures(
    'mock_internal_tp',
    'strongbox_get_secrets',
    'github_merge_pull',
    'create_files_and_push_to_branch',
    'create_file_change_proposal',
    'create_branch_fixture',
    'cube_job_get_information_update',
    'dashboards_mockserver',
)
async def test_recipe_relocate_service_to_nanny(
        load_yaml,
        task_processor,
        tvm_info_mockserver,
        yav_mockserver,
        strongbox_get_groups,
        abk_configs_mockserver,
        run_job_with_meta,
        abc_nonofficial_mockserver,
        github_get_pull,
        mock_github,
        github_create_service_fixture,
        st_get_myself,
        st_create_ticket,
        st_get_comments,
        st_create_comment,
        st_get_ticket,
        patch_github_single_file,
        abc_mockserver,
        add_external_cubes,
):
    mock_github()
    yav_mockserver()
    tvm_info_mockserver()
    abk_configs_mockserver()
    abc_nonofficial_mockserver()
    abc_mockserver(services=True)
    patch_github_single_file(
        'services/test_service/service.yaml', 'test_service.yaml',
    )
    add_external_cubes()
    task_processor.load_recipe(
        load_yaml('recipes/AbcCreateTvmResource.yaml')['data'],
    )

    job = await task_processor.start_job(
        job_vars={
            'service_id': 1,
            'project_id': 1,
            'needs_unstable': False,
            'needs_balancers': False,
            'user': 'elrusso',
            'is_uservices': False,
            'service_yaml': {
                'service_type': 'backendpy3',
                'service_yaml_url': (
                    'https://github.yandex-team.ru/taxi/backend-py3/blob/'
                    'develop/services/test_service/service.yaml'
                ),
                'service_name': 'order-notify',
                'wiki_path': (
                    'https://wiki.yandex-team.ru/taxi/backend/'
                    'architecture/order-notify/'
                ),
                'maintainers': ['Evgeny Usov <e-usov@yandex-team.ru>'],
                'service_info': {
                    'name': 'order-notify',
                    'clownductor_project': 'test_project',
                    'preset': {'name': 'x2micro'},
                    'disk_profile': 'default',
                    'abc': None,
                    'description': 'ttt',
                    'design_review': (
                        'https://st.yandex-team.ru/TAXIARCHREVIEW-680'
                    ),
                    'grafana': None,
                    'robots': None,
                    'deploy_callback_url': None,
                    'duty_group_id': '5f6b5a8c8ef826475e624740',
                    'release_flow': {'single_approve': True},
                    'units': [],
                    'has_unstable': False,
                    'has_balancers': False,
                    'yt_log_replications': None,
                    'networks': None,
                },
                'tvm_name': 'order-notify',
                'hostnames': None,
            },
            'draft_ticket': 'TAXIADMIN-88',
            'skip_db': True,
            'database': None,
            'relocation': True,
            'old_service_id': 10,
        },
        name='RelocateServiceToNanny',
        initiator='clownductor',
        idempotency_token='clowny_token1',
    )
    await run_job_with_meta(job)
    assert len(st_create_comment.calls) == 18
    assert len(st_get_myself.calls) == 1
    assert len(st_get_comments.calls) == 1
    assert strongbox_get_groups.times_called == 3
