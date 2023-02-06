import os
from typing import Optional

import pytest

from scripts.lib.models import async_check_queue as acq_models
from scripts.stuff.async_check import do_stuff


@pytest.fixture(name='test_task')
def _test_task(
        loop,
        scripts_tasks_app,
        setup_scripts,
        insert_many_acq_tasks,
        get_acq_task,
):
    async def _wrapper(
            script_id: str,
            script_extras: dict,
            is_failed: bool = False,
            task_error: Optional[dict] = None,
    ):
        script_updates = {'_id': script_id, **script_extras}

        await setup_scripts([script_updates])
        await insert_many_acq_tasks(acq_models.QueueItem.new(script_id))

        class StuffContext:
            id = 'id'  # pylint: disable=invalid-name
            data = scripts_tasks_app

        await do_stuff.do_stuff(StuffContext(), loop)

        task = await get_acq_task(script_id)
        if is_failed:
            assert task.status.is_failed
        else:
            assert task.status.is_success
        assert task.error_reason == task_error

        return task

    return _wrapper


async def test_python_script(test_task):
    await test_task('python-script', {})


@pytest.mark.enable_raw_arc_client
@pytest.mark.skipif(
    bool(os.environ.get('IS_TEAMCITY')),
    reason=(
        'even "init --bare" requires authorisation, '
        'so test MUST past locally but may (and will) '
        'fail on build agents'
    ),
)
async def test_pgmigrate_script(init_arc, set_pgmigrate_root_dir, test_task):
    arc_writer, arc_mock = init_arc
    arc_writer('V1__init.sql', 'SELECT 1;')

    with set_pgmigrate_root_dir(arc_mock.root_dir):
        await test_task(
            'pgmigrate-script',
            {
                'execute_type': 'pgmigrate',
                'arguments': [
                    '--service_name',
                    'taxi_api_admin',
                    '--db_name',
                    'api_admin',
                    '--repository',
                    'taxi/backend-py3',
                ],
            },
        )


@pytest.mark.enable_raw_arc_client
@pytest.mark.skipif(
    bool(os.environ.get('IS_TEAMCITY')),
    reason=(
        'even "init --bare" requires authorisation, '
        'so test MUST past locally but may (and will) '
        'fail on build agents'
    ),
)
async def test_pgmigrate_script_with_revision(
        init_arc, set_pgmigrate_root_dir, test_task,
):
    arc_writer, arc_mock = init_arc
    arc_writer('V1__init.sql', 'SELECT 1;')

    arc_mock.make_branch('r1234')
    arc_mock.checkout()

    with set_pgmigrate_root_dir(arc_mock.root_dir):
        await test_task(
            'pgmigrate-script',
            {
                'execute_type': 'pgmigrate',
                'arguments': [
                    '--service_name',
                    'taxi_api_admin',
                    '--db_name',
                    'api_admin',
                    '--repository',
                    'taxi/backend-py3',
                    '--branch',
                    'r1234',
                ],
            },
        )


@pytest.mark.enable_raw_arc_client
@pytest.mark.skipif(
    bool(os.environ.get('IS_TEAMCITY')),
    reason=(
        'even "init --bare" requires authorisation, '
        'so test MUST past locally but may (and will) '
        'fail on build agents'
    ),
)
async def test_pgmigrate_script_with_bad_revision(
        init_arc, set_pgmigrate_root_dir, test_task,
):
    _, arc_mock = init_arc
    with set_pgmigrate_root_dir(arc_mock.root_dir):
        await test_task(
            'pgmigrate-script',
            {
                'execute_type': 'pgmigrate',
                'arguments': [
                    '--service_name',
                    'taxi_api_admin',
                    '--db_name',
                    'api_admin',
                    '--repository',
                    'taxi/backend-py3',
                    '--branch',
                    'r1234',
                ],
            },
            is_failed=True,
            task_error={
                'code': 'BAD_BRANCH',
                'message': 'cannot fetch branch None, branch/commit \'r1234\'',
            },
        )


@pytest.mark.enable_raw_arc_client
@pytest.mark.skipif(
    bool(os.environ.get('IS_TEAMCITY')),
    reason=(
        'even "init --bare" requires authorisation, '
        'so test MUST past locally but may (and will) '
        'fail on build agents'
    ),
)
async def test_pgmigrate_migrations_directory_not_found(
        init_arc, set_pgmigrate_root_dir, test_task,
):
    _, arc_mock = init_arc
    migrations_dir = (
        'taxi/backend-py3/services/taxi_api_admin/postgresql/api_admin'
    )
    error_message = (
        f'migrations directory \'{migrations_dir}\' ' f'not found on \'trunk\''
    )
    with set_pgmigrate_root_dir(arc_mock.root_dir):
        task = await test_task(
            'pgmigrate-script',
            {
                'execute_type': 'pgmigrate',
                'arguments': [
                    '--service_name',
                    'taxi_api_admin',
                    '--db_name',
                    'api_admin',
                    '--repository',
                    'taxi/backend-py3',
                ],
            },
            is_failed=True,
            task_error={'code': 'DIR_NOT_FOUND', 'message': error_message},
        )
    assert task.error_messages == [error_message]


@pytest.mark.enable_raw_arc_client
@pytest.mark.skipif(
    bool(os.environ.get('IS_TEAMCITY')),
    reason=(
        'even "init --bare" requires authorisation, '
        'so test MUST past locally but may (and will) '
        'fail on build agents'
    ),
)
async def test_pgmigrate_for_linter_warnings(
        init_arc, set_pgmigrate_root_dir, test_task,
):
    arc_writer, arc_mock = init_arc
    arc_writer('V1__init.sql', 'SELECT *;')

    arc_mock.make_branch('r1234')
    arc_mock.checkout()

    with set_pgmigrate_root_dir(arc_mock.root_dir):
        task = await test_task(
            'pgmigrate-script',
            {
                'execute_type': 'pgmigrate',
                'arguments': [
                    '--service_name',
                    'taxi_api_admin',
                    '--db_name',
                    'api_admin',
                    '--repository',
                    'taxi/backend-py3',
                    '--branch',
                    'r1234',
                ],
            },
        )

    star_usage_message = (
        'sql-linter: '
        './migrations/V1__init.sql: '
        'Do not use SELECT * in the root query, '
        'it will break on the next column removal/addition.'
    )
    assert task.warn_messages == [star_usage_message]
