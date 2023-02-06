# flake8: noqa
# pylint: disable=import-error,wildcard-import

################################################################################
# THIS IS ABO PERIODIC-TASK TESTS ONLY!                                        #
# PLEASE ADD HERE YOUR ABO DYNAMIC SPECIFIC TEST                               #
################################################################################

import os
import pytest
import shutil
import yatest.common
from datetime import datetime

from tests_market_hide_offers_dyn2yt import utils


# It must be the same as in the abo_dynamic.cpp file
PERIODIC_TASK_NAME = ('abo-dynamic-periodic-task', 'abo')

PERIODIC_TASK_RUN = PERIODIC_TASK_NAME[0] + '/run'
PERIODIC_TASK_CLEAR = PERIODIC_TASK_NAME[0] + '/clear'

TESTPOINT_DYNAMIC = 'task::check_dynamic_' + PERIODIC_TASK_NAME[0]
TESTPOINT_SAVER = 'task::check_saver_' + PERIODIC_TASK_NAME[0]
TESTPOINT_HASH = 'task::check_hash_' + PERIODIC_TASK_NAME[0]
TESTPOINT_STATS = 'task::check_stats_' + PERIODIC_TASK_NAME[0]
TESTPOINT_EMERGENCY = 'task::check_emergency_' + PERIODIC_TASK_NAME[0]
TESTPOINT_CLEAR = 'task::check_clear_' + PERIODIC_TASK_NAME[0]

FILE = 'current_market-sku-filters.pbuf'

FILE_CONTENT = 'test_shop_sku_1'
FILE_HASH_1 = '5e8c2bec9f93e5377b44da131b18f81c4448e31f40e8adfff21eddb952ab579a7de2b730e0abbc6ade3cc600f186ad3645c7cf9a367fe0a97eab2dd9e2793480'
FILE_HASH_2 = 'a6e6102c2e5225da641d4f1aab88817037f8a0d92ba21e8d0574a478eb7663f59dc4356665bea9c55841f640687e2a6aed4712e68ddd4c9b4f28433d127a0794'


# Feel free to provide your custom implementation to override generated tests.


@pytest.fixture()
def teardown():
    yield
    path = yatest.common.work_path() + '/' + PERIODIC_TASK_NAME[1]
    if os.path.exists(path):
        shutil.rmtree(path)
    path = yatest.common.work_path() + '/' + PERIODIC_TASK_NAME[1] + '.shadow'
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
    bucket = utils.abo_s3_bucket_response(datetime.utcnow())
    dynamic = ''

    if request.method == 'GET':
        if utils.is_bucket_list(request):
            return mockserver.make_response(bucket, 200)
        else:
            return mockserver.make_response(dynamic, 200)

    return mockserver.make_response('Wrong method', 500)


def invalid_dynamic(request, mockserver):
    bucket = utils.abo_s3_bucket_response(datetime.utcnow())
    dynamic = 'this is not abo dynamic'

    if request.method == 'GET':
        if utils.is_bucket_list(request):
            return mockserver.make_response(bucket, 200)
        else:
            return mockserver.make_response(dynamic, 200)

    return mockserver.make_response('Wrong method', 500)


def valid_dynamic(request, mockserver, id):
    # In real life there is a actual delay between file modification
    # and microservice downloading.
    # So statement 'since-last-modified > 0' is true in case of tests
    bucket = utils.abo_s3_bucket_response(datetime.utcnow())
    dynamic = utils.abo_dynamic_response(FILE, FILE_CONTENT, id)

    if request.method == 'GET':
        if utils.is_bucket_list(request):
            return mockserver.make_response(bucket, 200)
        else:
            return mockserver.make_response(dynamic, 200)

    return mockserver.make_response('Wrong method', 500)


# Checks dynamic content reading if file is empty expects nothing
async def test_abo_dynamic_content_with_empty_dynamic(
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


# Checks dynamic content reading if file is invalid expects nothing
async def test_abo_dynamic_content_with_invalid_dynamic(
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


class TestContent:
    counter = 0


# Checks dynamic content reading if file is valid expects some file content
async def test_abo_dynamic_content_with_valid_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestContent.counter = TestContent.counter + 1
        return valid_dynamic(request, mockserver, TestContent.counter)

    @testpoint(TESTPOINT_DYNAMIC)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 2
    assert result['dynamic'] == FILE_CONTENT


# Checks dynamic saving if file is empty expects false
async def test_abo_dynamic_save_with_empty_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return empty_dynamic(request, mockserver)

    @testpoint(TESTPOINT_SAVER)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 2
    assert result['saver'] == False


# Checks dynamic saving if file is invalid expects false
async def test_abo_dynamic_save_with_invalid_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return invalid_dynamic(request, mockserver)

    @testpoint(TESTPOINT_SAVER)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 2
    assert result['saver'] == False


class TestSave:
    counter = 0


# Checks dynamic saving if file is valid expects true
async def test_abo_dynamic_save_with_valid_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestSave.counter = TestSave.counter + 1
        return valid_dynamic(request, mockserver, TestSave.counter)

    @testpoint(TESTPOINT_SAVER)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 2
    assert result['saver'] == True


# Checks dynamic hash if file is empty expects nothing
async def test_abo_dynamic_hash_with_emtpy_dynamic(
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


# Checks dynamic hash if file is invalid expects nothing
async def test_abo_dynamic_hash_with_invalid_dynamic(
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


class TestHash:
    counter = 0


# Checks dynamic hash if file is valid expects some hash
async def test_abo_dynamic_hash_with_valid_dynamic(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestHash.counter = TestHash.counter + 1
        return valid_dynamic(request, mockserver, TestHash.counter)

    @testpoint(TESTPOINT_HASH)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']

    assert mock_mds.times_called == 2
    assert result['hash'] == FILE_HASH_1


class TestHashRoutine:
    counter = 0


# Checks dynamic hashing routine expects new hash if files are different
async def test_abo_dynamic_hash_routine(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestHashRoutine.counter = TestHashRoutine.counter + 1
        id = TestHashRoutine.counter
        if id == 6:
            id = 4  # Emulates the same file as the previous
        return valid_dynamic(request, mockserver, id)

    @testpoint(TESTPOINT_HASH)
    def task_testpoint(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['hash'] == FILE_HASH_1

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 4
        assert result['hash'] == FILE_HASH_2

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint.wait_call())['data']
        assert mock_mds.times_called == 6
        assert result['hash'] == FILE_HASH_2


class TestStatisticRoutine:
    counter = 0


# Checks stats if dynamics are valid expects some delay
async def test_abo_dynamic_statistic_routine(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        TestStatisticRoutine.counter = TestStatisticRoutine.counter + 1
        return valid_dynamic(request, mockserver, TestStatisticRoutine.counter)

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


# Checks emergency stats for cache clear api expects 'periodic-tasks number'
async def test_abo_dynamic_emergency_cache_clear(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return valid_dynamic(request, mockserver, 2)

    @testpoint(TESTPOINT_HASH)
    def task_testpoint_hash(data):
        return data

    @testpoint(TESTPOINT_EMERGENCY)
    def task_testpoint_emergency(data):
        return data

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint_hash.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['hash'] == FILE_HASH_1

        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-cache-clear'] == 0

    response = await taxi_market_hide_offers_dyn2yt.post('v1/cache/clear')
    assert response.status_code == 200

    async with taxi_market_hide_offers_dyn2yt.spawn_task(PERIODIC_TASK_RUN):
        result = (await task_testpoint_hash.wait_call())['data']
        assert mock_mds.times_called == 4
        assert result['hash'] == FILE_HASH_1

        result = (await task_testpoint_emergency.wait_call())['data']
        assert result['emergency-cache-clear'] == utils.PERIODIC_TASKS_NUM
