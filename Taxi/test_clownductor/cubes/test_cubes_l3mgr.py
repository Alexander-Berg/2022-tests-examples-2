from clownductor.internal.tasks import cubes


def task_data(name='name'):
    return {
        'id': 123,
        'job_id': 456,
        'name': name,
        'sleep_until': 0,
        'input_mapping': {},
        'output_mapping': {},
        'payload': {},
        'retries': 0,
        'status': 'in_progress',
        'error_message': None,
        'created_at': 0,
        'updated_at': 0,
    }


async def test_fetch_service(web_context, l3mgr_mockserver):
    l3mgr_mockserver()

    cube = cubes.CUBES['L3MGRFetchIpv6'](
        web_context, task_data(), {'l3mgrServiceId': '4123'}, [], None,
    )

    await cube.update()

    assert cube.success


async def test_disable_service(web_context, l3mgr_mockserver):
    l3mgr_mockserver()

    cube = cubes.CUBES['L3MGRDisableBalancer'](
        web_context, task_data(), {'l3mgrServiceId': '8780'}, [], None,
    )

    await cube.update()

    assert cube.success


async def test_service_status(web_context, l3mgr_mockserver):
    l3mgr_mockserver()

    cube = cubes.CUBES['L3MGRWaitForEmptyServiceActivation'](
        web_context,
        task_data(),
        {'l3mgrServiceId': '8780', 'config_id': 76220},
        [],
        None,
    )

    await cube.update()

    assert cube.success


async def test_hide_service(web_context, l3mgr_mockserver):
    l3mgr_mockserver()

    cube = cubes.CUBES['L3MGRHideService'](
        web_context, task_data(), {'l3mgrServiceId': '8780'}, [], None,
    )

    await cube.update()

    assert cube.success
