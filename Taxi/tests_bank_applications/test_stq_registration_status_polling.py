import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


def get_attributes(
        application_id,
        request_id='some_core_request_id',
        product=None,
        yuid=None,
        session_uuid=None,
):
    result = {
        'application_id': application_id,
        'buid': common.DEFAULT_YANDEX_BUID,
        'idempotency_token': common.DEFAULT_IDEMPOTENCY_TOKEN,
        'client_ip': common.SOME_IP,
    }
    if request_id is not None:
        result['request_id'] = request_id
    if product is not None:
        result['product'] = product
    if yuid is not None:
        result['yuid'] = yuid
    if session_uuid is not None:
        result['session_uuid'] = session_uuid

    return result


async def test_registration_stq_task_pending(
        stq_runner, pgsql, bank_core_client_mock, taxi_processing_mock,
):
    application_id = '7948e3a9-623c-4524-a390-9e4264d27a01'
    await stq_runner.bank_applications_registration_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=False,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert not taxi_processing_mock.create_event_handler.has_calls
    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'PROCESSING'


@pytest.mark.config(BANK_APPLICATIONS_POLLING_REGISTRATION_MAX_PENDING_TIMES=0)
async def test_registration_stq_task_max_pending_times(
        stq_runner, pgsql, bank_core_client_mock, taxi_processing_mock,
):
    application_id = '7948e3a9-623c-4524-a390-9e4264d27a01'
    await stq_runner.bank_applications_registration_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        reschedule_counter=1,
        expect_fail=True,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert not taxi_processing_mock.create_event_handler.has_calls
    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'PROCESSING'


@pytest.mark.parametrize('cleanup_enabled', [True, False])
@pytest.mark.parametrize(
    'error_message',
    [
        'SOLAR saveAgreement failed with message:'
        ' ResponseBodyContent(type=ERROR, code=SLR-0003,'
        ' message=Unexpected error '
        'occurred)',
        'SOLAR saveAgreement failed with message: '
        'ResponseBodyContent(type=TIMEOUT, code=SLR-0005, message=Message '
        'processing timeout)',
    ],
)
async def test_registration_stq_task_failed(
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
        error_message,
        stq,
        cleanup_enabled,
        taxi_config,
):
    taxi_config.set_values(
        {
            'BANK_APPLICATIONS_REGISTRATION_CLEAN_UP_AFTER_SLR_0003': (
                cleanup_enabled
            ),
        },
    )
    application_id = '7948e3a9-623c-4524-a390-9e4264d27a01'
    bank_core_client_mock.set_request_status(
        'FAILED', [{'code': 'unknown error', 'message': error_message}],
    )
    await stq_runner.bank_applications_registration_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=False,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert not taxi_processing_mock.create_event_handler.has_calls
    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'FAILED'
    assert application.reason == f'unknown error:{error_message}'
    assert stq.bank_userinfo_deactivate_user.has_calls == (
        cleanup_enabled and 'SLR-0003' in error_message
    )


@pytest.mark.parametrize(
    'product', [None, common.PRODUCT_WALLET, common.PRODUCT_PRO],
)
@pytest.mark.parametrize('yuid', [None, common.DEFAULT_YANDEX_UID])
@pytest.mark.parametrize(
    'session_uuid', [None, common.DEFAULT_YABANK_SESSION_UUID],
)
async def test_registration_stq_task_success(
        stq_runner,
        pgsql,
        bank_core_client_mock,
        taxi_processing_mock,
        product,
        yuid,
        session_uuid,
):
    application_id = '7948e3a9-623c-4524-a390-9e4264d27a01'
    bank_core_client_mock.set_request_status('SUCCESS')
    await stq_runner.bank_applications_registration_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(
            application_id,
            product=product,
            yuid=yuid,
            session_uuid=session_uuid,
        ),
        expect_fail=False,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'PROCESSING'
    assert len(taxi_processing_mock.payloads) == 1
    expected_payload = {
        'buid': common.DEFAULT_YANDEX_BUID,
        'core_banking_status': 'SUCCESS',
        'core_banking_request_id': 'some_core_request_id',
        'kind': 'update',
        'type': 'update_buid_result',
        'client_ip': common.SOME_IP,
    }
    if product is not None:
        expected_payload['product'] = product
    if yuid is not None:
        expected_payload['yuid'] = yuid
    if session_uuid is not None:
        expected_payload['session_uuid'] = session_uuid
    assert taxi_processing_mock.payloads[0][1] == expected_payload


async def test_registration_stq_task_core_request_id_not_found(
        stq_runner, bank_core_client_mock, taxi_processing_mock,
):
    application_id = '7948e3a9-623c-4524-a390-9e4264d27a02'
    await stq_runner.bank_applications_registration_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id, request_id=None),
        expect_fail=True,
    )

    assert not bank_core_client_mock.client_request_check_handler.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls


@pytest.mark.parametrize(
    'core_client_error_code, times_tries', [(400, 1), (404, 1), (500, 2)],
)
async def test_registration_stq_core_client_error(
        stq_runner,
        bank_core_client_mock,
        core_client_error_code,
        taxi_processing_mock,
        times_tries,
):
    application_id = '7948e3a9-623c-4524-a390-9e4264d27a01'
    bank_core_client_mock.set_http_status_code(core_client_error_code)
    await stq_runner.bank_applications_registration_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=True,
    )
    assert (
        bank_core_client_mock.client_request_check_handler.times_called
        == times_tries
    )
    assert not taxi_processing_mock.create_event_handler.has_calls


@pytest.mark.config(
    BANK_APPLICATIONS_REGISTRATION_CLEAN_UP_AFTER_SLR_0003=True,
)
async def test_slr_0003_registration_already_failed(
        stq_runner, pgsql, bank_core_client_mock, taxi_processing_mock, stq,
):
    application_id = '7948e3a9-623c-4524-a390-9e4264d27a01'
    db_helpers.update_application_status(pgsql, application_id, 'FAILED')
    bank_core_client_mock.set_request_status(
        'FAILED',
        [
            {
                'code': 'SOLAR_UNDEFINED_ERROR',
                'message': (
                    'SOLAR ... ResponseBodyContent(..., code=SLR-0003,... '
                ),
            },
        ],
    )
    await stq_runner.bank_applications_registration_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=False,
    )

    assert bank_core_client_mock.client_request_check_handler.times_called == 1
    assert not taxi_processing_mock.create_event_handler.has_calls
    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'FAILED'
    assert stq.bank_userinfo_deactivate_user.has_calls
    next_call = stq.bank_userinfo_deactivate_user.next_call()
    assert (
        next_call.get('id')
        == 'registration_fail_slr_0003_7948e3a9-623c-4524-a390-9e4264d27a01'
    )
    assert next_call.get('kwargs').get('reason_code') == 'SLR-0003'


async def test_registration_stq_task_failed_status_failed_both_tables(
        stq_runner, pgsql, bank_core_client_mock,
):
    application_id = '7948e3a9-623c-4524-a390-9e4264d27a01'
    bank_core_client_mock.set_request_status(
        'FAILED',
        [
            {
                'code': 'unknown error',
                'message': 'SOLAR saveAgreement failed with message:',
            },
        ],
    )
    await stq_runner.bank_applications_registration_status_polling.call(
        task_id='stq_task_id',
        kwargs=get_attributes(application_id),
        expect_fail=False,
    )

    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'FAILED'

    application_reg = db_helpers.get_application_registration(
        pgsql, application_id,
    )
    assert application_reg.status == 'FAILED'
