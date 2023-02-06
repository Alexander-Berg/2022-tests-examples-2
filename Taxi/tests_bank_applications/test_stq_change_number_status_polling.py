import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers

APPLICATION_ID_1 = '7948e3a9-623c-4524-1111-9e4264d27a01'
APPLICATION_ID_2 = '7948e3a9-623c-4524-1111-9e4264d27a02'


def get_attributes(application_id, request_id='some_core_request_id'):
    result = {
        'application_id': application_id,
        'buid': common.DEFAULT_YANDEX_BUID,
        'yuid': common.DEFAULT_YANDEX_UID,
        'client_ip': common.SOME_IP,
        'idempotency_token': common.DEFAULT_IDEMPOTENCY_TOKEN,
    }
    if request_id is not None:
        result['request_id'] = request_id

    return result


async def test_change_number_stq_task_pending(
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):

    await stq_runner.bank_applications_change_number_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(APPLICATION_ID_1),
        expect_fail=False,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert not taxi_processing_mock.create_event_handler.has_calls
    application = db_helpers.get_application(pgsql, APPLICATION_ID_1)
    assert application.status == 'PROCESSING'


async def test_change_number_stq_task_success(
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    bank_core_client_mock.set_request_status('SUCCESS')
    await stq_runner.bank_applications_change_number_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(APPLICATION_ID_1),
        expect_fail=False,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    application = db_helpers.get_application(pgsql, APPLICATION_ID_1)
    assert application.status == 'PROCESSING'
    assert len(taxi_processing_mock.payloads) == 1
    assert taxi_processing_mock.payloads[0][1] == {
        'buid': common.DEFAULT_YANDEX_BUID,
        'new_phone_id': 'phone_id_2',
        'kind': 'update',
        'type': 'change_number_result',
    }


async def test_change_number_stq_task_failed(
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    bank_core_client_mock.set_request_status('FAILED')
    await stq_runner.bank_applications_change_number_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(APPLICATION_ID_1),
        expect_fail=False,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    application = db_helpers.get_application(pgsql, APPLICATION_ID_1)
    assert application.status == 'FAILED'
    assert application.reason == 'PROCESSING_FAILED'
    assert len(taxi_processing_mock.payloads) == 1
    assert taxi_processing_mock.payloads[0][1] == {
        'buid': common.DEFAULT_YANDEX_BUID,
        'new_phone_id': 'phone_id_1',
        'old_phone_id': 'phone_id_2',
        'yuid': '111111111',
        'kind': 'update',
        'core_banking_request_id': 'some_core_request_id',
        'core_banking_status': 'FAILED',
        'type': 'change_number_failed',
        'client_ip': common.SOME_IP,
    }


async def test_change_number_stq_task_core_request_id_not_found(
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    await stq_runner.bank_applications_change_number_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(APPLICATION_ID_2, request_id=None),
        expect_fail=True,
    )

    assert not bank_core_client_mock.client_request_check_handler.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls


@pytest.mark.parametrize(
    'core_client_error_code, times_tries', [(400, 1), (404, 1), (500, 2)],
)
async def test_change_number_stq_core_client_error(
        stq_runner,
        pgsql,
        bank_core_client_mock,
        core_client_error_code,
        taxi_processing_mock,
        times_tries,
):
    bank_core_client_mock.set_http_status_code(core_client_error_code)
    await stq_runner.bank_applications_change_number_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(APPLICATION_ID_1),
        expect_fail=True,
    )
    assert (
        bank_core_client_mock.client_request_check_handler.times_called
        == times_tries
    )
    assert not taxi_processing_mock.create_event_handler.has_calls


@pytest.mark.config(
    BANK_APPLICATIONS_POLLING_CHANGE_NUMBER_MAX_PENDING_TIMES=0,
)
async def test_change_number_stq_task_max_pending_times(
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    await stq_runner.bank_applications_change_number_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(APPLICATION_ID_1),
        reschedule_counter=1,
        expect_fail=True,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert not taxi_processing_mock.create_event_handler.times_called
    application = db_helpers.get_application(pgsql, APPLICATION_ID_1)
    assert application.status == 'PROCESSING'
