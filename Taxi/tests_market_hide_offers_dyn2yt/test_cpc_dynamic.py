# flake8: noqa
# pylint: disable=import-error,wildcard-import

################################################################################
# THIS IS CPC-SHOP PERIODIC-TASK SPECIFIC TESTS ONLY!                          #
# PLEASE ADD HERE YOUR CPC-SHOP DYNAMIC SPECIFIC TESTS                         #
################################################################################

import os
import pytest
import shutil
import yatest.common
from datetime import datetime

from tests_market_hide_offers_dyn2yt import utils


# It must be the same as in the cpc_dynamic.cpp file and .yaml config
PERIODIC_TASK_NAME = ('cpc-dynamic-periodic-task', 'shop-cpc-filter.db', 'cpc')

PERIODIC_TASK_RUN = PERIODIC_TASK_NAME[0] + '/run'
PERIODIC_TASK_CLEAR = PERIODIC_TASK_NAME[0] + '/clear'

TESTPOINT_SAVE = 'task::check_saver_' + PERIODIC_TASK_NAME[0]
TESTPOINT_HASH = 'task::check_hash_' + PERIODIC_TASK_NAME[0]
TESTPOINT_DYNAMIC = 'task::check_dynamic_' + PERIODIC_TASK_NAME[0]
TESTPOINT_STATS = 'task::check_stats_' + PERIODIC_TASK_NAME[0]
TESTPOINT_EMERGENCY = 'task::check_emergency_' + PERIODIC_TASK_NAME[0]
TESTPOINT_CLEAR = 'task::check_clear_' + PERIODIC_TASK_NAME[0]

FILE_CONTENT = '2\n#20220519'
FILE_CONTENT_NEW = '22\n#20220519'


@pytest.fixture()
def teardown():
    yield
    path = yatest.common.work_path() + '/' + PERIODIC_TASK_NAME[2] + '.mds-s3'
    if os.path.exists(path):
        shutil.rmtree(path)
    path = yatest.common.work_path() + '/' + PERIODIC_TASK_NAME[2]
    if os.path.exists(path):
        shutil.rmtree(path)
    path = yatest.common.work_path() + '/' + PERIODIC_TASK_NAME[2] + '.shadow'
    if os.path.exists(path):
        shutil.rmtree(path)


@pytest.fixture()
async def tearup(taxi_market_hide_offers_dyn2yt, testpoint):
    @testpoint(TESTPOINT_CLEAR)
    def task_testpoint(data):
        pass

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(PERIODIC_TASK_CLEAR)
    await task_testpoint.wait_call()


def empty_dynamic(request, mockserver):
    bucket = utils.shops_mbi_s3_bucket_response(datetime.utcnow())
    dynamic = ''

    if request.method == 'GET':
        if utils.is_bucket_list(request):
            return mockserver.make_response(bucket, 200)
        else:
            return mockserver.make_response(dynamic, 200)

    return mockserver.make_response('Wrong method', 500)


def invalid_dynamic(request, mockserver):
    bucket = utils.shops_mbi_s3_bucket_response(datetime.utcnow())
    dynamic = utils.shops_mbi_dynamic_response(
        'this is not shop-cpa dynamic',
        PERIODIC_TASK_NAME[2],
        PERIODIC_TASK_NAME[1],
    )

    if request.method == 'GET':
        if utils.is_bucket_list(request):
            return mockserver.make_response(bucket, 200)
        else:
            return mockserver.make_response(dynamic, 200)

    return mockserver.make_response('Wrong method', 500)


def valid_dynamic(request, mockserver, predef_dynamic=''):
    # In real life there is a actual delay between file modification
    # and microservice downloading.
    # So statement 'since-last-modified > 0' is true in case of tests
    bucket = utils.shops_mbi_s3_bucket_response(datetime.utcnow())
    dynamic = utils.shops_mbi_dynamic_response(
        FILE_CONTENT, PERIODIC_TASK_NAME[2], PERIODIC_TASK_NAME[1],
    )
    if predef_dynamic != '':
        dynamic = predef_dynamic

    if request.method == 'GET':
        if utils.is_bucket_list(request):
            return mockserver.make_response(bucket, 200)
        else:
            return mockserver.make_response(dynamic, 200)

    return mockserver.make_response('Wrong method', 500)


class TestCounter:
    counter = 0


# Checks dynamic saving if bucket is empty expects false
async def test_cpc_dynamic_save_with_empty_bucket(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.empty_response(request, mockserver)

    @testpoint(TESTPOINT_SAVE)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 1
        assert result['saver'] == False


# Checks dynamic saving if file is empty expects false
async def test_cpc_dynamic_save_with_empty_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return empty_dynamic(request, mockserver)

    @testpoint(TESTPOINT_SAVE)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['saver'] == False


# Checks dynamic saving if file is invalid expects false
async def test_cpc_dynamic_save_with_invalid_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return invalid_dynamic(request, mockserver)

    @testpoint(TESTPOINT_SAVE)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['saver'] == False


# Checks dynamic saving if file is valid expects true
async def test_cpc_dynamic_save_with_valid_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return valid_dynamic(request, mockserver)

    @testpoint(TESTPOINT_SAVE)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['saver'] == True


# Checks dynamic hashing if bucket is empty expects nothing
async def test_cpc_dynamic_hash_with_empty_bucket(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.empty_response(request, mockserver)

    @testpoint(TESTPOINT_HASH)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 1
        assert result['hash'] == ''


# Checks dynamic hashing if file is empty expects nothing
async def test_cpc_dynamic_hash_with_empty_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return empty_dynamic(request, mockserver)

    @testpoint(TESTPOINT_HASH)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['hash'] == ''


# Checks dynamic hashing if file is invalid expects nothing
async def test_cpc_dynamic_hash_with_invalid_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return invalid_dynamic(request, mockserver)

    @testpoint(TESTPOINT_HASH)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['hash'] == ''


# Checks dynamic hashing if file is valid expects hash
async def test_cpc_dynamic_hash_with_valid_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return valid_dynamic(request, mockserver)

    @testpoint(TESTPOINT_HASH)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['hash'] != ''


# Checks dynamic content if bucket is empty expects nothing
async def test_cpc_dynamic_content_with_empty_bucket(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.empty_response(request, mockserver)

    @testpoint(TESTPOINT_DYNAMIC)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 1
        assert result['dynamic'] == ''


# Checks dynamic content if file is empty expects nothing
async def test_cpc_dynamic_content_with_empty_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return empty_dynamic(request, mockserver)

    @testpoint(TESTPOINT_DYNAMIC)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['dynamic'] == ''


# Checks dynamic content if file is invalid expects nothing
async def test_cpc_dynamic_content_with_invalid_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return invalid_dynamic(request, mockserver)

    @testpoint(TESTPOINT_DYNAMIC)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['dynamic'] == ''


# Checks dynamic content if file is valid expects content
async def test_cpc_dynamic_content_with_valid_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return valid_dynamic(request, mockserver)

    @testpoint(TESTPOINT_DYNAMIC)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['dynamic'] == FILE_CONTENT


class TestDynamicHash:
    counter = 0


# Checks dynamic hashing routine expects new hash if files are different
async def test_cpc_dynamic_hash_routine(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    response1 = utils.shops_mbi_dynamic_response(
        FILE_CONTENT, PERIODIC_TASK_NAME[2], PERIODIC_TASK_NAME[1],
    )
    response2 = utils.shops_mbi_dynamic_response(
        FILE_CONTENT_NEW, PERIODIC_TASK_NAME[2], PERIODIC_TASK_NAME[1],
    )

    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestDynamicHash.counter = TestDynamicHash.counter + 1
        if TestDynamicHash.counter == 2:
            return valid_dynamic(request, mockserver, response1)
        elif TestDynamicHash.counter == 4:
            return valid_dynamic(request, mockserver, response2)
        elif TestDynamicHash.counter == 6:
            return valid_dynamic(request, mockserver, response2)
        else:
            return valid_dynamic(request, mockserver)

    @testpoint(TESTPOINT_HASH)
    def task_testpoint(data):
        return data

    file_hash = ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['hash'] != ''
        file_hash = result['hash']

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 4
        assert result['hash'] != file_hash
        file_hash = result['hash']

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 6
        assert result['hash'] == file_hash


class TestDynamicStats:
    counter = 0


# Checks stats if dynamics are valid expects some delay
async def test_cpc_dynamic_statistic_routine(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    response1 = utils.shops_mbi_dynamic_response(
        FILE_CONTENT, PERIODIC_TASK_NAME[2], PERIODIC_TASK_NAME[1],
    )
    response2 = utils.shops_mbi_dynamic_response(
        FILE_CONTENT_NEW, PERIODIC_TASK_NAME[2], PERIODIC_TASK_NAME[1],
    )

    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestDynamicStats.counter = TestDynamicStats.counter + 1
        if TestDynamicStats.counter == 2:
            return valid_dynamic(request, mockserver, response1)
        elif TestDynamicStats.counter == 4:
            return valid_dynamic(request, mockserver, response2)
        else:
            return valid_dynamic(request, mockserver)

    @testpoint(TESTPOINT_STATS)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['since-last-modified'] > 0
        assert result['since-last-work'] >= 0

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 4
        assert result['since-last-modified'] > 0
        assert result['since-last-work'] >= 0


class TestCacheClear:
    counter = 0


# Checks emergency stats for cache clear api expects 'periodic-tasks number'
async def test_cpc_dynamic_emergency_cache_clear(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    response1 = utils.shops_mbi_dynamic_response(
        FILE_CONTENT, PERIODIC_TASK_NAME[2], PERIODIC_TASK_NAME[1],
    )

    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestCacheClear.counter = TestCacheClear.counter + 1
        if TestCacheClear.counter == 2:
            return valid_dynamic(request, mockserver, response1)
        elif TestCacheClear.counter == 4:
            return valid_dynamic(request, mockserver, response1)
        else:
            return valid_dynamic(request, mockserver)

    @testpoint(TESTPOINT_HASH)
    def task_testpoint_hash(data):
        return data

    @testpoint(TESTPOINT_EMERGENCY)
    def task_testpoint_emergency(data):
        return data

    file_hash = ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint_hash.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['hash'] != ''
        file_hash = result['hash']

        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-cache-clear'] == 0

    response = await taxi_market_hide_offers_dyn2yt.post('v1/cache/clear')
    assert response.status_code == 200

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint_hash.wait_call())['data']
        assert mock_mds.times_called == 4
        assert result['hash'] == file_hash

        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-cache-clear'] == utils.PERIODIC_TASKS_NUM
