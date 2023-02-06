import datetime

import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers

WRONG_APPLICATION_ID = '7948e3a9-0000-0000-1111-9e4264d27a02'

APPLICATION_ID_1 = '7948e3a9-623c-4524-1111-9e4264d27a01'
APPLICATION_ID_2 = '7948e3a9-623c-4524-1111-9e4264d27a02'
APPLICATION_ID_3 = '7948e3a9-623c-4524-1111-9e4264d27a03'
APPLICATION_ID_4 = '7948e3a9-623c-4524-1111-9e4264d27a04'
APPLICATION_ID_5 = '7948e3a9-623c-4524-1111-9e4264d27a05'
APPLICATION_ID_6 = '7948e3a9-623c-4524-1111-9e4264d27a06'
APPLICATION_ID_7 = '7948e3a9-623c-4524-1111-9e4264d27a07'

CODE = '1234'
WRONG_CODE = '1235'
LIMIT_CODE = '1236'

WRONG_TOKEN = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJzdWIiOiJzdXBwb3J0LWFiYy11.'
)

MOCK_NOW = '2021-09-28T19:31:00+00:00'


@pytest.fixture(name='bank_authorization_test')
def _bank_authorization_test(mockserver, mocked_time):
    class Context:
        def __init__(self):
            self.create_track_handler = None
            self.send_code_handler = None
            self.verify_code_handler = None
            self.http_status_code = 200
            self.response_create_track = {'track_id': 'default_track_id'}

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_response_create_track(self, new_response):
            self.response_create_track = new_response

    context = Context()

    @mockserver.json_handler(
        '/bank-authorization/authorization-internal/v1/create_track',
    )
    async def _create_track_handler(request):
        return {'track_id': request.headers['X-Idempotency-Token'] + '-track'}

    @mockserver.json_handler(
        '/bank-authorization/authorization-internal/v1/send_code',
    )
    async def _send_code_handler(request):
        if context.http_status_code != 200:
            return mockserver.make_response(status=context.http_status_code)
        return mockserver.make_response(
            json={'retry_interval': 30, 'status': 'OK'}, status=200,
        )

    @mockserver.json_handler(
        '/bank-authorization/authorization-internal/v1/verify_code',
    )
    async def _verify_code_handler(request):

        if request.json['code'] == CODE:
            return mockserver.make_response(
                json={
                    'verification_result': 'OK',
                    'ok_data': {'verification_token': 'token'},
                },
                status=200,
            )
        if request.json['code'] == LIMIT_CODE:
            return mockserver.make_response(
                json={
                    'verification_result': 'FAIL',
                    'fail_data': {
                        'result_code': 'NO_ATTEMPTS_LEFT',
                        'attempts_left': 0,
                    },
                },
                status=200,
            )
        if request.json['code'] == WRONG_CODE:
            return mockserver.make_response(
                json={
                    'verification_result': 'FAIL',
                    'fail_data': {
                        'result_code': 'CODE_MISMATCH',
                        'attempts_left': 2,
                    },
                },
                status=200,
            )

    context.create_track_handler = _create_track_handler
    context.send_code_handler = _send_code_handler
    context.verify_code_handler = _verify_code_handler

    return context


def check_application(pgsql, application_id, status):
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        """SELECT status, initiator FROM bank_applications.change_phone_applications
         WHERE application_id = %s""",
        [application_id],
    )
    records = cursor.fetchall()
    assert records[0][0] == status
    assert records[0][1]['initiator_id'] == 'support-abc'
    assert len(records) == 1


async def test_change_phone_send_sms_old_phone_ok(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        pgsql,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/send_code_old_phone',
        headers=headers,
        json={'application_id': APPLICATION_ID_1},
    )

    assert response.status_code == 200
    check_application(
        pgsql,
        application_id=APPLICATION_ID_1,
        status='SMS_CODE_SENT_OLD_PHONE',
    )
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert bank_authorization_test.create_track_handler.times_called == 1
    assert bank_authorization_test.send_code_handler.times_called == 1


@pytest.mark.parametrize(
    'application_id', [APPLICATION_ID_5, APPLICATION_ID_6],
)
async def test_change_phone_send_sms_new_phone_ok(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        bank_userinfo_mock,
        pgsql,
        application_id,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/send_code_new_phone',
        headers=headers,
        json={'application_id': application_id},
    )

    assert response.status_code == 200
    check_application(
        pgsql, application_id=application_id, status='SMS_CODE_SENT_NEW_PHONE',
    )
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert bank_authorization_test.create_track_handler.times_called == 1
    assert bank_authorization_test.send_code_handler.times_called == 1
    assert bank_userinfo_mock.get_phone_by_phone_id_handler.times_called == 1


@pytest.mark.parametrize(
    'handle',
    [
        '/applications-support/v1/change_phone_number/send_code_old_phone',
        '/applications-support/v1/change_phone_number/send_code_new_phone',
    ],
)
async def test_change_phone_send_sms_old_phone_wrong_application_id(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        pgsql,
        handle,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        handle, headers=headers, json={'application_id': WRONG_APPLICATION_ID},
    )

    assert response.status_code == 404
    assert access_control_mock.apply_policies_handler.times_called == 1


@pytest.mark.parametrize(
    'handle',
    [
        '/applications-support/v1/change_phone_number/send_code_old_phone',
        '/applications-support/v1/change_phone_number/send_code_new_phone',
    ],
)
async def test_change_phone_send_sms_old_phone_finished_application(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        pgsql,
        handle,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        handle, headers=headers, json={'application_id': APPLICATION_ID_2},
    )

    assert response.status_code == 409
    assert access_control_mock.apply_policies_handler.times_called == 1


@pytest.mark.parametrize(
    'handle',
    [
        '/applications-support/v1/change_phone_number/send_code_old_phone',
        '/applications-support/v1/change_phone_number/send_code_new_phone',
    ],
)
async def test_change_phone_send_sms_old_phone_access_failed(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        pgsql,
        handle,
):
    headers = common.get_support_headers(token=WRONG_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        handle, headers=headers, json={'application_id': APPLICATION_ID_1},
    )

    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


@pytest.mark.parametrize(
    'handle, application_id',
    [
        (
            '/applications-support/v1/change_phone_number/send_code_old_phone',
            APPLICATION_ID_1,
        ),
        (
            '/applications-support/v1/change_phone_number/send_code_new_phone',
            APPLICATION_ID_5,
        ),
    ],
)
async def test_change_phone_send_sms_old_phone_send_error(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        bank_userinfo_mock,
        pgsql,
        handle,
        application_id,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    bank_authorization_test.set_http_status_code(429)
    response = await taxi_bank_applications.post(
        handle, headers=headers, json={'application_id': application_id},
    )

    assert response.status_code == 500
    assert access_control_mock.apply_policies_handler.times_called == 1


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    BANK_APPLICATIONS_POLLING_CHANGE_NUMBER_TIMELIMIT_QUARANTINE_INTERVAL=168,
)
@pytest.mark.parametrize(
    'validation_type, expected_status',
    [('REGULAR', 'CREATED'), ('LOSTWITHCARANTINE', 'FAILED')],
)
async def test_change_phone_quarantine_ok(
        taxi_bank_applications,
        access_control_mock,
        pgsql,
        stq,
        stq_runner,
        validation_type,
        expected_status,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/skip_check_old_number',
        headers=headers,
        json={'application_id': APPLICATION_ID_1, 'reason': 'this is the way'},
    )

    assert response.status_code == 200
    check_application(
        pgsql, application_id=APPLICATION_ID_1, status='QUARANTINE',
    )
    assert access_control_mock.apply_policies_handler.times_called == 1

    assert stq.bank_applications_change_number_timelimit_polling.next_call()[
        'eta'
    ] == datetime.datetime(2021, 10, 5, 19, 31)

    await stq_runner.bank_applications_change_number_timelimit_polling.call(
        task_id='stq_task_id',
        kwargs={
            'application_id': APPLICATION_ID_1,
            'validation_type': validation_type,
        },
        expect_fail=False,
    )

    application = db_helpers.get_application(pgsql, APPLICATION_ID_1)
    assert application.status == expected_status


async def test_change_phone_quarantine_wrong_application_id(
        taxi_bank_applications, access_control_mock, pgsql,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/skip_check_old_number',
        headers=headers,
        json={
            'application_id': '7948e3a9-0000-0000-1111-9e4264d27a02',
            'reason': 'this is the way',
        },
    )

    assert response.status_code == 404
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_quarantine_finished_application(
        taxi_bank_applications, access_control_mock, pgsql,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/skip_check_old_number',
        headers=headers,
        json={'application_id': APPLICATION_ID_2, 'reason': 'this is the way'},
    )

    assert response.status_code == 409
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_quarantine_access_failed(
        taxi_bank_applications, access_control_mock, pgsql,
):
    headers = common.get_support_headers(token=WRONG_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/skip_check_old_number',
        headers=headers,
        json={'application_id': APPLICATION_ID_1, 'reason': 'this is the way'},
    )

    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_verify_code_wrong_status(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        pgsql,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/verify_code',
        headers=headers,
        json={'application_id': APPLICATION_ID_1, 'code': CODE},
    )

    assert response.status_code == 409
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_verify_code_wrong_token(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        pgsql,
):
    headers = common.get_support_headers(token=WRONG_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/verify_code',
        headers=headers,
        json={'application_id': APPLICATION_ID_1, 'code': CODE},
    )

    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_verify_code_ok_old(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        pgsql,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/verify_code',
        headers=headers,
        json={'application_id': APPLICATION_ID_3, 'code': CODE},
    )

    assert response.status_code == 200
    check_application(
        pgsql, application_id=APPLICATION_ID_3, status='SUBMIT_OLD_PHONE',
    )
    assert response.json() == {
        'status': 'SUBMIT_OLD_PHONE',
        'verification_result': 'OK',
    }
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_verify_code_ok_new(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        pgsql,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/verify_code',
        headers=headers,
        json={'application_id': APPLICATION_ID_4, 'code': CODE},
    )

    assert response.status_code == 200
    check_application(
        pgsql, application_id=APPLICATION_ID_4, status='SUBMIT_NEW_PHONE',
    )
    assert response.json() == {
        'status': 'SUBMIT_NEW_PHONE',
        'verification_result': 'OK',
    }
    assert access_control_mock.apply_policies_handler.times_called == 1


@pytest.mark.parametrize(
    'expected_status, status, answer',
    [
        (
            'SMS_CODE_SENT_NEW_PHONE',
            200,
            {'status': 'SUBMIT_NEW_PHONE', 'verification_result': 'OK'},
        ),
        (
            'SMS_CODE_SENT_OLD_PHONE',
            409,
            {
                'code': 'BadRequest',
                'message': 'Application in SMS_CODE_SENT_NEW_PHONE status',
            },
        ),
    ],
)
async def test_change_phone_verify_code_ok_new_expected_status(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        pgsql,
        expected_status,
        answer,
        status,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/verify_code',
        headers=headers,
        json={
            'application_id': APPLICATION_ID_4,
            'code': CODE,
            'expected_status': expected_status,
        },
    )

    assert response.status_code == status
    assert response.json() == answer
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_verify_code_wrong_code(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        pgsql,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/verify_code',
        headers=headers,
        json={'application_id': APPLICATION_ID_3, 'code': WRONG_CODE},
    )

    assert response.status_code == 200
    assert response.json() == {
        'fail_data': {'attempts_left': 2, 'result_code': 'CODE_MISMATCH'},
        'status': 'SMS_CODE_SENT_OLD_PHONE',
        'verification_result': 'FAIL',
    }
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_verify_code_limit_code(
        bank_authorization_test,
        taxi_bank_applications,
        access_control_mock,
        pgsql,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/verify_code',
        headers=headers,
        json={'application_id': APPLICATION_ID_3, 'code': LIMIT_CODE},
    )

    assert response.status_code == 200
    assert response.json() == {
        'fail_data': {'attempts_left': 0, 'result_code': 'NO_ATTEMPTS_LEFT'},
        'status': 'SMS_CODE_SENT_OLD_PHONE',
        'verification_result': 'FAIL',
    }
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_start_procaas_ok(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/start_procaas',
        headers=common.get_support_headers(),
        json={'application_id': APPLICATION_ID_7},
    )
    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 2
    assert access_control_mock.apply_policies_handler.times_called == 1
    check_application(pgsql, APPLICATION_ID_7, 'PROCESSING')


async def test_change_phone_start_procaas_processing_returns_500(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    taxi_processing_mock.http_status_code = 500
    taxi_processing_mock.response = {'code': '500', 'message': 'error'}
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/start_procaas',
        headers=common.get_support_headers(),
        json={'application_id': APPLICATION_ID_7},
    )
    assert response.status_code == 500
    assert taxi_processing_mock.create_event_handler.times_called == 3
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_start_procaas_access_deny(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/start_procaas',
        headers=common.get_support_headers(''),
        json={'application_id': APPLICATION_ID_7},
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_start_procaas_not_found(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    application_id = '99999999-1111-1111-1111-111111111111'
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/start_procaas',
        headers=common.get_support_headers(),
        json={'application_id': application_id},
    )
    assert response.status_code == 404
    assert not taxi_processing_mock.create_event_handler.has_calls
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_start_procaas_app_in_invalid_status(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/start_procaas',
        headers=common.get_support_headers(),
        json={'application_id': APPLICATION_ID_1},
    )
    assert response.status_code == 409
    assert not taxi_processing_mock.create_event_handler.has_calls
    assert access_control_mock.apply_policies_handler.times_called == 1


@pytest.mark.parametrize(
    'application_id, validation_type, expected_status',
    [
        (APPLICATION_ID_1, 'REGULAR', 'FAILED'),
        (APPLICATION_ID_1, 'LOSTWITHCARANTINE', 'CREATED'),
    ],
)
async def test_change_number_stq_task_timelimit_success(
        mockserver,
        stq_runner,
        pgsql,
        application_id,
        validation_type,
        expected_status,
):
    await stq_runner.bank_applications_change_number_timelimit_polling.call(
        task_id='stq_task_id',
        kwargs={
            'application_id': application_id,
            'validation_type': validation_type,
        },
        expect_fail=False,
    )

    application = db_helpers.get_application(pgsql, APPLICATION_ID_1)
    assert application.status == expected_status


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    BANK_APPLICATIONS_POLLING_CHANGE_NUMBER_TIMELIMIT_INTERVAL=24,
)
async def test_change_phone_create_application_stq_work(
        taxi_bank_applications,
        access_control_mock,
        bank_userinfo_mock,
        pgsql,
        mocked_time,
        stq,
):
    # bank_forms_mock.set_http_status_code(200)
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/create_application',
        headers=headers,
        json={
            'form': {
                'buid': '22222222-d4d1-43c1-aadb-cabd06674ea6',
                'new_phone': '+71234577890',
                'validation_type': 'REGULAR',
                'chatterbox_id': 'FTB-2115',
            },
        },
    )

    assert response.status_code == 200
    assert (
        stq.bank_applications_change_number_timelimit_polling.times_called == 1
    )
    assert stq.bank_applications_change_number_timelimit_polling.next_call()[
        'eta'
    ] == datetime.datetime(2021, 9, 29, 19, 31)
