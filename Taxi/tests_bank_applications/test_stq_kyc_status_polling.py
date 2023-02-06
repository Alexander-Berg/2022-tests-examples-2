import json

import pytest

from tests_bank_applications import common
from tests_bank_applications import kyc_db_helpers


def get_attributes(application_id):
    result = {
        'application_id': application_id,
        'buid': common.DEFAULT_YANDEX_BUID,
        'idempotency_token': common.DEFAULT_IDEMPOTENCY_TOKEN,
        'request_id': 'some_core_request_id',
    }
    return result


async def test_kyc_stq_task_pending(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        testpoint,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    await taxi_bank_applications.enable_testpoints()
    form = common.get_kyc_standard_form()
    form['id_record_abs'] = 'id_record_abs_1'
    application_id = kyc_db_helpers.insert_kyc_application(
        pgsql, submitted_form=json.dumps(form),
    )

    @testpoint('tp_kafka-producer-kyc-status')
    def data_publish(data):
        pass

    await stq_runner.bank_applications_kyc_status_polling.call(
        task_id='stq_task_id', kwargs=get_attributes(application_id),
    )

    assert not data_publish.has_calls
    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert not taxi_processing_mock.create_event_handler.has_calls
    application = kyc_db_helpers.get_kyc_id_app(pgsql, application_id)
    assert application.status == 'PROCESSING'


async def test_kyc_stq_task_failed(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        testpoint,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    form = common.get_kyc_standard_form()
    form['id_record_abs'] = 'id_record_abs_1'
    application_id = kyc_db_helpers.insert_kyc_application(
        pgsql,
        submitted_form=json.dumps(form),
        status=common.STATUS_CORE_BANKING,
    )

    fail_reason_from_ftc = 'SRL-0003:unknown'

    @testpoint('tp_kafka-producer-kyc-status')
    def data_publish(data):
        assert json.loads(data['message']) == {
            'id_record_abs': 'id_record_abs_1',
            'result': 0,
            'result_text': fail_reason_from_ftc,
            'application_id': application_id,
        }

    bank_core_client_mock.set_request_status(
        'FAILED', [{'code': 'SRL-0003', 'message': 'unknown'}],
    )
    await stq_runner.bank_applications_kyc_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=False,
    )
    await taxi_bank_applications.enable_testpoints()
    await data_publish.wait_call()

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    application = kyc_db_helpers.get_kyc_id_app(pgsql, application_id)
    assert application.status == 'FAILED'
    assert application.reason == fail_reason_from_ftc


async def test_kyc_stq_task_success(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        testpoint,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    form = common.get_kyc_standard_form()
    form['id_record_abs'] = 'id_record_abs_1'
    application_id = kyc_db_helpers.insert_kyc_application(
        pgsql,
        submitted_form=json.dumps(form),
        status=common.STATUS_CORE_BANKING,
    )

    @testpoint('tp_kafka-producer-kyc-status')
    def data_publish(data):
        assert json.loads(data['message']) == {
            'id_record_abs': 'id_record_abs_1',
            'result': 1,
            'result_text': '',
            'application_id': application_id,
        }

    bank_core_client_mock.set_request_status('SUCCESS')
    await stq_runner.bank_applications_kyc_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=False,
    )
    await taxi_bank_applications.enable_testpoints()
    await data_publish.wait_call()

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    application = kyc_db_helpers.get_kyc_id_app(pgsql, application_id)
    assert application.status == 'SUCCESS'


@pytest.mark.parametrize(
    'core_client_error_code, times_tries', [(400, 1), (404, 1), (500, 2)],
)
async def test_kyc_stq_core_client_error(
        taxi_bank_applications,
        stq_runner,
        testpoint,
        bank_core_client_mock,
        pgsql,
        core_client_error_code,
        taxi_processing_mock,
        times_tries,
):
    await taxi_bank_applications.enable_testpoints()
    application_id = kyc_db_helpers.insert_kyc_application(
        pgsql,
        submitted_form=json.dumps(common.get_kyc_standard_form()),
        status=common.STATUS_CORE_BANKING,
    )

    @testpoint('kafka_publish')
    def data_publish(data):
        pass

    bank_core_client_mock.set_http_status_code(core_client_error_code)
    await stq_runner.bank_applications_kyc_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=True,
    )
    assert not data_publish.has_calls
    assert (
        bank_core_client_mock.client_request_check_handler.times_called
        == times_tries
    )
    assert not taxi_processing_mock.create_event_handler.has_calls
