# flake8: noqa
# pylint: disable=import-error,wildcard-import

################################################################################
# THIS IS BASE PERIODIC-TASK TESTS ONLY!                                       #
# PLEASE ADD HERE YOUR ALL BASIC TESTS                                         #
# e.g.: http errors, empty reposnse, invalid response, etc                     #
################################################################################

import os
import pytest
import shutil
import yatest.common

from tests_market_hide_offers_dyn2yt import utils


# It must be the same as in the [XXX]_dynamic.cpp file and .yaml config
ABO_PERIODIC_TASK = (
    'abo-dynamic-periodic-task',
    'market-sku-filters/current_market-sku-filters.pbuf',
    'abo',
)
CPA_PERIODIC_TASK = ('cpa-dynamic-periodic-task', 'dynamic', 'cpa')
СPC_PERIODIC_TASK = ('cpc-dynamic-periodic-task', 'dynamic', 'cpc')
SUPPLIER_PERIODIC_TASK = (
    'supplier-dynamic-periodic-task',
    'dynamic',
    'supplier',
)

CMD = '/run'
ABO_PERIODIC_TASK_CMD = ABO_PERIODIC_TASK[0] + CMD
CPA_PERIODIC_TASK_CMD = CPA_PERIODIC_TASK[0] + CMD
CPC_PERIODIC_TASK_CMD = СPC_PERIODIC_TASK[0] + CMD
SUPPLIER_PERIODIC_TASK_CMD = SUPPLIER_PERIODIC_TASK[0] + CMD

CMD_CLEAR = '/clear'
ABO_PERIODIC_TASK_CMD_CLEAR = ABO_PERIODIC_TASK[0] + CMD_CLEAR
CPA_PERIODIC_TASK_CMD_CLEAR = CPA_PERIODIC_TASK[0] + CMD_CLEAR
CPC_PERIODIC_TASK_CMD_CLEAR = СPC_PERIODIC_TASK[0] + CMD_CLEAR
SUPPLIER_PERIODIC_TASK_CMD_CLEAR = SUPPLIER_PERIODIC_TASK[0] + CMD_CLEAR

TESTPOINT_NAME = 'task::check_name_'
ABO_TESTPOINT_NAME = TESTPOINT_NAME + ABO_PERIODIC_TASK[0]
CPA_TESTPOINT_NAME = TESTPOINT_NAME + CPA_PERIODIC_TASK[0]
CPC_TESTPOINT_NAME = TESTPOINT_NAME + СPC_PERIODIC_TASK[0]
SUPPLIER_TESTPOINT_NAME = TESTPOINT_NAME + SUPPLIER_PERIODIC_TASK[0]

TESTPOINT_S3_PATH = 'task::check_s3_path_'
ABO_TESTPOINT_S3_PATH = TESTPOINT_S3_PATH + ABO_PERIODIC_TASK[0]
CPA_TESTPOINT_S3_PATH = TESTPOINT_S3_PATH + CPA_PERIODIC_TASK[0]
CPC_TESTPOINT_S3_PATH = TESTPOINT_S3_PATH + СPC_PERIODIC_TASK[0]
SUPPLIER_TESTPOINT_S3_PATH = TESTPOINT_S3_PATH + SUPPLIER_PERIODIC_TASK[0]

TESTPOINT_SAVE = 'task::check_saver_'
ABO_TESTPOINT_SAVE = TESTPOINT_SAVE + ABO_PERIODIC_TASK[0]
CPA_TESTPOINT_SAVE = TESTPOINT_SAVE + CPA_PERIODIC_TASK[0]
CPC_TESTPOINT_SAVE = TESTPOINT_SAVE + СPC_PERIODIC_TASK[0]
SUPPLIER_TESTPOINT_SAVE = TESTPOINT_SAVE + SUPPLIER_PERIODIC_TASK[0]

TESTPOINT_DYNAMIC = 'task::check_dynamic_'
ABO_TESTPOINT_DYNAMIC = TESTPOINT_DYNAMIC + ABO_PERIODIC_TASK[0]
CPA_TESTPOINT_DYNAMIC = TESTPOINT_DYNAMIC + CPA_PERIODIC_TASK[0]
CPC_TESTPOINT_DYNAMIC = TESTPOINT_DYNAMIC + СPC_PERIODIC_TASK[0]
SUPPLIER_TESTPOINT_DYNAMIC = TESTPOINT_DYNAMIC + SUPPLIER_PERIODIC_TASK[0]

TESTPOINT_HASH = 'task::check_hash_'
ABO_TESTPOINT_HASH = TESTPOINT_HASH + ABO_PERIODIC_TASK[0]
CPA_TESTPOINT_HASH = TESTPOINT_HASH + CPA_PERIODIC_TASK[0]
CPC_TESTPOINT_HASH = TESTPOINT_HASH + СPC_PERIODIC_TASK[0]
SUPPLIER_TESTPOINT_HASH = TESTPOINT_HASH + SUPPLIER_PERIODIC_TASK[0]

TESTPOINT_CLEAR = 'task::check_clear_'
ABO_TESTPOINT_CLEAR = TESTPOINT_CLEAR + ABO_PERIODIC_TASK[0]
CPA_TESTPOINT_CLEAR = TESTPOINT_CLEAR + CPA_PERIODIC_TASK[0]
CPC_TESTPOINT_CLEAR = TESTPOINT_CLEAR + СPC_PERIODIC_TASK[0]
SUPPLIER_TESTPOINT_CLEAR = TESTPOINT_CLEAR + SUPPLIER_PERIODIC_TASK[0]

TESTPOINT_EMERGENCY = 'task::check_emergency_'
ABO_TESTPOINT_EMERGENCY = TESTPOINT_EMERGENCY + ABO_PERIODIC_TASK[0]


@pytest.fixture()
def teardown():
    yield
    for task_name in [
            ABO_PERIODIC_TASK[2],
            CPA_PERIODIC_TASK[2],
            СPC_PERIODIC_TASK[2],
            SUPPLIER_PERIODIC_TASK[2],
    ]:
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

    @testpoint(CPA_TESTPOINT_CLEAR)
    def task_testpoint_cpa(data):
        pass

    @testpoint(CPC_TESTPOINT_CLEAR)
    def task_testpoint_cpc(data):
        pass

    @testpoint(SUPPLIER_TESTPOINT_CLEAR)
    def task_testpoint_supplier(data):
        pass

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    await taxi_market_hide_offers_dyn2yt.run_task(ABO_PERIODIC_TASK_CMD_CLEAR)
    await taxi_market_hide_offers_dyn2yt.run_task(CPA_PERIODIC_TASK_CMD_CLEAR)
    await taxi_market_hide_offers_dyn2yt.run_task(CPC_PERIODIC_TASK_CMD_CLEAR)
    await taxi_market_hide_offers_dyn2yt.run_task(
        SUPPLIER_PERIODIC_TASK_CMD_CLEAR,
    )
    await task_testpoint_abo.wait_call()
    await task_testpoint_cpa.wait_call()
    await task_testpoint_cpc.wait_call()
    await task_testpoint_supplier.wait_call()


# Checks task-name passing expects task-name
async def test_dynamic_task_name_passing(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.empty_response(request, mockserver)

    @testpoint(ABO_TESTPOINT_NAME)
    def task_testpoint_abo(data):
        return data

    @testpoint(CPA_TESTPOINT_NAME)
    def task_testpoint_cpa(data):
        return data

    @testpoint(CPC_TESTPOINT_NAME)
    def task_testpoint_cpc(data):
        return data

    @testpoint(SUPPLIER_TESTPOINT_NAME)
    def task_testpoint_supplier(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            ABO_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_abo.wait_call())['data']
        assert mock_mds.times_called == 1
        assert result['name'] == ABO_PERIODIC_TASK[0]

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPA_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpa.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['name'] == CPA_PERIODIC_TASK[0]

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPC_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpc.wait_call())['data']
        assert mock_mds.times_called == 3
        assert result['name'] == СPC_PERIODIC_TASK[0]

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            SUPPLIER_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_supplier.wait_call())['data']
        assert mock_mds.times_called == 4
        assert result['name'] == SUPPLIER_PERIODIC_TASK[0]


# Checks dynamic s3-path passing from config expects s3-path
async def test_dynamic_s3_path_passing(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.empty_response(request, mockserver)

    @testpoint(ABO_TESTPOINT_S3_PATH)
    def task_testpoint_abo(data):
        return data

    @testpoint(CPA_TESTPOINT_S3_PATH)
    def task_testpoint_cpa(data):
        return data

    @testpoint(CPC_TESTPOINT_S3_PATH)
    def task_testpoint_cpc(data):
        return data

    @testpoint(SUPPLIER_TESTPOINT_S3_PATH)
    def task_testpoint_supplier(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            ABO_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_abo.wait_call())['data']
        assert mock_mds.times_called == 1
        assert result['s3-path'] == ABO_PERIODIC_TASK[1]

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPA_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpa.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['s3-path'] == CPA_PERIODIC_TASK[1]

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPC_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpc.wait_call())['data']
        assert mock_mds.times_called == 3
        assert result['s3-path'] == СPC_PERIODIC_TASK[1]

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            SUPPLIER_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_supplier.wait_call())['data']
        assert mock_mds.times_called == 4
        assert result['s3-path'] == SUPPLIER_PERIODIC_TASK[1]


# Checks dynamic saving if server error expects false
async def test_dynamic_save_with_server_error(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.server_error(request, mockserver)

    @testpoint(ABO_TESTPOINT_SAVE)
    def task_testpoint_abo(data):
        return data

    @testpoint(CPA_TESTPOINT_SAVE)
    def task_testpoint_cpa(data):
        return data

    @testpoint(CPC_TESTPOINT_SAVE)
    def task_testpoint_cpc(data):
        return data

    @testpoint(SUPPLIER_TESTPOINT_SAVE)
    def task_testpoint_supplier(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            ABO_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_abo.wait_call())['data']
        assert mock_mds.times_called == 3
        assert result['saver'] == False

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPA_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpa.wait_call())['data']
        assert mock_mds.times_called == 6
        assert result['saver'] == False

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPC_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpc.wait_call())['data']
        assert mock_mds.times_called == 9
        assert result['saver'] == False

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            SUPPLIER_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_supplier.wait_call())['data']
        assert mock_mds.times_called == 12
        assert result['saver'] == False


# Checks dynamic content if server error expects nothing
async def test_dynamic_content_with_server_error(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.server_error(request, mockserver)

    @testpoint(ABO_TESTPOINT_DYNAMIC)
    def task_testpoint_abo(data):
        return data

    @testpoint(CPA_TESTPOINT_DYNAMIC)
    def task_testpoint_cpa(data):
        return data

    @testpoint(CPC_TESTPOINT_DYNAMIC)
    def task_testpoint_cpc(data):
        return data

    @testpoint(SUPPLIER_TESTPOINT_DYNAMIC)
    def task_testpoint_supplier(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            ABO_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_abo.wait_call())['data']
        assert mock_mds.times_called == 3
        assert result['dynamic'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPA_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpa.wait_call())['data']
        assert mock_mds.times_called == 6
        assert result['dynamic'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPC_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpc.wait_call())['data']
        assert mock_mds.times_called == 9
        assert result['dynamic'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            SUPPLIER_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_supplier.wait_call())['data']
        assert mock_mds.times_called == 12
        assert result['dynamic'] == ''


# Checks dynamic hash if server error expects nothing
async def test_dynamic_hash_with_server_error(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.server_error(request, mockserver)

    @testpoint(ABO_TESTPOINT_HASH)
    def task_testpoint_abo(data):
        return data

    @testpoint(CPA_TESTPOINT_HASH)
    def task_testpoint_cpa(data):
        return data

    @testpoint(CPC_TESTPOINT_HASH)
    def task_testpoint_cpc(data):
        return data

    @testpoint(SUPPLIER_TESTPOINT_HASH)
    def task_testpoint_supplier(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            ABO_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_abo.wait_call())['data']
        assert mock_mds.times_called == 3
        assert result['hash'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPA_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpa.wait_call())['data']
        assert mock_mds.times_called == 6
        assert result['hash'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPC_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpc.wait_call())['data']
        assert mock_mds.times_called == 9
        assert result['hash'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            SUPPLIER_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_supplier.wait_call())['data']
        assert mock_mds.times_called == 12
        assert result['hash'] == ''


# Checks dynamic saving if s3 bucket is empty expects nothing
async def test_dynamic_save_with_empty_s3_bucket(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.empty_response(request, mockserver)

    @testpoint(ABO_TESTPOINT_SAVE)
    def task_testpoint_abo(data):
        return data

    @testpoint(CPA_TESTPOINT_SAVE)
    def task_testpoint_cpa(data):
        return data

    @testpoint(CPC_TESTPOINT_SAVE)
    def task_testpoint_cpc(data):
        return data

    @testpoint(SUPPLIER_TESTPOINT_SAVE)
    def task_testpoint_supplier(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            ABO_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_abo.wait_call())['data']
        assert mock_mds.times_called == 1
        assert result['saver'] == False

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPA_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpa.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['saver'] == False

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPC_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpc.wait_call())['data']
        assert mock_mds.times_called == 3
        assert result['saver'] == False

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            SUPPLIER_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_supplier.wait_call())['data']
        assert mock_mds.times_called == 4
        assert result['saver'] == False


# Checks dynamic content if s3 bucket is empty expects nothing
async def test_dynamic_content_with_empty_s3_bucket(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.empty_response(request, mockserver)

    @testpoint(ABO_TESTPOINT_DYNAMIC)
    def task_testpoint_abo(data):
        return data

    @testpoint(CPA_TESTPOINT_DYNAMIC)
    def task_testpoint_cpa(data):
        return data

    @testpoint(CPC_TESTPOINT_DYNAMIC)
    def task_testpoint_cpc(data):
        return data

    @testpoint(SUPPLIER_TESTPOINT_DYNAMIC)
    def task_testpoint_supplier(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            ABO_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_abo.wait_call())['data']
        assert mock_mds.times_called == 1
        assert result['dynamic'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPA_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpa.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['dynamic'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPC_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpc.wait_call())['data']
        assert mock_mds.times_called == 3
        assert result['dynamic'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            SUPPLIER_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_supplier.wait_call())['data']
        assert mock_mds.times_called == 4
        assert result['dynamic'] == ''


# Checks dynamic hash if s3 bucket is empty expects nothing
async def test_dynamic_hash_with_empty_s3_bucket(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.empty_response(request, mockserver)

    @testpoint(ABO_TESTPOINT_HASH)
    def task_testpoint_abo(data):
        return data

    @testpoint(CPA_TESTPOINT_HASH)
    def task_testpoint_cpa(data):
        return data

    @testpoint(CPC_TESTPOINT_HASH)
    def task_testpoint_cpc(data):
        return data

    @testpoint(SUPPLIER_TESTPOINT_HASH)
    def task_testpoint_supplier(data):
        return data

    await taxi_market_hide_offers_dyn2yt.enable_testpoints()
    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            ABO_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_abo.wait_call())['data']
        assert mock_mds.times_called == 1
        assert result['hash'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPA_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpa.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['hash'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPC_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpc.wait_call())['data']
        assert mock_mds.times_called == 3
        assert result['hash'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            SUPPLIER_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_supplier.wait_call())['data']
        assert mock_mds.times_called == 4
        assert result['hash'] == ''


# Checks emergency for stop api expects 'periodic-tasks number'
async def test_dynamic_emergency_stop(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.empty_response(request, mockserver)

    @testpoint(ABO_TESTPOINT_EMERGENCY)
    def task_testpoint_abo_emergency(data):
        return data

    @testpoint(ABO_TESTPOINT_HASH)
    def task_testpoint_abo(data):
        return data

    @testpoint(CPA_TESTPOINT_HASH)
    def task_testpoint_cpa(data):
        return data

    @testpoint(CPC_TESTPOINT_HASH)
    def task_testpoint_cpc(data):
        return data

    @testpoint(SUPPLIER_TESTPOINT_HASH)
    def task_testpoint_supplier(data):
        return data

    response = await taxi_market_hide_offers_dyn2yt.post('v1/work/stop')
    assert response.status_code == 200

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            ABO_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_abo.wait_call())['data']
        assert mock_mds.times_called == 0
        assert result['hash'] == ''
        result = (await task_testpoint_abo_emergency.wait_call())['data']
        assert result['emergency-stop'] == utils.PERIODIC_TASKS_NUM

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPA_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpa.wait_call())['data']
        assert mock_mds.times_called == 0
        assert result['hash'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPC_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpc.wait_call())['data']
        assert mock_mds.times_called == 0
        assert result['hash'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            SUPPLIER_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_supplier.wait_call())['data']
        assert mock_mds.times_called == 0
        assert result['hash'] == ''


# Checks emergency for start api expects 'periodic-tasks number'
async def test_dynamic_emergency_start(
        taxi_market_hide_offers_dyn2yt,
        testpoint,
        mockserver,
        tearup,
        teardown,
):
    @mockserver.handler('/mds-s3', prefix=True)
    def mock_mds(request):
        return utils.empty_response(request, mockserver)

    @testpoint(ABO_TESTPOINT_EMERGENCY)
    def task_testpoint_abo_emergency(data):
        return data

    @testpoint(ABO_TESTPOINT_HASH)
    def task_testpoint_abo(data):
        return data

    @testpoint(CPA_TESTPOINT_HASH)
    def task_testpoint_cpa(data):
        return data

    @testpoint(CPC_TESTPOINT_HASH)
    def task_testpoint_cpc(data):
        return data

    @testpoint(SUPPLIER_TESTPOINT_HASH)
    def task_testpoint_supplier(data):
        return data

    response = await taxi_market_hide_offers_dyn2yt.post('v1/work/stop')
    assert response.status_code == 200

    response = await taxi_market_hide_offers_dyn2yt.post('v1/work/start')
    assert response.status_code == 200

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            ABO_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_abo.wait_call())['data']
        assert mock_mds.times_called == 1
        assert result['hash'] == ''
        result = (await task_testpoint_abo_emergency.wait_call())['data']
        assert result['emergency-start'] == utils.PERIODIC_TASKS_NUM

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPA_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpa.wait_call())['data']
        assert mock_mds.times_called == 2
        assert result['hash'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            CPC_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_cpc.wait_call())['data']
        assert mock_mds.times_called == 3
        assert result['hash'] == ''

    async with taxi_market_hide_offers_dyn2yt.spawn_task(
            SUPPLIER_PERIODIC_TASK_CMD,
    ):
        result = (await task_testpoint_supplier.wait_call())['data']
        assert mock_mds.times_called == 4
        assert result['hash'] == ''
