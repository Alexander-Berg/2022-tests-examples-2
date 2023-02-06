# pylint: disable=protected-access,redefined-outer-name
import datetime
import os
from unittest import mock

import asynctest
import pytest

from taxi.clients import mds_s3
from taxi.scripts import db as scripts_db
from taxi.scripts import exceptions
from taxi.scripts import os as scripts_os
from taxi.scripts import settings
from tests.taxi import scripts


NON_RUNNING_STATUSES = scripts_db.ScriptStatus.ALL - {
    scripts_db.ScriptStatus.RUNNING,
}
NON_APPROVED_STATUSES = scripts_db.ScriptStatus.ALL - {
    scripts_db.ScriptStatus.APPROVED,
}


@pytest.yield_fixture(autouse=False)
async def setup_many_scripts(db):
    await db.scripts.insert_many(
        [
            scripts.get_script_doc(
                {
                    'status': scripts_db.ScriptStatus.APPROVED,
                    'run_manually': True,
                },
            ),
            scripts.get_script_doc(
                {
                    'status': scripts_db.ScriptStatus.RUNNING,
                    'started_running_at': datetime.datetime.utcnow(),
                    'fetch_lock_expires_at': (
                        datetime.datetime.utcnow()
                        + datetime.timedelta(minutes=5)
                    ),
                    'server_name': 'test-dev',
                },
            ),
            scripts.get_script_doc(
                {
                    'status': scripts_db.ScriptStatus.APPROVED,
                    'fetch_lock_expires_at': (
                        datetime.datetime.utcnow()
                        + datetime.timedelta(weeks=1)
                    ),
                },
            ),
            scripts.get_script_doc(
                {
                    '_id': '1',
                    'project': 'fake-project-1',
                    'status': scripts_db.ScriptStatus.APPROVED,
                    'fetch_lock_expires_at': (
                        datetime.datetime.utcnow()
                        - datetime.timedelta(minutes=1)
                    ),
                },
            ),
            scripts.get_script_doc(
                {
                    '_id': '2',
                    'project': 'fake-project-1',
                    'status': scripts_db.ScriptStatus.APPROVED,
                    'fetch_lock_expires_at': datetime.datetime.utcnow(),
                },
            ),
            scripts.get_script_doc(
                {
                    'project': 'fake-project-2',
                    'status': scripts_db.ScriptStatus.APPROVED,
                    'fetch_lock_expires_at': (
                        datetime.datetime.utcnow()
                        - datetime.timedelta(weeks=1)
                    ),
                },
            ),
        ],
    )

    yield

    await db.scripts.drop()


async def script_with_status(db, status, doc_update=None):
    if doc_update is None:
        doc_update = {}
    doc_update['status'] = status
    script_doc = scripts.get_script_doc(doc_update)

    script = scripts_db.Script(db.scripts, script_doc)
    await db.scripts.insert_one(script_doc)

    return script


@pytest.fixture
async def failed_script(db):
    return await script_with_status(db, scripts_db.ScriptStatus.FAILED)


@pytest.fixture
async def running_script(db):
    return await script_with_status(db, scripts_db.ScriptStatus.RUNNING)


@pytest.fixture
async def succeeded_script(db):
    return await script_with_status(db, scripts_db.ScriptStatus.SUCCEEDED)


@pytest.fixture
async def approved_script(db):
    return await script_with_status(db, scripts_db.ScriptStatus.APPROVED)


@pytest.fixture
async def outdated_script(db):
    script_doc = scripts.get_script_doc({'_id': '1'})
    script = scripts_db.Script(db.scripts, script_doc)

    await db.scripts.insert_one(
        scripts.get_script_doc({'_id': '1', 'version': '2'}),
    )

    return script


@pytest.fixture
def mongodb_collections():
    return ['scripts']


@pytest.mark.usefixtures('setup_many_scripts')
async def test_get_running_scripts_count(db, setup_many_scripts):
    assert await scripts_db.get_running_scripts_count(db, 'test-dev') == 1


@pytest.mark.usefixtures('setup_many_scripts')
async def test_get_next_script(db):
    with pytest.raises(exceptions.NotFound):
        await scripts_db.get_next_script(db, 'fake-project')

    script = await scripts_db.get_next_script(db, 'fake-project-1')
    assert script.primary_key == '1'

    # Shouldn't raise NotFound
    await scripts_db.get_next_script(db, 'fake-project-2')


async def test_script_force_fail(
        failed_script, succeeded_script, approved_script,
):
    with pytest.raises(exceptions.CantFail):
        await failed_script.force_fail('SHOULDN\'T FAIL')

    with pytest.raises(exceptions.CantFail):
        await succeeded_script.force_fail('SHOULDN\'T FAIL')

    fail_result = await approved_script.force_fail('FAIL')
    assert fail_result.status == scripts_db.ScriptStatus.FAILED
    assert fail_result.failed_reason == 'FAIL'


async def test_script_fail(db, running_script):
    for status in NON_RUNNING_STATUSES:
        script = await script_with_status(db, status)
        with pytest.raises(exceptions.CantFail):
            await script.fail('SHOULDN\'T FAIL', 1)

    fail_result = await running_script.fail('FAIL', 12)
    assert fail_result.status == scripts_db.ScriptStatus.FAILED
    assert fail_result.failed_reason == 'FAIL'
    assert fail_result.exit_code == 12
    assert fail_result.finished_at is not None


async def test_script_succeed(db, running_script):
    for status in NON_RUNNING_STATUSES:
        script = await script_with_status(db, status)
        with pytest.raises(exceptions.CantSucceed):
            await script.succeed(1)

    result = await running_script.succeed(2)
    assert result.status == scripts_db.ScriptStatus.SUCCEEDED
    assert result.exit_code == 2
    assert result.finished_at is not None


async def test_script_start_running(db, approved_script):
    for status in NON_APPROVED_STATUSES:
        script = await script_with_status(db, status)
        with pytest.raises(exceptions.CantStartRunning):
            await script.start_running('server')

    result = await approved_script.start_running('non_existent_server')
    assert result.status == scripts_db.ScriptStatus.RUNNING
    assert result.server_name == 'non_existent_server'
    assert result.started_running_at is not None


async def test_script_acquire_fetch_lock(db, approved_script):
    for status in NON_APPROVED_STATUSES:
        script = await script_with_status(db, status)
        with pytest.raises(exceptions.CantLock):
            await script.acquire_fetch_lock(1)

    lock_duration = 10

    result = await approved_script.acquire_fetch_lock(lock_duration)
    assert (
        result.fetch_lock_expires_at - result.updated
    ).seconds == lock_duration


async def test_script_release_fetch_lock(db):
    fetch_lock_doc = {'fetch_lock_expires_at': datetime.datetime.utcnow()}

    for status in scripts_db.ScriptStatus.ALL:
        script = await script_with_status(db, status, fetch_lock_doc)
        result = await script.release_fetch_lock()
        assert result.fetch_lock_expires_at is None


@pytest.mark.mongodb_collections('script_logs')
async def test_save_script(db, tmpdir):
    working_area = tmpdir.mkdir('working_area')

    script = await script_with_status(
        db, scripts_db.ScriptStatus.SUCCEEDED, {},
    )
    config = mock.MagicMock(LOG_UPLOAD_CHUNK_SIZE=1)

    s3_client_mock = asynctest.MagicMock(
        mds_s3.MdsS3Client, s3_settings=settings.ADMIN_SCRIPT_LOGS_MDS_S3,
    )

    log_data = {
        'stdout': b'a' * (settings.MAX_MONGO_TEXT_SIZE * 2),
        'stderr': b'a',
        'raw_stdout': b'b' * (settings.MAX_MONGO_TEXT_SIZE + 1),
        'raw_stderr': b'b',
    }

    with mock.patch('taxi.scripts.settings.WORKING_AREA_DIR', working_area):
        for log_type, log_type_data in log_data.items():
            log_path = getattr(scripts_os, f'get_{log_type}_path')(script)

            log_dir = os.path.dirname(log_path)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            with open(log_path, 'wb') as log_file:
                log_file.write(log_type_data)

        await scripts_db.save_script_logs(
            db,
            s3_client_mock,
            script,
            scripts.get_static_filepath('test_script.py'),
            config,
        )

    assert s3_client_mock.upload_file_multipart.called
    assert s3_client_mock.upload_content.called

    # pylint: disable=unused-variable
    (
        _,
        _,
        file_size,
        chunk_size,
        *unimportant,
    ) = s3_client_mock.upload_file_multipart.call_args[0]

    assert chunk_size == config.LOG_UPLOAD_CHUNK_SIZE
    assert file_size == len(log_data['raw_stdout'])

    _, body, *unimportant = s3_client_mock.upload_content.call_args[0]
    assert body == log_data['raw_stderr']

    script_logs = await db.script_logs.find_one({'_id': script.primary_key})
    assert script_logs is not None

    for log_type in ('stdout', 'stderr'):
        assert script_logs[log_type] == (
            log_data[log_type][: settings.MAX_MONGO_TEXT_SIZE].decode()
        )
