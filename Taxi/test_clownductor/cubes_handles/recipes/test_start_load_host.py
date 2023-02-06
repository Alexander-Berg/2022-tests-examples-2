AMMO_FILE = """147GET /ping HTTP/1.1
Host: qqbyrftajycoh7q2.vla.yp-c.yandex.net
User-Agent: tank
Accept: */*
Content-length: 7
Connection: keep-alive

{"a":1}"""


async def test_start_load_testing_recepie(
        sandbox_mockserver,
        task_processor,
        run_job_common,
        load_yaml,
        load_json,
):
    sandbox_mock = sandbox_mockserver()

    recipe = task_processor.load_recipe(
        load_yaml('recipes/LoadHost.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'ammo_file': AMMO_FILE,
            'ammo_description': 'test_ammo_description',
            'target_address': 'qqbyrftajycoh7q2.vla.yp-c.yandex.net',
            'schedule': 'line(1,2,3)',
            'operator_name': 'dyusudakov',
            'st_task': 'TAXICOMMON-123',
            'fire_title': 'auto-fire',
            'fire_description': 'auto-fire empty description',
            'monitoring_config': '',
        },
        initiator='clownductor',
        idempotency_token='ony_one_job',
    )
    await run_job_common(job)
    assert job.job_vars == load_json('expected_job_vars.json')
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
