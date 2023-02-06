import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


def get_attributes(application_id):
    result = {
        'application_id': application_id,
        'buid': common.DEFAULT_YANDEX_BUID,
        'idempotency_token': common.DEFAULT_IDEMPOTENCY_TOKEN,
        'ip_address': '123.123.123.123',
        'session_id': common.DEFAULT_YABANK_SESSION_UUID,
        'data_revision': 1000_000_000_000,
    }
    return result


def common_checks(
        pgsql,
        application_id,
        status=common.STATUS_CORE_BANKING,
        hist_not_empty=False,
        data_revision=None,
):
    applications = db_helpers.select_simpl_esia_apps(
        pgsql, common.DEFAULT_YANDEX_BUID,
    )
    assert len(applications) == 1
    assert applications[0].application_id == application_id
    assert applications[0].status == status
    assert applications[0].data_revision == data_revision

    application_history = db_helpers.select_simpl_esia_apps_hist(
        pgsql, application_id,
    )
    if hist_not_empty:
        assert len(application_history) == 1
        assert application_history[0].application_id == application_id
        assert application_history[0].data_revision == data_revision
    else:
        assert not application_history


@pytest.mark.parametrize('status', [None, 'PENDING'])
@pytest.mark.parametrize(
    'auth_level', ['ANONYMOUS', 'IDENTIFIED', 'KYC_EDS', 'KYC'],
)
async def test_simplified_identification_esia_stq_task_pending(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
        status,
        auth_level,
):
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CORE_BANKING,
        simpl_esia_status=common.STATUS_CORE_BANKING,
    )

    bank_core_client_mock.ensure_pending = True
    bank_core_client_mock.set_auth_level(auth_level)
    bank_core_client_mock.set_request_status(status)

    await stq_runner.bank_applications_simplified_identification_esia_status_polling.call(  # noqa
        task_id='stq_task_id', kwargs=get_attributes(application_id),
    )

    assert bank_core_client_mock.client_ensure_handler.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls

    common_checks(pgsql, application_id)


@pytest.mark.parametrize('status', [None, 'ALLOW'])
@pytest.mark.parametrize('auth_level', ['KYC', 'KYC_EDS'])
async def test_simplified_identification_esia_stq_task_success(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
        status,
        auth_level,
):
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CORE_BANKING,
        simpl_esia_status=common.STATUS_CORE_BANKING,
    )

    bank_core_client_mock.ensure_success = True
    bank_core_client_mock.set_request_status(status)
    bank_core_client_mock.set_auth_level(auth_level)

    await stq_runner.bank_applications_simplified_identification_esia_status_polling.call(  # noqa
        task_id='stq_task_id', kwargs=get_attributes(application_id),
    )

    assert bank_core_client_mock.client_ensure_handler.has_calls
    assert taxi_processing_mock.create_event_handler.has_calls

    common_checks(pgsql, application_id, hist_not_empty=True, data_revision=2)


@pytest.mark.parametrize('status', [None, 'DENY'])
@pytest.mark.parametrize('auth_level', ['IDENTIFIED', 'ANONYMOUS'])
async def test_simplified_identification_esia_stq_task_failed(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
        status,
        auth_level,
):
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CORE_BANKING,
        simpl_esia_status=common.STATUS_CORE_BANKING,
    )

    bank_core_client_mock.ensure_failed = True
    bank_core_client_mock.set_auth_level(auth_level)
    bank_core_client_mock.set_request_status(status)

    await stq_runner.bank_applications_simplified_identification_esia_status_polling.call(  # noqa
        task_id='stq_task_id', kwargs=get_attributes(application_id),
    )

    assert bank_core_client_mock.client_ensure_handler.has_calls
    assert taxi_processing_mock.create_event_handler.has_calls

    common_checks(
        pgsql, application_id, common.STATUS_FAILED, hist_not_empty=True,
    )


async def test_simplified_identification_esia_stq_task_application_not_found(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
):
    application_id = '11111111-1111-1111-1111-111111111111'

    bank_core_client_mock.ensure_success = True
    bank_core_client_mock.set_auth_level('KYC_EDS')

    await stq_runner.bank_applications_simplified_identification_esia_status_polling.call(  # noqa
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=True,
    )

    assert bank_core_client_mock.client_ensure_handler.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls

    applications = db_helpers.select_simpl_esia_apps(
        pgsql, common.DEFAULT_YANDEX_BUID,
    )
    assert not applications


@pytest.mark.parametrize(
    'core_client_error_code, times_tries', [(400, 1), (500, 2)],
)
async def test_simplified_identification_esia_stq_task_core_client_error(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
        core_client_error_code,
        times_tries,
):
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CORE_BANKING,
        simpl_esia_status=common.STATUS_CORE_BANKING,
    )

    bank_core_client_mock.set_http_status_code(core_client_error_code)

    await stq_runner.bank_applications_simplified_identification_esia_status_polling.call(  # noqa
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=True,
    )

    assert (
        bank_core_client_mock.client_ensure_handler.times_called == times_tries
    )
    assert not taxi_processing_mock.create_event_handler.has_calls

    common_checks(pgsql, application_id)


@pytest.mark.parametrize('task_failed', [True, False])
async def test_simplified_identification_esia_stq_task_processing_error(
        taxi_bank_applications,
        mockserver,
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
        task_failed,
):
    application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CORE_BANKING,
        simpl_esia_status=common.STATUS_CORE_BANKING,
    )

    if task_failed:
        bank_core_client_mock.ensure_failed = True
        bank_core_client_mock.set_request_status(None)
    else:
        bank_core_client_mock.set_auth_level('KYC_EDS')
        bank_core_client_mock.ensure_success = True
    taxi_processing_mock.set_http_status_code(500)

    await stq_runner.bank_applications_simplified_identification_esia_status_polling.call(  # noqa
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=True,
    )

    assert bank_core_client_mock.client_ensure_handler.has_calls
    assert taxi_processing_mock.create_event_handler.has_calls

    common_checks(
        pgsql,
        application_id,
        common.STATUS_FAILED if task_failed else common.STATUS_CORE_BANKING,
        True,
        None if task_failed else 2,
    )
