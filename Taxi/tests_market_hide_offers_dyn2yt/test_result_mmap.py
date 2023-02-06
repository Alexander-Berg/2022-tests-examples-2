# flake8: noqa
# pylint: disable=import-error,wildcard-import
import os
import time
import pytest
import shutil
import yatest.common
from datetime import datetime

from tests_market_hide_offers_dyn2yt import utils


# It must be the same as in the result_mmap.cpp file
ABO_PERIODIC_TASK_NAME = 'abo-dynamic-periodic-task'
RMM_PERIODIC_TASK_NAME = 'result-mmap-periodic-task'

ABO_PERIODIC_TASK_RUN = ABO_PERIODIC_TASK_NAME + '/run'
ABO_PERIODIC_TASK_CLEAR = ABO_PERIODIC_TASK_NAME + '/clear'

RMM_PERIODIC_TASK_RUN = RMM_PERIODIC_TASK_NAME + '/run'
RMM_PERIODIC_TASK_RUN_MASTER = RMM_PERIODIC_TASK_NAME + '/run-master'
RMM_PERIODIC_TASK_RUN_SLAVE = RMM_PERIODIC_TASK_NAME + '/run-slave'
RMM_PERIODIC_TASK_RUN_FAKE_SIGNAL_MASTER = (
    RMM_PERIODIC_TASK_NAME + '/run-fake-signal-master'
)
RMM_PERIODIC_TASK_CLEAR = RMM_PERIODIC_TASK_NAME + '/clear'

ABO_TESTPOINT_CLEAR = 'task::check_clear_' + ABO_PERIODIC_TASK_NAME
RMM_TESTPOINT_CONVERT_STATUS = (
    'task::check_convert_status_' + RMM_PERIODIC_TASK_NAME
)
RMM_TESTPOINT_HASH = 'task::check_hash_' + RMM_PERIODIC_TASK_NAME
RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS = (
    'task::check_s3_upload_current_status_' + RMM_PERIODIC_TASK_NAME
)
RMM_TESTPOINT_S3_UPLOAD_BACKUP_STATUS = (
    'task::check_s3_upload_backup_status_' + RMM_PERIODIC_TASK_NAME
)
RMM_TESTPOINT_NEW_VERSION = 'task::check_new_version_' + RMM_PERIODIC_TASK_NAME
RMM_TESTPOINT_STATS = 'task::check_stats_' + RMM_PERIODIC_TASK_NAME
RMM_TESTPOINT_CLEAR = 'task::check_clear_' + RMM_PERIODIC_TASK_NAME
RMM_TESTPOINT_EMERGENCY = 'task::check_emergency_' + RMM_PERIODIC_TASK_NAME

ABO_BUCKET = 'market-sku-filters'
ABO_FILE = 'current_market-sku-filters.pbuf'
ABO_FILE_CONTENT = 'test_shop_sku_1'
ABO_URL = ABO_BUCKET + '/' + ABO_FILE

DELAY = 10  # sec

# Feel free to provide your custom implementation to override generated tests.


@pytest.fixture()
def teardown():
    yield
    for task_name in ['abo', 'cpa', 'cpc', 'supplier']:
        path = yatest.common.work_path() + '/' + task_name + '.mds-s3'
        if os.path.exists(path):
            shutil.rmtree(path)
        path = yatest.common.work_path() + '/' + task_name
        if os.path.exists(path):
            shutil.rmtree(path)
        path = yatest.common.work_path() + '/' + task_name + '.shadow'
        if os.path.exists(path):
            shutil.rmtree(path)


@pytest.fixture()
async def tearup(taxi_market_hide_offers_dyn2yt, testpoint):
    @testpoint(ABO_TESTPOINT_CLEAR)
    def task_testpoint_abo(data):
        pass

    @testpoint(RMM_TESTPOINT_CLEAR)
    def task_testpoint_rmm(data):
        pass

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_CLEAR)
    await taxi_market_hide_offers_dyn2yt.run_task(RMM_PERIODIC_TASK_CLEAR)

    await task_testpoint_abo.wait_call()
    await task_testpoint_rmm.wait_call()


def all_dynamics():
    for dir, file, data in [
            (
                '/abo',
                '/abo.pbuf',
                utils.abo_dynamic_response(ABO_FILE, ABO_FILE_CONTENT, 1),
            ),
            ('/cpa', '/shop-cpa-filter.db', b'1\n#20220519'),
            ('/cpc', '/shop-cpc-filter.db', b'2\n#20220519'),
            ('/supplier', '/supplier-filter.db', b'3\n#20220519'),
    ]:
        path = yatest.common.work_path() + dir
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + file, 'wb') as writer:
            writer.write(data)


def invalid_abo_dynamic():
    path = yatest.common.work_path() + '/abo'
    if not os.path.exists(path):
        os.mkdir(path)
    with open(path + '/abo', 'wb') as writer:
        writer.write(b'this is not abo dynamic')


def abo_dynamic(request, mockserver, mock_calls=1, put_status=200):
    # In real life there is a actual delay between file modification
    # and microservice downloading.
    # So statement 'since-last-modified > 0' is true in case of tests
    bucket = utils.abo_s3_bucket_response(datetime.utcnow())
    dynamic = utils.abo_dynamic_response(
        ABO_FILE, ABO_FILE_CONTENT, mock_calls,
    )

    if request.method == 'GET':
        if utils.is_bucket_list(request):
            return mockserver.make_response(bucket, 200)
        else:
            return mockserver.make_response(dynamic, 200)

    if request.method == 'PUT':
        return mockserver.make_response('OK', put_status)

    return mockserver.make_response('Wrong method', 500)


def mmap_response(request, mockserver):
    bucket = utils.mmap_s3_bucket_response(datetime.utcnow())

    if request.method == 'GET':
        if utils.is_bucket_list(request):
            return mockserver.make_response(bucket, 200)

    return mockserver.make_response('Wrong method', 500)


def server_upload(request, mockserver):
    if request.method == 'PUT':
        return mockserver.make_response('OK', 200)
    return mockserver.make_response('Wrong method', 500)


# Checks all mmap statuses if no dynamics expects false
async def test_result_mmap_abo_convert_status_with_no_dynamics(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @testpoint(RMM_TESTPOINT_CONVERT_STATUS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_FAKE_SIGNAL_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert result['abo-convert'] == False


# Checks abo-mmap status if file is invalid expects false
async def test_result_mmap_abo_convert_status_with_invalid_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    invalid_abo_dynamic()

    @testpoint(RMM_TESTPOINT_CONVERT_STATUS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_FAKE_SIGNAL_MASTER,
    ):
        rmm_result = (await task_testpoint.wait_call())['data']

    assert rmm_result['abo-convert'] == False


# Checks abo-mmap status if file is valid expects true
async def test_result_mmap_abo_convert_status_with_valid_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_CONVERT_STATUS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        rmm_result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 4
    assert rmm_result['abo-convert'] == True


class TestConvertSameFile:
    counter = 0


# Checks abo-mmap status if file is valid and same expects true
async def test_result_mmap_abo_convert_status_with_same_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestConvertSameFile.counter = TestConvertSameFile.counter + 1
        return abo_dynamic(request, mockserver, TestConvertSameFile.counter)

    @testpoint(RMM_TESTPOINT_CONVERT_STATUS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 4
    assert result['abo-convert'] == True

    TestConvertSameFile.counter = 0

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 6
    assert result['abo-convert'] == True


# Checks all dynamic hash if no dynamics expects nothing
async def test_result_mmap_abo_hash_with_no_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @testpoint(RMM_TESTPOINT_HASH)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_FAKE_SIGNAL_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert result['abo-hash'] == ''


# Checks abo-dynamic hash if file is invalid expects nothing
async def test_result_mmap_abo_hash_with_invalid_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    invalid_abo_dynamic()

    @testpoint(RMM_TESTPOINT_HASH)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_FAKE_SIGNAL_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert result['abo-hash'] == ''


# Checks abo-dynamic hash if file is valid expects some hash
async def test_result_mmap_abo_hash_with_valid_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_HASH)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 4
    assert result['abo-hash'] != ''


class TestHashSameFile:
    counter = 0


# Checks dynamic hashing routine expects same hash if files are equal
async def test_result_mmap_abo_hash_with_same_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestHashSameFile.counter = TestHashSameFile.counter + 1
        return abo_dynamic(request, mockserver, TestHashSameFile.counter)

    @testpoint(RMM_TESTPOINT_HASH)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 4
    file_hash = result['abo-hash']
    assert result['abo-hash'] != ''

    TestHashSameFile.counter = 0

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 6
    assert result['abo-hash'] == file_hash


class TestHash:
    counter = 0


# Checks dynamic hashing routine expects new hash if files are different
async def test_result_mmap_abo_hash_with_different_files(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestHash.counter = TestHash.counter + 1
        return abo_dynamic(request, mockserver, TestHash.counter)

    @testpoint(RMM_TESTPOINT_HASH)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 4
    file_hash = result['abo-hash']
    assert result['abo-hash'] != ''

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 7
    assert result['abo-hash'] != file_hash


# Checks s3-mds upload current-status with server error expects false
async def test_result_mmap_s3_current_upload_with_server_error(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver, put_status=500)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 8
    assert result['s3-current-upload'] == False


# Checks s3-mds upload current-status if no file expects false
async def test_result_mmap_s3_current_upload_with_no_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_FAKE_SIGNAL_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 0
    assert result['s3-current-upload'] == False


# Checks s3-mds upload current-status if file is invalid expects false
async def test_result_mmap_s3_current_upload_with_invalid_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    invalid_abo_dynamic()

    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_FAKE_SIGNAL_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 0
    assert result['s3-current-upload'] == False


# Checks s3-mds upload current-status if file is valid expects true
async def test_result_mmap_s3_current_upload_with_valid_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 4
    assert result['s3-current-upload'] == True


class TestUpload:
    counter = 0


# Checks s3-mds upload current-status if file is valid and same expects false
async def test_result_mmap_s3_current_upload_with_same_valid_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestUpload.counter = TestUpload.counter + 1
        return abo_dynamic(request, mockserver, TestUpload.counter)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 4
    assert result['s3-current-upload'] == True

    TestUpload.counter = 0

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 6
    assert result['s3-current-upload'] == False


# Checks s3-mds upload backup-status if file is valid expects true
async def test_result_mmap_s3_backup_upload_with_valid_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_BACKUP_STATUS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 4
    assert result['s3-backup-upload'] == True


class TestBackup:
    counter = 0


# Checks s3-mds upload backup-status if file is valid expects true
async def test_result_mmap_s3_backup_upload_with_valid_file_without_delay(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestBackup.counter = TestBackup.counter + 1
        return abo_dynamic(request, mockserver, TestBackup.counter)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_BACKUP_STATUS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 4
    assert result['s3-backup-upload'] == True

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 7
    assert result['s3-backup-upload'] == False


class TestBackupDelay:
    counter = 0


# Checks s3-mds upload backup-status if file is valid expects true
async def test_result_mmap_s3_backup_upload_with_valid_file_with_delay(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestBackupDelay.counter = TestBackupDelay.counter + 1
        return abo_dynamic(request, mockserver, TestBackupDelay.counter)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_BACKUP_STATUS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 4
    assert result['s3-backup-upload'] == True

    time.sleep(DELAY)

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 8
    assert result['s3-backup-upload'] == True


# Checks new version status if no file expects false
async def test_result_mmap_new_version_with_no_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_NEW_VERSION)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_FAKE_SIGNAL_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 0
    assert result['new-version'] == False


# Checks new version status status if file is invalid expects false
async def test_result_mmap_new_version_with_invalid_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    invalid_abo_dynamic()

    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_NEW_VERSION)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_FAKE_SIGNAL_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 0
    assert result['new-version'] == False


# Checks new version upload status if file is valid expects true
async def test_result_mmap_new_version_with_valid_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_NEW_VERSION)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 4
    assert result['new-version'] == True


class TestNewVersion:
    counter = 0


# Checks new version status if file is valid and same expects false
async def test_result_mmap_new_version_with_same_valid_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestNewVersion.counter = TestNewVersion.counter + 1
        return abo_dynamic(request, mockserver, TestNewVersion.counter)

    @testpoint(RMM_TESTPOINT_NEW_VERSION)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 4
    assert result['new-version'] == True

    TestNewVersion.counter = 0

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 6
    assert result['new-version'] == False


# Checks slave s3-mds upload statuses if file is valid expects false
async def test_result_mmap_slave_s3_upload_with_valid_file(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS)
    def task_testpoint_current(data):
        return data

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_BACKUP_STATUS)
    def task_testpoint_backup(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_SLAVE,
    ):
        result_current = (await task_testpoint_current.wait_call())['data']
        result_backup = (await task_testpoint_backup.wait_call())['data']

    assert mock_mds.times_called == 2
    assert result_current['s3-current-upload'] == False
    assert result_backup['s3-backup-upload'] == False


# Checks all mmap status if files are valid expects true
async def test_result_mmap_statuses_with_all_valid_dynamics(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    all_dynamics()

    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return server_upload(request, mockserver)

    @testpoint(RMM_TESTPOINT_HASH)
    def task_testpoint_hash(data):
        return data

    @testpoint(RMM_TESTPOINT_CONVERT_STATUS)
    def task_testpoint_convert(data):
        return data

    @testpoint(RMM_TESTPOINT_NEW_VERSION)
    def task_testpoint_new_version(data):
        return data

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS)
    def task_testpoint_current(data):
        return data

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_BACKUP_STATUS)
    def task_testpoint_backup(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_FAKE_SIGNAL_MASTER,
    ):
        result_hash = (await task_testpoint_hash.wait_call())['data']
        result_convert = (await task_testpoint_convert.wait_call())['data']
        result_new_version = (await task_testpoint_new_version.wait_call())[
            'data'
        ]
        result_current = (await task_testpoint_current.wait_call())['data']
        result_backup = (await task_testpoint_backup.wait_call())['data']

        assert result_hash['abo-hash'] != ''
        assert result_hash['cpa-hash'] != ''
        assert result_hash['cpc-hash'] != ''
        assert result_hash['supplier-hash'] != ''

        assert result_convert['abo-convert'] == True
        assert result_convert['cpa-convert'] == True
        assert result_convert['cpc-convert'] == True
        assert result_convert['supplier-convert'] == True

        assert result_new_version['new-version'] == True

        assert result_current['s3-current-upload'] == True
        assert result_backup['s3-backup-upload'] == True

        assert mock_mds.times_called == 2


# Checks all mmap status if files are invalid expects true
async def test_result_mmap_statuses_with_all_invalid_dynamics(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return server_upload(request, mockserver)

    @testpoint(RMM_TESTPOINT_HASH)
    def task_testpoint_hash(data):
        return data

    @testpoint(RMM_TESTPOINT_CONVERT_STATUS)
    def task_testpoint_convert(data):
        return data

    @testpoint(RMM_TESTPOINT_NEW_VERSION)
    def task_testpoint_new_version(data):
        return data

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS)
    def task_testpoint_current(data):
        return data

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_BACKUP_STATUS)
    def task_testpoint_backup(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_FAKE_SIGNAL_MASTER,
    ):
        result_hash = (await task_testpoint_hash.wait_call())['data']
        result_convert = (await task_testpoint_convert.wait_call())['data']
        result_new_version = (await task_testpoint_new_version.wait_call())[
            'data'
        ]
        result_current = (await task_testpoint_current.wait_call())['data']
        result_backup = (await task_testpoint_backup.wait_call())['data']

        assert result_hash['abo-hash'] == ''
        assert result_hash['cpa-hash'] == ''
        assert result_hash['cpc-hash'] == ''
        assert result_hash['supplier-hash'] == ''

        assert result_convert['abo-convert'] == False
        assert result_convert['cpa-convert'] == False
        assert result_convert['cpc-convert'] == False
        assert result_convert['supplier-convert'] == False

        assert result_new_version['new-version'] == False

        assert result_current['s3-current-upload'] == False
        assert result_backup['s3-backup-upload'] == False

        assert mock_mds.times_called == 0


class TestStats:
    counter = 0


# Checks stats if dynamics are valid expects some delay
async def test_result_mmap_statistic_routine(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestStats.counter = TestStats.counter + 1
        return abo_dynamic(request, mockserver, TestStats.counter)

    @testpoint(RMM_TESTPOINT_STATS)
    def task_testpoint(data):
        return data

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 4
        assert result['since-last-modified'] >= 0
        assert result['since-last-work'] >= 0
        assert result['is-master'] == 1

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 7
        assert result['since-last-modified'] >= 0
        assert result['since-last-work'] >= 0
        assert result['is-master'] == 1


# Checks mmap emergency role set api expects same role as set by api
async def test_result_mmap_emergency_role_set_master(
        taxi_market_hide_offers_dyn2yt, testpoint, tearup, teardown,
):
    @testpoint(RMM_TESTPOINT_STATS)
    def task_testpoint(data):
        return data

    @testpoint(RMM_TESTPOINT_EMERGENCY)
    def task_testpoint_emergency(data):
        return data

    response = await taxi_market_hide_offers_dyn2yt.post(
        'v1/role/set', json={'role': 'master'},
    )
    assert response.status_code == 200

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN,
    ):
        result = (await task_testpoint.wait_call())['data']
        assert result['is-master'] == 1
        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-role-set'] == 1


# Checks mmap emergency role set api expects same role as set by api
async def test_result_mmap_emergency_role_set_slave(
        taxi_market_hide_offers_dyn2yt, testpoint, tearup, teardown,
):
    @testpoint(RMM_TESTPOINT_STATS)
    def task_testpoint(data):
        return data

    @testpoint(RMM_TESTPOINT_EMERGENCY)
    def task_testpoint_emergency(data):
        return data

    response = await taxi_market_hide_offers_dyn2yt.post(
        'v1/role/set', json={'role': 'slave'},
    )
    assert response.status_code == 200

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN,
    ):
        result = (await task_testpoint.wait_call())['data']
        assert result['is-master'] == 0
        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-role-set'] == 1


# Checks mmap emergency role set api expects same role as set by api
async def test_result_mmap_emergency_role_set_unknown(
        taxi_market_hide_offers_dyn2yt, testpoint, tearup, teardown,
):
    @testpoint(RMM_TESTPOINT_STATS)
    def task_testpoint(data):
        return data

    @testpoint(RMM_TESTPOINT_EMERGENCY)
    def task_testpoint_emergency(data):
        return data

    response = await taxi_market_hide_offers_dyn2yt.post(
        'v1/role/set', json={'role': '_'},
    )
    assert response.status_code == 400

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN,
    ):
        result = (await task_testpoint.wait_call())['data']
        assert result['is-master'] == 0
        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-role-set'] == 0


# Checks mmap emergency role usnet api expects same role as before api
async def test_result_mmap_emergency_role_unset(
        taxi_market_hide_offers_dyn2yt, testpoint, tearup, teardown,
):
    @testpoint(RMM_TESTPOINT_STATS)
    def task_testpoint(data):
        return data

    @testpoint(RMM_TESTPOINT_EMERGENCY)
    def task_testpoint_emergency(data):
        return data

    response = await taxi_market_hide_offers_dyn2yt.post(
        'v1/role/set', json={'role': 'master'},
    )
    assert response.status_code == 200

    response = await taxi_market_hide_offers_dyn2yt.post('v1/role/unset')
    assert response.status_code == 200

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN,
    ):
        result = (await task_testpoint.wait_call())['data']
        assert result['is-master'] == 0
        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-role-unset'] == 1


# Checks mmap emergency for cache clear api expects `periodic-tasks number`
async def test_result_mmap_emergency_cache_clear(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS)
    def task_testpoint_upload(data):
        return data

    @testpoint(RMM_TESTPOINT_EMERGENCY)
    def task_testpoint_emergency(data):
        return data

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint_upload.wait_call())['data']
        assert result['s3-current-upload'] == True
        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-cache-clear'] == 0
        assert mock_mds.times_called == 4

    response = await taxi_market_hide_offers_dyn2yt.post('v1/cache/clear')
    assert response.status_code == 200

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint_upload.wait_call())['data']
        assert result['s3-current-upload'] == True
        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-cache-clear'] == utils.PERIODIC_TASKS_NUM
        assert mock_mds.times_called == 8


# Checks emergency for rules create api expects 1
async def test_result_mmap_emergency_rules_create(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS)
    def task_testpoint_upload(data):
        return data

    @testpoint(RMM_TESTPOINT_EMERGENCY)
    def task_testpoint_emergency(data):
        return data

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint_upload.wait_call())['data']
        assert result['s3-current-upload'] == True
        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-rules-create'] == 0
        assert mock_mds.times_called == 4

    response = await taxi_market_hide_offers_dyn2yt.post('v1/rules/create')
    assert response.status_code == 200

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint_upload.wait_call())['data']
        assert result['s3-current-upload'] == True
        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-rules-create'] == 1
        assert mock_mds.times_called == 6


# Checks emergency for rules list api expects 1
async def test_result_mmap_emergency_rules_list(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return mmap_response(request, mockserver)

    @testpoint(RMM_TESTPOINT_EMERGENCY)
    def task_testpoint_emergency(data):
        return data

    response = await taxi_market_hide_offers_dyn2yt.post(
        'v1/rules/list', json={'dir': ''},
    )
    assert response.status_code == 200
    assert mock_mds.times_called == 1
    assert response.json() == {
        'items': [
            {'file': 'current_market-sku-filters.pbuf'},
            {'file': 'backup_market-sku-filters.pbuf-1'},
            {'file': 'backup_market-sku-filters.pbuf-2'},
        ],
    }

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-rules-list'] == 1


# Checks emergency for rules recreate api expects 1
async def test_result_mmap_emergency_rules_recreate(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_EMERGENCY)
    def task_testpoint_emergency(data):
        return data

    response = await taxi_market_hide_offers_dyn2yt.post(
        'v1/rules/recreate',
        json={
            'file-from': 'market-sku-filters/backup_market-sku-filters.pbuf',
            'file-to': 'market-sku-filters/current_market-sku-filters.pbuf',
        },
    )
    assert response.status_code == 200
    assert mock_mds.times_called == 2

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN,
    ):
        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-rules-recreate'] == 1


# Checks emergency for stop api expects 'periodic-tasks number'
async def test_result_mmap_emergency_stop(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS)
    def task_testpoint_upload(data):
        return data

    @testpoint(RMM_TESTPOINT_EMERGENCY)
    def task_testpoint_emergency(data):
        return data

    response = await taxi_market_hide_offers_dyn2yt.post('v1/work/stop')
    assert response.status_code == 200

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint_upload.wait_call())['data']
        assert result['s3-current-upload'] == False
        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-stop'] == utils.PERIODIC_TASKS_NUM
        assert mock_mds.times_called == 0


# Checks emergency for start api expects 'periodic-tasks number'
async def test_result_mmap_emergency_start(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return abo_dynamic(request, mockserver)

    @testpoint(RMM_TESTPOINT_S3_UPLOAD_CURRENT_STATUS)
    def task_testpoint_upload(data):
        return data

    @testpoint(RMM_TESTPOINT_EMERGENCY)
    def task_testpoint_emergency(data):
        return data

    response = await taxi_market_hide_offers_dyn2yt.post('v1/work/stop')
    assert response.status_code == 200

    response = await taxi_market_hide_offers_dyn2yt.post('v1/work/start')
    assert response.status_code == 200

    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_RUN)
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            RMM_PERIODIC_TASK_RUN_MASTER,
    ):
        result = (await task_testpoint_upload.wait_call())['data']
        assert result['s3-current-upload'] == True
        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-start'] == utils.PERIODIC_TASKS_NUM
        assert mock_mds.times_called == 4
