import json

import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


def default_form():
    result_form = {
        'last_name': common.LAST_NAME,
        'first_name': common.FIRST_NAME,
        'middle_name': common.MIDDLE_NAME,
        'passport_number': common.PASSPORT_NUMBER,
        'birthday': '1994-11-15',
        'snils': '12345678901',
    }
    return json.dumps(result_form)


def get_attributes(application_id, request_id='some_core_request_id'):
    result = {
        'application_id': application_id,
        'buid': common.DEFAULT_YANDEX_BUID,
        'idempotency_token': common.DEFAULT_IDEMPOTENCY_TOKEN,
    }
    if request_id is not None:
        result['request_id'] = request_id
    return result


def get_old_attributes(application_id, request_id='some_core_request_id'):
    result = {
        'application_id': application_id,
        'buid': common.DEFAULT_YANDEX_BUID,
        'idempotency_token': common.DEFAULT_IDEMPOTENCY_TOKEN,
    }
    if request_id is not None:
        result['request_id'] = request_id
    return result


def get_empty_attributes(application_id, request_id='some_core_request_id'):
    result = {
        'application_id': application_id,
        'buid': common.DEFAULT_YANDEX_BUID,
        'idempotency_token': common.DEFAULT_IDEMPOTENCY_TOKEN,
    }
    if request_id is not None:
        result['request_id'] = request_id
    return result


async def test_simplified_stq_task_pending(
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=default_form(),
        prenormalized_form=default_form(),
        agreement_version=2,
    )

    await stq_runner.bank_applications_simplified_status_polling.call(
        task_id='stq_task_id', kwargs=get_attributes(application_id),
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert not taxi_processing_mock.create_event_handler.has_calls
    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'PROCESSING'


async def test_simplified_stq_task_failed(
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=default_form(),
        prenormalized_form=default_form(),
        agreement_version=2,
        status=common.STATUS_CORE_BANKING,
    )

    bank_core_client_mock.set_request_status(
        'FAILED', [{'code': 'SRL-0003', 'message': 'unknown'}],
    )
    await stq_runner.bank_applications_simplified_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=False,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    application = db_helpers.get_simpl_id_app(pgsql, application_id)
    assert application.status == 'FAILED'
    assert application.reason == 'SRL-0003:unknown;'


async def test_simplified_stq_task_success(
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=default_form(),
        prenormalized_form=default_form(),
        agreement_version=2,
        status=common.STATUS_CORE_BANKING,
    )

    bank_core_client_mock.set_request_status('SUCCESS')
    await stq_runner.bank_applications_simplified_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=False,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'SUCCESS'


async def test_simplified_stq_task_success_old(
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=default_form(),
        prenormalized_form=default_form(),
        agreement_version=2,
    )

    bank_core_client_mock.set_request_status('SUCCESS')
    await stq_runner.bank_applications_simplified_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_old_attributes(application_id),
        expect_fail=False,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'SUCCESS'


async def test_simplified_stq_task_success_empty(
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=default_form(),
        prenormalized_form=default_form(),
        agreement_version=2,
    )

    bank_core_client_mock.set_request_status('SUCCESS')
    await stq_runner.bank_applications_simplified_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_empty_attributes(application_id),
        expect_fail=False,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'SUCCESS'


async def test_simplified_stq_task_core_request_id_not_found(
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=default_form(),
        prenormalized_form=default_form(),
        agreement_version=2,
    )

    await stq_runner.bank_applications_simplified_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id, request_id=None),
        expect_fail=True,
    )

    assert not bank_core_client_mock.client_request_check_handler.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls


@pytest.mark.parametrize(
    'core_client_error_code, times_tries', [(400, 1), (404, 1), (500, 2)],
)
async def test_simplified_stq_core_client_error(
        stq_runner,
        bank_core_client_mock,
        pgsql,
        core_client_error_code,
        taxi_processing_mock,
        times_tries,
):
    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=default_form(),
        prenormalized_form=default_form(),
        agreement_version=2,
    )

    bank_core_client_mock.set_http_status_code(core_client_error_code)
    await stq_runner.bank_applications_simplified_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=True,
    )
    assert (
        bank_core_client_mock.client_request_check_handler.times_called
        == times_tries
    )
    assert not taxi_processing_mock.create_event_handler.has_calls
