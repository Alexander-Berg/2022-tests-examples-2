import pytest


AMMO_FILE = """147GET /ping HTTP/1.1
Host: qqbyrftajycoh7q2.vla.yp-c.yandex.net
User-Agent: tank
Accept: */*
Content-length: 7
Connection: keep-alive

{"a":1}"""


@pytest.mark.features_on('give_root_access')
@pytest.mark.config(CLOWNDUCTOR_FEATURES={'update_hosts_cube_enabled': True})
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_create_env_and_load_host_recipe(
        task_processor,
        mock_internal_tp,
        sandbox_mockserver,
        mock_clowny_balancer,
        strongbox_get_groups,
        create_branch_fixture,
        st_create_comment,
        st_get_ticket,
        random_region,
        cube_job_get_information_update,
        run_job_with_meta,
        load_yaml,
        monkeypatch,
        patch,
        assert_job_variables,
):
    @patch('clownductor.internal.tasks.manager._create_job')
    async def _create_job(context, job_data, variables, recipe, conn):
        job = await task_processor.start_job(
            name=job_data['name'],
            job_vars=variables,
            initiator=job_data['initiator'],
            idempotency_token=job_data['idempotency_token'],
            change_doc_id=job_data['change_doc_id'],
        )
        return job.id

    @patch('clownductor.internal.tasks.manager.get_jobs')
    async def _get_jobs(context, db_conn, job_ids):
        jobs = task_processor.find_jobs(job_ids)
        return [job.to_api() for job in jobs]

    sandbox_mock = sandbox_mockserver()

    @mock_clowny_balancer('/balancers/v1/service/get/')
    def _balancers_service_get(request):
        return {'namespaces': []}

    recipe = task_processor.load_recipe(
        load_yaml('recipes/CreateEnvAndLoadHost.yaml')['data'],
    )
    task_processor.load_recipe(load_yaml('recipes/LoadHost.yaml')['data'])

    job = await recipe.make_job(
        job_vars={
            'service_id': 1,
            'project_id': 1,
            'operator_name': 'dyusudakov',
            'ammo_file': AMMO_FILE,
            'ammo_description': 'test_ammo_description',
            'schedule': 'line(1,2,3)',
            'st_task': 'TAXICOMMON-123',
            'fire_title': 'auto-fire',
            'fire_description': 'auto-fire empty description',
            'monitoring_config': '',
            'new_branch_name': 'tank',
            'copy_branch_name': 'testing',
            'new_branch_ram': 4096,
            'new_branch_cpu': 512,
            'new_branch_regions': ['sas', 'vla'],
        },
        initiator='clownductor',
        idempotency_token='one_job',
    )
    await run_job_with_meta(job, is_waiter=False)

    for (job_name, job_id), job in task_processor.jobs.items():
        assert_job_variables(
            job.job_vars, job_name, job_id, 'expected_job_vars.json',
        )

    # LoadHost recipe asserts :

    # Two tasks created
    assert sandbox_mock['create_task_mock'].times_called == 2
    # Two tasks started
    assert sandbox_mock['start_task_mock'].times_called == 2
    # Checked twice, while waiting and getting result
    assert sandbox_mock['check_fire_task_mock'].times_called == 2
    # One check for wait
    assert sandbox_mock['check_upload_task_mock'].times_called == 1
    # Get link from resources when it is ready
    assert sandbox_mock['get_resource_mock'].times_called == 1

    requests = sandbox_mock['requests']
    test_data = sandbox_mock['test_data']

    assert requests['create_task_mock'][0].json == {
        'requirements': {},
        'type': 'CREATE_TEXT_RESOURCE',
        'owner': 'ROBOT_TAXI_SANDLOAD',
        'description': 'test_ammo_description',
        'custom_fields': [
            {'name': 'resource_type', 'value': 'AMMO_FILE'},
            {'name': 'resource_arch', 'value': 'any'},
            {'name': 'created_resource_name', 'value': 'auto-uploaded-ammo'},
            {'name': 'resource_file_content', 'value': AMMO_FILE},
            {'name': 'store_forever', 'value': False},
            {'name': 'resource_attrs', 'value': ''},
        ],
    }

    assert requests['start_task_mock'][0].json == {
        'id': [test_data['sandbox_upload_task_id']],
    }

    assert not requests['check_upload_task_mock'][0].get_data()

    assert dict(requests['get_resource_mock'][0].query) == {
        'limit': '1',
        'type': 'AMMO_FILE',
        'state': 'READY',
        'task_id': str(test_data['sandbox_upload_task_id']),
    }

    assert requests['create_task_mock'][1].json == {
        'requirements': {},
        'type': 'FIRESTARTER',
        'owner': 'ROBOT_TAXI_SANDLOAD',
        'custom_fields': [
            {'name': 'dry_run', 'value': False},
            {'name': 'tank_config', 'value': test_data['tank_config']},
            {'name': 'monitoring_config', 'value': ''},
            {'name': 'use_last_binary', 'value': True},
        ],
    }

    assert requests['start_task_mock'][1].json == {
        'id': [test_data['sandbox_fire_task_id']],
    }

    assert not requests['check_fire_task_mock'][0].get_data()

    assert not requests['check_fire_task_mock'][1].get_data()
