import pytest

from clownductor.internal.tasks import cubes


def task_data(name):
    return {
        'id': 123,
        'job_id': 456,
        'task_id': 789,
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


async def test_load_create_tank_config_cube(
        sandbox_mockserver, call_cube_handle,
):
    sandbox_mock = sandbox_mockserver()

    await call_cube_handle(
        'LoadCreateTankConfigCube',
        {
            'content_expected': {
                'status': 'success',
                'payload': {
                    'tank_config': sandbox_mock['test_data'][
                        'full_tank_config'
                    ],
                },
            },
            'data_request': {
                **task_data('LoadCreateTankConfigCube'),
                'input_data': {
                    'target_address': 'qqbyrftajycoh7q2.vla.yp-c.yandex.net',
                    'ammo_link': sandbox_mock['test_data']['ammo_link'],
                    'schedule': 'line(1,2,3)',
                    'operator_name': 'dyusudakov',
                    'st_task': 'TAXICOMMON-123',
                    'title': 'custom-title',
                    'description': 'custom-description',
                },
            },
        },
    )

    await call_cube_handle(
        'LoadCreateTankConfigCube',
        {
            'content_expected': {
                'status': 'success',
                'payload': {
                    'tank_config': sandbox_mock['test_data']['tank_config'],
                },
            },
            'data_request': {
                **task_data('LoadCreateTankConfigCube'),
                'input_data': {
                    'ammo_link': sandbox_mock['test_data']['ammo_link'],
                    'target_address': 'qqbyrftajycoh7q2.vla.yp-c.yandex.net',
                    'schedule': 'line(1,2,3)',
                    'operator_name': 'dyusudakov',
                    'st_task': 'TAXICOMMON-123',
                },
            },
        },
    )


@pytest.mark.parametrize('task_status', ['SUCCESS', 'ERROR'])
async def test_load_get_lunapark_id_cube(
        call_cube_handle, sandbox_mockserver, task_status,
):
    sandbox_mock = sandbox_mockserver(task_status=task_status)
    content_expected = (
        {
            'status': 'success',
            'payload': {
                'lunapark_id': sandbox_mock['test_data']['lunapark_id'],
                'lunapark_message': sandbox_mock['test_data'][
                    'lunapark_message'
                ],
            },
        }
        if task_status == 'SUCCESS'
        else {
            'status': 'failed',
            'error_message': (
                'Can not start load. For more details '
                'https://sandbox.yandex-team.ru/task/1129082489/view'
            ),
        }
    )

    await call_cube_handle(
        'LoadGetLunaparkIdCube',
        {
            'content_expected': content_expected,
            'data_request': {
                **task_data('LoadGetLunaparkIdCube'),
                'input_data': {
                    'sandbox_id': sandbox_mock['test_data'][
                        'sandbox_fire_task_id'
                    ],
                },
            },
        },
    )

    assert sandbox_mock['check_fire_task_mock'].times_called == 1


async def test_load_get_sandbox_resource_link_cube(
        call_cube_handle, sandbox_mockserver,
):
    sandbox_mock = sandbox_mockserver(task_status='SUCCESS')

    await call_cube_handle(
        'LoadGetSandboxResourceLinkCube',
        {
            'content_expected': {
                'status': 'success',
                'payload': {
                    'ammo_link': sandbox_mock['test_data']['ammo_link'],
                },
            },
            'data_request': {
                **task_data('LoadGetSandboxResourceLinkCube'),
                'input_data': {
                    'sandbox_id': sandbox_mock['test_data'][
                        'sandbox_upload_task_id'
                    ],
                },
            },
        },
    )

    assert sandbox_mock['get_resource_mock'].times_called == 1


async def test_load_create_fire_task_cube(
        call_cube_handle, sandbox_mockserver,
):
    sandbox_mock = sandbox_mockserver()
    await call_cube_handle(
        'LoadCreateFireTaskCube',
        {
            'content_expected': {
                'status': 'success',
                'payload': {
                    'sandbox_fire_task_id': sandbox_mock['test_data'][
                        'sandbox_fire_task_id'
                    ],
                },
            },
            'data_request': {
                **task_data('LoadCreateFireTaskCube'),
                'input_data': {
                    'tank_config': sandbox_mock['test_data']['tank_config'],
                    'monitoring_config': '',
                    'operator': 'dyusudakov',
                },
            },
        },
    )

    assert sandbox_mock['create_task_mock'].times_called == 1


async def test_load_create_upload_ammo_task_cube(
        call_cube_handle, sandbox_mockserver,
):
    sandbox_mock = sandbox_mockserver()
    await call_cube_handle(
        'LoadCreateUploadAmmoTaskCube',
        {
            'content_expected': {
                'status': 'success',
                'payload': {
                    'sandbox_upload_ammo_task_id': sandbox_mock['test_data'][
                        'sandbox_upload_task_id'
                    ],
                },
            },
            'data_request': {
                **task_data('LoadCreateUploadAmmoTaskCube'),
                'input_data': {
                    'ammo_file': sandbox_mock['test_data']['ammo_file'],
                },
            },
        },
    )

    assert sandbox_mock['create_task_mock'].times_called == 1


@pytest.mark.parametrize('task_status', ['SUCCESS', 'ERROR'])
async def test_load_start_sandbox_task_cube(
        call_cube_handle, sandbox_mockserver, task_status,
):
    sandbox_mock = sandbox_mockserver(task_status=task_status)

    content_expected = dict()
    content_expected['status'] = (
        'success' if task_status == 'SUCCESS' else 'failed'
    )
    if task_status != 'SUCCESS':
        content_expected['error_message'] = 'Can not start task'

    await call_cube_handle(
        'LoadStartSandboxTaskCube',
        {
            'content_expected': content_expected,
            'data_request': {
                **task_data('LoadStartSandboxTaskCube'),
                'input_data': {
                    'sandbox_id': sandbox_mock['test_data'][
                        'sandbox_fire_task_id'
                    ],
                },
            },
        },
    )

    assert sandbox_mock['start_task_mock'].times_called == 1


@pytest.mark.parametrize(
    'task_status',
    [
        'ASSIGNED',
        'PREPARING',
        'EXECUTING',
        'FINISHING',
        'SUCCESS',
        'EXCEPTION',
    ],
)
async def test_load_wait_sandbox_task_cube(
        call_cube_handle, sandbox_mockserver, task_status,
):
    sandbox_mock = sandbox_mockserver(task_status=task_status)
    status = (
        'failed'
        if task_status == 'EXCEPTION'
        else 'success'
        if task_status == 'SUCCESS'
        else 'in_progress'
    )

    content_expected = dict()
    content_expected['status'] = status
    if status == 'failed':
        content_expected['error_message'] = 'Exception in task'
    elif status == 'in_progress':
        content_expected['sleep_duration'] = cubes.CUBES[
            'LoadWaitSandboxTaskCube'
        ].get_refresh_gap()

    await call_cube_handle(
        'LoadWaitSandboxTaskCube',
        {
            'content_expected': content_expected,
            'data_request': {
                **task_data('LoadWaitSandboxTaskCube'),
                'input_data': {
                    'sandbox_id': sandbox_mock['test_data'][
                        'sandbox_fire_task_id'
                    ],
                },
            },
        },
    )

    assert sandbox_mock['check_fire_task_mock'].times_called == 1


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.parametrize('branch_id', [1, 666])
async def test_load_get_target_address_cube(call_cube_handle, branch_id):
    content_expected = {}
    if branch_id == 1:
        content_expected = {
            'status': 'success',
            'payload': {
                'target_address': (
                    'taxi-userver-load-tank-1.vla.yp-c.yandex.net'
                ),
            },
        }
    elif branch_id == 666:
        content_expected = {
            'status': 'failed',
            'error_message': 'Branch with id 666 does not exists',
        }

    await call_cube_handle(
        'LoadGetTargetAddressCube',
        {
            'content_expected': content_expected,
            'data_request': {
                **task_data('LoadGetTargetAddressCube'),
                'input_data': {'branch_id': branch_id},
            },
        },
    )
