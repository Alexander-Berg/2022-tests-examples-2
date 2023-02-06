import pytest

from tests_bank_applications import common
from tests_bank_applications.product import db_helpers

MOCK_NOW = '2021-09-28T19:31:00.100+00:00'
CONFIG = {
    'polling_interval': 5,
    'soft_polling_interval': 60,
    'tries_after_soft_penalty_apply': 3,
    'tries_after_hard_penalty_apply': 10,
}


def get_attributes(
        application_id,
        request_id=common.CORE_REQUEST_ID,
        product=common.PRODUCT_WALLET,
):
    return {
        'application_id': application_id,
        'request_id': request_id,
        'yuid': common.DEFAULT_YANDEX_UID,
        'buid': common.DEFAULT_YANDEX_BUID,
        'idempotency_token': common.DEFAULT_IDEMPOTENCY_TOKEN,
        'client_ip': common.SOME_IP,
        'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
        'product': product,
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(BANK_APPLICATIONS_POLLING_PRODUCT_STATUS_SETTINGS=CONFIG)
async def test_pending(
        stq_runner,
        pgsql,
        stq,
        bank_core_current_account_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_application(
        pgsql, status=common.STATUS_CORE_BANKING,
    )
    await stq_runner.bank_applications_product_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=False,
    )
    assert stq.bank_applications_product_status_polling.times_called == 1
    stq_call = stq.bank_applications_product_status_polling.next_call()
    assert stq_call['eta'].isoformat() == '2021-09-28T19:31:05.100000'
    assert (
        bank_core_current_account_mock.request_check_handler.times_called == 1
    )
    assert not taxi_processing_mock.create_event_handler.has_calls
    application = db_helpers.select_application(pgsql, application_id)
    assert application.status == common.STATUS_CORE_BANKING


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(BANK_APPLICATIONS_POLLING_PRODUCT_STATUS_SETTINGS=CONFIG)
async def test_pending_soft_and_hard_limit(
        stq_runner, pgsql, stq, bank_core_current_account_mock,
):
    application_id = db_helpers.insert_application(
        pgsql, status=common.STATUS_CORE_BANKING,
    )
    await stq_runner.bank_applications_product_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        reschedule_counter=4,
        expect_fail=False,
    )
    assert stq.bank_applications_product_status_polling.times_called == 1
    stq_call = stq.bank_applications_product_status_polling.next_call()
    assert stq_call['eta'].isoformat() == '2021-09-28T19:32:00.100000'

    await stq_runner.bank_applications_product_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        reschedule_counter=11,
        expect_fail=True,
    )
    assert stq.bank_applications_product_status_polling.times_called == 0


async def test_success(
        stq_runner,
        pgsql,
        stq,
        bank_core_current_account_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_application(
        pgsql, status=common.STATUS_CORE_BANKING,
    )
    bank_core_current_account_mock.response = {
        'status': common.STATUS_SUCCESS,
        'request_id': common.CORE_REQUEST_ID,
    }
    await stq_runner.bank_applications_product_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=False,
    )
    assert not stq.bank_applications_product_status_polling.has_calls
    assert taxi_processing_mock.create_event_handler.times_called == 1
    call = taxi_processing_mock.create_event_handler.next_call()
    assert (
        call['request'].headers['X-Idempotency-Token']
        == common.DEFAULT_IDEMPOTENCY_TOKEN
    )
    assert call['request'].json == {
        'kind': 'update',
        'type': 'product_after',
        'yuid': common.DEFAULT_YANDEX_UID,
        'buid': common.DEFAULT_YANDEX_BUID,
        'client_ip': common.SOME_IP,
        'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
        'product': 'WALLET',
        'core_request_id': common.CORE_REQUEST_ID,
    }
    application = db_helpers.select_application(pgsql, application_id)
    assert application.status == common.STATUS_SUCCESS


async def test_failed(
        stq_runner,
        pgsql,
        stq,
        bank_core_current_account_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_application(
        pgsql, status=common.STATUS_CORE_BANKING,
    )
    bank_core_current_account_mock.response = {
        'status': common.STATUS_FAILED,
        'request_id': common.CORE_REQUEST_ID,
        'errors': [
            {'code': '0', 'message': '1'},
            {'code': '2', 'message': '3'},
        ],
    }
    await stq_runner.bank_applications_product_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=False,
    )
    assert not stq.bank_applications_product_status_polling.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls
    application = db_helpers.select_application(pgsql, application_id)
    assert application.status == common.STATUS_FAILED
    assert application.reason == '0:1;2:3;'


async def test_application_not_found(
        stq_runner, stq, bank_core_current_account_mock, taxi_processing_mock,
):
    await stq_runner.bank_applications_product_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes('d6646547-0c90-4cf2-9b54-92a3a88d1bc7'),
        expect_fail=True,
    )
    assert not bank_core_current_account_mock.request_check_handler.has_calls
    assert not stq.bank_applications_product_status_polling.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls


async def test_core_500(
        stq_runner,
        pgsql,
        stq,
        bank_core_current_account_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_application(
        pgsql, status=common.STATUS_CORE_BANKING,
    )
    bank_core_current_account_mock.http_status_code = 500
    await stq_runner.bank_applications_product_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=True,
    )
    assert (
        bank_core_current_account_mock.request_check_handler.times_called == 2
    )
    assert not stq.bank_applications_product_status_polling.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls
