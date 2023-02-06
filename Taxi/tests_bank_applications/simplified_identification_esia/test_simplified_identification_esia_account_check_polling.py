import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


def get_attributes(application_id, buid=common.DEFAULT_YANDEX_BUID):
    result = {
        'application_id': application_id,
        'buid': buid,
        'idempotency_token': common.DEFAULT_IDEMPOTENCY_TOKEN,
        'session_id': common.DEFAULT_YABANK_SESSION_UUID,
        'request_id': '1234',
    }
    return result


def common_checks(
        pgsql, application_id, status, hist_not_empty=False, reason=None,
):
    applications = db_helpers.select_simpl_esia_apps(
        pgsql, common.DEFAULT_YANDEX_BUID,
    )
    assert len(applications) == 1
    assert applications[0].application_id == application_id
    assert applications[0].status == status

    application_history = db_helpers.select_simpl_esia_apps_hist(
        pgsql, application_id,
    )
    if hist_not_empty:
        assert len(application_history) == 1
        assert application_history[0].status == status
    else:
        assert not application_history

    if reason is not None:
        assert applications[0].reason == reason


async def test_simplified_identification_esia_stq_task_pending(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        core_current_account_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CORE_BANKING,
        simpl_esia_status=common.STATUS_CORE_BANKING,
    )

    await stq_runner.bank_applications_simplified_identification_account_check_polling.call(  # noqa
        task_id='stq_task_id', kwargs=get_attributes(application_id),
    )

    assert core_current_account_mock.client_check_handler.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls

    common_checks(pgsql, application_id, common.STATUS_CORE_BANKING)


async def test_simplified_identification_esia_stq_task_success(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        core_current_account_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CORE_BANKING,
        simpl_esia_status=common.STATUS_CORE_BANKING,
    )

    core_current_account_mock.set_request_status('SUCCESS')

    await stq_runner.bank_applications_simplified_identification_account_check_polling.call(  # noqa
        task_id='stq_task_id', kwargs=get_attributes(application_id),
    )

    assert core_current_account_mock.client_check_handler.has_calls
    assert taxi_processing_mock.create_event_handler.has_calls

    common_checks(
        pgsql, application_id, common.STATUS_SUCCESS, hist_not_empty=True,
    )


async def test_simplified_identification_esia_stq_task_failed(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        core_current_account_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CORE_BANKING,
        simpl_esia_status=common.STATUS_CORE_BANKING,
    )

    core_current_account_mock.set_request_status('FAILED')
    core_current_account_mock.set_response_errors(
        [{'code': '1', 'message': '11'}, {'code': '2', 'message': '22'}],
    )

    await stq_runner.bank_applications_simplified_identification_account_check_polling.call(  # noqa
        task_id='stq_task_id', kwargs=get_attributes(application_id),
    )

    assert core_current_account_mock.client_check_handler.has_calls
    assert taxi_processing_mock.create_event_handler.has_calls

    common_checks(
        pgsql,
        application_id,
        common.STATUS_FAILED,
        hist_not_empty=True,
        reason='1:11;2:22;',
    )


async def test_simplified_identification_esia_stq_task_app_not_found(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        core_current_account_mock,
        taxi_processing_mock,
):
    core_current_account_mock.set_request_status('SUCCESS')

    await stq_runner.bank_applications_simplified_identification_account_check_polling.call(  # noqa
        task_id='stq_task_id',
        kwargs=get_attributes('11111111-1111-1111-1111-111111111111'),
        expect_fail=True,
    )

    assert core_current_account_mock.client_check_handler.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls


@pytest.mark.parametrize('core_account_status_code', [400, 404, 500])
async def test_simplified_identification_esia_stq_task_core_account_error(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        core_current_account_mock,
        taxi_processing_mock,
        core_account_status_code,
):
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CORE_BANKING,
        simpl_esia_status=common.STATUS_CORE_BANKING,
    )

    core_current_account_mock.set_http_status_code(core_account_status_code)

    await stq_runner.bank_applications_simplified_identification_account_check_polling.call(  # noqa
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=True,
    )

    assert core_current_account_mock.client_check_handler.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls

    common_checks(pgsql, application_id, common.STATUS_CORE_BANKING)


@pytest.mark.parametrize('request_status', ['SUCCESS', 'FAILED'])
async def test_simplified_identification_esia_stq_task_processing_error(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        core_current_account_mock,
        taxi_processing_mock,
        request_status,
):
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CORE_BANKING,
        simpl_esia_status=common.STATUS_CORE_BANKING,
    )

    core_current_account_mock.set_request_status(request_status)
    taxi_processing_mock.set_http_status_code(500)

    await stq_runner.bank_applications_simplified_identification_account_check_polling.call(  # noqa
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=True,
    )

    assert core_current_account_mock.client_check_handler.has_calls
    assert taxi_processing_mock.create_event_handler.has_calls

    common_checks(pgsql, application_id, request_status, hist_not_empty=True)


async def test_simplified_identification_esia_stq_task_bad_buid(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        core_current_account_mock,
        taxi_processing_mock,
):
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CORE_BANKING,
        simpl_esia_status=common.STATUS_CORE_BANKING,
    )

    core_current_account_mock.set_request_status('SUCCESS')

    await stq_runner.bank_applications_simplified_identification_account_check_polling.call(  # noqa
        task_id='stq_task_id',
        kwargs=get_attributes(application_id, buid=''),
        expect_fail=True,
    )

    assert core_current_account_mock.client_check_handler.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls

    common_checks(pgsql, application_id, common.STATUS_CORE_BANKING)
