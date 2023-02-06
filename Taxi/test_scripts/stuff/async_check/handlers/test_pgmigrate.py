import os

import pytest

from scripts.lib import db_utils
from scripts.stuff.async_check import handlers
from scripts.stuff.async_check import models
from test_scripts import helpers


def mk_script(**updates):
    return db_utils.Script(None, helpers.get_script_doc(updates))


@pytest.mark.enable_raw_arc_client
@pytest.mark.skipif(
    bool(os.environ.get('IS_TEAMCITY')),
    reason=(
        'even "init --bare" requires authorisation, '
        'so test MUST past locally but may (and will) '
        'fail on build agents'
    ),
)
async def test_run_from_stable_no_errors(
        init_arc, set_pgmigrate_root_dir, scripts_tasks_app,
):
    arc_writer, arc_mock = init_arc
    arc_writer('V1__init.sql', 'SELECT 1;')

    check_result = models.CheckResult(None, [], [])
    with set_pgmigrate_root_dir(arc_mock.root_dir):
        await handlers.check_pgmigrate(
            scripts_tasks_app,
            mk_script(
                arguments=[
                    '--service_name',
                    'taxi_api_admin',
                    '--db_name',
                    'api_admin',
                    '--repository',
                    'taxi/backend-py3',
                ],
            ),
            check_result,
        )
    assert check_result.failure is None
    assert not check_result.warn_messages
    assert not check_result.error_messages


@pytest.mark.enable_raw_arc_client
@pytest.mark.skipif(
    bool(os.environ.get('IS_TEAMCITY')),
    reason=(
        'even "init --bare" requires authorisation, '
        'so test MUST past locally but may (and will) '
        'fail on build agents'
    ),
)
async def test_run_from_revision_no_errors(
        scripts_tasks_app, set_pgmigrate_root_dir, init_arc,
):
    arc_writer, arc_mock = init_arc
    arc_writer('V1__init.sql', 'SELECT 1;')

    arc_mock.make_branch('r1234')
    arc_mock.checkout()

    check_result = models.CheckResult(None, [], [])
    with set_pgmigrate_root_dir(arc_mock.root_dir):
        await handlers.check_pgmigrate(
            scripts_tasks_app,
            mk_script(
                arguments=[
                    '--service_name',
                    'taxi_api_admin',
                    '--db_name',
                    'api_admin',
                    '--repository',
                    'taxi/backend-py3',
                    '--branch',
                    'r1234',
                ],
            ),
            check_result,
        )
    assert check_result.failure is None
    assert not check_result.warn_messages
    assert not check_result.error_messages


@pytest.mark.enable_raw_arc_client
@pytest.mark.skipif(
    bool(os.environ.get('IS_TEAMCITY')),
    reason=(
        'even "init --bare" requires authorisation, '
        'so test MUST past locally but may (and will) '
        'fail on build agents'
    ),
)
async def test_run_from_revision_error_for_bad_revision(
        scripts_tasks_app, set_pgmigrate_root_dir, init_arc,
):
    _, arc_mock = init_arc

    check_result = models.CheckResult(None, [], [])
    with pytest.raises(handlers.Break), set_pgmigrate_root_dir(
            arc_mock.root_dir,
    ):
        await handlers.check_pgmigrate(
            scripts_tasks_app,
            mk_script(
                arguments=[
                    '--service_name',
                    'taxi_api_admin',
                    '--db_name',
                    'api_admin',
                    '--repository',
                    'taxi/backend-py3',
                    '--branch',
                    'r1234',
                ],
            ),
            check_result,
        )
    assert check_result.failure == models.FailReason(
        code='BAD_BRANCH',
        message='cannot fetch branch None, branch/commit \'r1234\'',
    )
    assert check_result.error_messages == [
        'cannot fetch branch None, branch/commit \'r1234\'',
    ]
    assert not check_result.warn_messages


@pytest.mark.enable_raw_arc_client
@pytest.mark.skipif(
    bool(os.environ.get('IS_TEAMCITY')),
    reason=(
        'even "init --bare" requires authorisation, '
        'so test MUST past locally but may (and will) '
        'fail on build agents'
    ),
)
async def test_warnings_from_sql_linters(
        scripts_tasks_app, set_pgmigrate_root_dir, init_arc,
):
    arc_writer, arc_mock = init_arc
    arc_writer('V1__init.sql', 'SELECT *;')

    check_result = models.CheckResult(None, [], [])
    with set_pgmigrate_root_dir(arc_mock.root_dir):
        await handlers.check_pgmigrate(
            scripts_tasks_app,
            mk_script(
                arguments=[
                    '--service_name',
                    'taxi_api_admin',
                    '--db_name',
                    'api_admin',
                    '--repository',
                    'taxi/backend-py3',
                ],
            ),
            check_result,
        )
    assert check_result.failure is None
    assert not check_result.error_messages

    star_usage_message = (
        'sql-linter: '
        './migrations/V1__init.sql: '
        'Do not use SELECT * in the root query, '
        'it will break on the next column removal/addition.'
    )
    assert check_result.warn_messages == [star_usage_message]


async def test_sql_linters(load, tmp_path):
    for filename in [
            'no-errors.sql',
            'non-concurrent-index-error.sql',
            'order-by-int-error.sql',
            'several-errors.sql',
            'star-usage-error.sql',
            'timestamp-wo-tz-usage-error.sql',
    ]:
        (tmp_path / filename).write_text(load(filename))
    # pylint: disable=protected-access
    result = await handlers._run_sql_linters(tmp_path)
    assert sorted(result) == [
        (
            './non-concurrent-index-error.sql: '
            'CREATE/DROP INDEX without CONCURENTLY might lock the whole table.'
        ),
        (
            './order-by-int-error.sql: '
            'Do not use ORDER BY with integer arguments '
            '(output column number), it is error-prone.'
        ),
        (
            './several-errors.sql: '
            'CREATE/DROP INDEX without CONCURENTLY might lock the whole table.'
        ),
        (
            './several-errors.sql: '
            'Do not use ORDER BY with integer arguments '
            '(output column number), it is error-prone.'
        ),
        (
            './several-errors.sql: '
            'Do not use SELECT * in the root query, '
            'it will break on the next column removal/addition.'
        ),
        (
            './several-errors.sql: '
            'Do not use TIMESTAMP WITHOUT TIME ZONE, '
            'see more at https://nda.ya.ru/t/25um2WA353SFcw'
        ),
        (
            './star-usage-error.sql: '
            'Do not use SELECT * in the root query, '
            'it will break on the next column removal/addition.'
        ),
        (
            './timestamp-wo-tz-usage-error.sql: '
            'Do not use TIMESTAMP WITHOUT TIME ZONE, '
            'see more at https://nda.ya.ru/t/25um2WA353SFcw'
        ),
    ]
