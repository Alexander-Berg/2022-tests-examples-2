import pytest

from scripts.lib.models import async_check_queue as acq_models
from scripts.lib.models import common


@pytest.fixture(name='init_scripts')
async def _init_scripts(setup_scripts):
    await setup_scripts(
        [
            {'_id': 'check-not-started'},
            {'_id': 'check-is-in-progress'},
            {'_id': 'check-completed'},
            {'_id': 'check-failed'},
        ],
    )


@pytest.fixture(name='init_check_queue_items')
async def _init_check_queue_items(insert_many_acq_tasks):
    await insert_many_acq_tasks(
        acq_models.QueueItem.new('check-is-in-progress'),
        acq_models.QueueItem.new(
            'check-completed', status=common.Status.success,
        ),
        acq_models.QueueItem.new(
            'check-failed',
            status=common.Status.failed,
            error_reason={
                'code': 'SOME_FAIL',
                'message': 'check failed just cause',
            },
        ),
    )


@pytest.fixture(name='test_handler')
def _test_handler(scripts_client):
    async def _wrapper(script_id: str, response_code: int, check_data: dict):
        response = await scripts_client.post(
            '/scripts/create/check/', json={'script_id': script_id},
        )
        assert response.status == response_code
        data = await response.json()
        assert data == check_data

    return _wrapper


@pytest.mark.usefixtures('init_scripts', 'init_check_queue_items')
@pytest.mark.config(
    SCRIPTS_ASYNC_CHECKS_SWITCHER=[
        {'value': True, 'service': '__ANY__', 'execute_type': '__ANY__'},
    ],
)
async def test_missing_script(test_handler):
    await test_handler(
        'non-exists',
        404,
        {
            'code': 'not_found',
            'message': 'Script with id \'non-exists\' not found',
            'status': 'error',
        },
    )


@pytest.mark.usefixtures('init_scripts', 'init_check_queue_items')
@pytest.mark.config(
    SCRIPTS_ASYNC_CHECKS_SWITCHER=[
        {'value': True, 'service': '__ANY__', 'execute_type': '__ANY__'},
    ],
)
async def test_new_check_created(get_acq_task, test_handler):
    await test_handler(
        'check-not-started',
        200,
        {
            'status': 'processing',
            'change_doc_id': 'scripts_check-not-started',
            'data': {'script_id': 'check-not-started'},
        },
    )
    task = await get_acq_task('check-not-started')
    assert task.script_id == 'check-not-started'
    assert task.status == common.Status.pending


@pytest.mark.usefixtures('init_scripts', 'init_check_queue_items')
@pytest.mark.config(
    SCRIPTS_ASYNC_CHECKS_SWITCHER=[
        {'value': True, 'service': 'some-service', 'execute_type': '__ANY__'},
        {'value': False, 'service': '__ANY__', 'execute_type': '__ANY__'},
    ],
)
async def test_check_not_created_by_config(test_handler):
    await test_handler(
        'check-not-started',
        200,
        {
            'change_doc_id': 'scripts_check-not-started',
            'data': {'script_id': 'check-not-started'},
        },
    )


@pytest.mark.usefixtures('init_scripts', 'init_check_queue_items')
@pytest.mark.config(
    SCRIPTS_ASYNC_CHECKS_SWITCHER=[
        {'value': True, 'service': '__ANY__', 'execute_type': '__ANY__'},
    ],
    SCRIPTS_FEATURES_BY_PROJECT={
        '__default__': {'force_disable_async_check': True},
    },
)
async def test_check_not_created_by_feature(test_handler):
    await test_handler(
        'check-not-started',
        200,
        {
            'change_doc_id': 'scripts_check-not-started',
            'data': {'script_id': 'check-not-started'},
        },
    )


@pytest.mark.usefixtures('init_scripts', 'init_check_queue_items')
@pytest.mark.config(
    SCRIPTS_ASYNC_CHECKS_SWITCHER=[
        {'value': True, 'service': '__ANY__', 'execute_type': '__ANY__'},
    ],
)
async def test_chek_already_in_progress(test_handler):
    await test_handler(
        'check-is-in-progress',
        200,
        {
            'status': 'processing',
            'change_doc_id': 'scripts_check-is-in-progress',
            'data': {'script_id': 'check-is-in-progress'},
        },
    )


@pytest.mark.usefixtures('init_scripts', 'init_check_queue_items')
@pytest.mark.config(
    SCRIPTS_ASYNC_CHECKS_SWITCHER=[
        {'value': True, 'service': '__ANY__', 'execute_type': '__ANY__'},
    ],
)
async def test_check_failed(test_handler):
    await test_handler(
        'check-failed',
        400,
        {
            'code': 'SOME_FAIL',
            'message': 'check failed just cause',
            'status': 'error',
        },
    )
