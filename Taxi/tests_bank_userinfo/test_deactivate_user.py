import pytest

from tests_bank_userinfo import common
from tests_bank_userinfo import utils

HANDLE_URL = '/userinfo-support/v1/deactivate_user'
BUID = 'c98504fd-de51-403c-9108-8a0aff5e8d30'
REASON = 'testing'
REMOTE_IP = '127.0.0.1'
IDEMPOTENCY_TOKEN = 'd1576bc0-2c11-4408-a084-712d8f0d7463'


def get_support_headers(token='allow', idempotency_token=None):
    headers = common.get_support_headers(
        token=token, idempotency_token=idempotency_token,
    )
    headers['X-Remote-IP'] = REMOTE_IP
    return headers


def default_stq_kwargs(buid=BUID):
    return {
        'buid': buid,
        'idempotency_token': IDEMPOTENCY_TOKEN,
        'reason': REASON,
        'x_remote_ip': REMOTE_IP,
    }


async def test_handle_ok(taxi_bank_userinfo, mockserver, stq):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/deactivate_user',
        headers=common.get_headers(
            idempotency_token=IDEMPOTENCY_TOKEN, remote_ip=REMOTE_IP,
        ),
        json={'buid': BUID, 'reason': REASON},
    )
    assert response.status_code == 200

    assert stq.bank_userinfo_deactivate_user.times_called == 1
    stq_call = stq.bank_userinfo_deactivate_user.next_call()
    assert stq_call['id'] == 'deactivate_user_' + BUID
    stq_kwargs = stq_call['kwargs']
    stq_kwargs.pop('log_extra')
    assert stq_kwargs == {
        'buid': BUID,
        'idempotency_token': IDEMPOTENCY_TOKEN,
        'reason': REASON,
        'x_remote_ip': REMOTE_IP,
    }


async def test_support_handle_ok(
        taxi_bank_userinfo, mockserver, stq, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=get_support_headers(idempotency_token=IDEMPOTENCY_TOKEN),
        json={'buid': BUID, 'reason': REASON},
    )
    assert response.status_code == 200

    assert stq.bank_userinfo_deactivate_user.times_called == 1
    stq_call = stq.bank_userinfo_deactivate_user.next_call()
    assert stq_call['id'] == 'deactivate_user_' + BUID
    stq_kwargs = stq_call['kwargs']
    stq_kwargs.pop('log_extra')
    assert stq_kwargs == {
        'buid': BUID,
        'idempotency_token': IDEMPOTENCY_TOKEN,
        'reason': REASON,
        'x_remote_ip': REMOTE_IP,
    }


async def test_support_handle_access_deny(
        taxi_bank_userinfo, mockserver, stq, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=get_support_headers(
            token='', idempotency_token=IDEMPOTENCY_TOKEN,
        ),
        json={'buid': BUID, 'reason': REASON},
    )
    assert response.status_code == 401

    assert stq.bank_userinfo_deactivate_user.times_called == 0


async def test_stq_ok(
        taxi_bank_userinfo,
        mockserver,
        pgsql,
        stq,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='deactivate_user_' + BUID,
        kwargs=default_stq_kwargs(),
        expect_fail=False,
    )
    assert bank_applications.get_processing_apps_handle.times_called == 1
    assert bank_core_client.client_deactivate_handler.times_called == 1
    assert bank_core_client.request_check_handler.times_called == 1
    assert bank_applications.delete_passport_bank_phone.times_called == 1
    assert bank_applications.get_applications_handle.times_called == 1
    assert bank_applications.delete_application_handle.times_called == 1
    assert bank_userinfo.delete_user_handler.times_called == 1
    assert mock_stq_reschedule.times_called == 0


@pytest.mark.parametrize(
    'status_code, json',
    [
        (500, {}),
        (
            200,
            {
                'applications': [
                    {
                        'application_id': (
                            '495d0628-dd00-4d13-8043-50b182cb3a1f'
                        ),
                        'type': 'REGISTRATION',
                        'is_blocking': 'true',
                    },
                ],
            },
        ),
    ],
)
async def test_stq_get_processing_applications_stage(
        taxi_bank_userinfo,
        mockserver,
        stq,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
        status_code,
        json,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler(
        '/bank-applications'
        '/applications-internal/v1/get_processing_applications',
    )
    def get_processing_applications(request):
        return mockserver.make_response(status=status_code, json=json)

    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='deactivate_user_' + BUID,
        kwargs=default_stq_kwargs(),
        expect_fail=False,
    )
    assert get_processing_applications.times_called == 1
    assert bank_core_client.client_deactivate_handler.times_called == 1
    assert bank_core_client.request_check_handler.times_called == 1
    assert bank_applications.delete_passport_bank_phone.times_called == 1
    assert bank_applications.get_applications_handle.times_called == 1
    assert bank_applications.delete_application_handle.times_called == 1
    assert bank_userinfo.delete_user_handler.times_called == 1
    assert mock_stq_reschedule.times_called == 0


async def test_stq_client_deactivate_handler_stage_fail(
        taxi_bank_userinfo,
        mockserver,
        stq,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler('/bank-core-client/v1/client/deactivate')
    def client_deactivate(request):
        return mockserver.make_response(status=500)

    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='deactivate_user_' + BUID,
        kwargs=default_stq_kwargs(),
        expect_fail=True,
    )
    assert bank_applications.get_processing_apps_handle.times_called == 1
    assert client_deactivate.times_called == 2
    assert bank_core_client.request_check_handler.times_called == 0
    assert bank_applications.delete_passport_bank_phone.times_called == 0
    assert bank_applications.get_applications_handle.times_called == 0
    assert bank_applications.delete_application_handle.times_called == 0
    assert bank_userinfo.delete_user_handler.times_called == 0
    assert mock_stq_reschedule.times_called == 0


async def test_stq_client_request_check_stage_fail(
        taxi_bank_userinfo,
        mockserver,
        stq,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler('/bank-core-client/v1/client/request/check')
    def request_check(request):
        return mockserver.make_response(status=500)

    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='deactivate_user_' + BUID,
        kwargs=default_stq_kwargs(),
        expect_fail=True,
    )
    assert bank_applications.get_processing_apps_handle.times_called == 1
    assert bank_core_client.client_deactivate_handler.times_called == 1
    assert request_check.times_called == 2
    assert bank_applications.delete_passport_bank_phone.times_called == 0
    assert bank_applications.get_applications_handle.times_called == 0
    assert bank_applications.delete_application_handle.times_called == 0
    assert bank_userinfo.delete_user_handler.times_called == 0
    assert mock_stq_reschedule.times_called == 0


async def test_stq_client_request_check_stage_pending(
        taxi_bank_userinfo,
        mockserver,
        stq,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler('/bank-core-client/v1/client/request/check')
    def request_check(request):
        return {
            'status': 'PENDING',
            'request_id': '1ab7f45d-492f-41cd-bfe8-3611eb65ef80',
        }

    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='deactivate_user_' + BUID,
        kwargs=default_stq_kwargs(),
        expect_fail=False,
    )
    assert bank_applications.get_processing_apps_handle.times_called == 1
    assert bank_core_client.client_deactivate_handler.times_called == 1
    assert request_check.times_called == 1
    assert bank_applications.delete_passport_bank_phone.times_called == 0
    assert bank_applications.get_applications_handle.times_called == 0
    assert bank_applications.delete_application_handle.times_called == 0
    assert bank_userinfo.delete_user_handler.times_called == 0
    assert mock_stq_reschedule.times_called == 1


@pytest.mark.parametrize(
    'status_code, json, expect_fail',
    [(500, {}, True), (200, {'status': 'FAILED', 'errors': []}, False)],
)
async def test_stq_delete_passport_bank_phone_stage_fail(
        taxi_bank_userinfo,
        mockserver,
        stq,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
        status_code,
        json,
        expect_fail,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler(
        '/bank-applications'
        '/applications-internal/v1/delete_passport_bank_phone',
    )
    def delete_passport_bank_phone(request):
        return mockserver.make_response(status=status_code, json=json)

    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='deactivate_user_' + BUID,
        kwargs=default_stq_kwargs(),
        expect_fail=expect_fail,
    )
    assert bank_applications.get_processing_apps_handle.times_called == 1
    assert bank_core_client.client_deactivate_handler.times_called == 1
    assert bank_core_client.request_check_handler.times_called == 1
    assert delete_passport_bank_phone.times_called == 1
    assert bank_applications.get_applications_handle.times_called == 0
    assert bank_applications.delete_application_handle.times_called == 0
    assert bank_userinfo.delete_user_handler.times_called == 0
    assert mock_stq_reschedule.times_called == 0


async def test_stq_delete_passport_bank_phone_stage_sid_not_found(
        taxi_bank_userinfo,
        mockserver,
        stq,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler(
        '/bank-applications'
        '/applications-internal/v1/delete_passport_bank_phone',
    )
    def delete_passport_bank_phone(request):
        return {
            'status': 'FAILED',
            'errors': [
                'alias.not_found',
                'RemoveSidFromPassport error: DELETE '
                '/1/account/yandex_uid/subscription/bank/, status code 404',
            ],
        }

    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='deactivate_user_' + BUID,
        kwargs=default_stq_kwargs(),
        expect_fail=False,
    )
    assert bank_applications.get_processing_apps_handle.times_called == 1
    assert bank_core_client.client_deactivate_handler.times_called == 1
    assert bank_core_client.request_check_handler.times_called == 1
    assert delete_passport_bank_phone.times_called == 1
    assert bank_applications.get_applications_handle.times_called == 1
    assert bank_applications.delete_application_handle.times_called == 1
    assert bank_userinfo.delete_user_handler.times_called == 1
    assert mock_stq_reschedule.times_called == 0


@pytest.mark.parametrize(
    'status_code, json', [(500, {}), (401, {'status': '', 'message': ''})],
)
async def test_stq_get_applications_stage_fail(
        taxi_bank_userinfo,
        mockserver,
        stq,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
        status_code,
        json,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler(
        '/bank-applications' '/applications-internal/v1/get_applications',
    )
    def get_applications(request):
        return mockserver.make_response(status=status_code, json=json)

    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='deactivate_user_' + BUID,
        kwargs=default_stq_kwargs(),
        expect_fail=True,
    )
    assert bank_applications.get_processing_apps_handle.times_called == 1
    assert bank_core_client.client_deactivate_handler.times_called == 1
    assert bank_core_client.request_check_handler.times_called == 1
    assert bank_applications.delete_passport_bank_phone.times_called == 1
    assert get_applications.times_called == 1
    assert bank_applications.delete_application_handle.times_called == 0
    assert bank_userinfo.delete_user_handler.times_called == 0
    assert mock_stq_reschedule.times_called == 0


async def test_stq_get_applications_stage_empty_list(
        taxi_bank_userinfo,
        mockserver,
        stq,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler(
        '/bank-applications' '/applications-internal/v1/get_applications',
    )
    def get_applications(request):
        return {'applications': []}

    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='deactivate_user_' + BUID,
        kwargs=default_stq_kwargs(),
        expect_fail=False,
    )
    assert bank_applications.get_processing_apps_handle.times_called == 1
    assert bank_core_client.client_deactivate_handler.times_called == 1
    assert bank_core_client.request_check_handler.times_called == 1
    assert bank_applications.delete_passport_bank_phone.times_called == 1
    assert get_applications.times_called == 1
    assert bank_applications.delete_application_handle.times_called == 0
    assert bank_userinfo.delete_user_handler.times_called == 1
    assert mock_stq_reschedule.times_called == 0


@pytest.mark.parametrize('status_code, json', [(500, {})])
async def test_stq_delete_application_fail(
        taxi_bank_userinfo,
        mockserver,
        stq,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
        status_code,
        json,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler(
        '/bank-applications' '/applications-internal/v1/delete_application',
    )
    def delete_application(request):
        return mockserver.make_response(status=status_code, json=json)

    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='deactivate_user_' + BUID,
        kwargs=default_stq_kwargs(),
        expect_fail=True,
    )
    assert bank_applications.get_processing_apps_handle.times_called == 1
    assert bank_core_client.client_deactivate_handler.times_called == 1
    assert bank_core_client.request_check_handler.times_called == 1
    assert bank_applications.delete_passport_bank_phone.times_called == 1
    assert bank_applications.get_applications_handle.times_called == 1
    assert delete_application.times_called == 1
    assert bank_userinfo.delete_user_handler.times_called == 0
    assert mock_stq_reschedule.times_called == 0


@pytest.mark.parametrize('status_code, json', [(500, {})])
async def test_stq_delete_user_fail(
        taxi_bank_userinfo,
        mockserver,
        stq,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
        status_code,
        json,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler('/bank-userinfo/userinfo-internal/v1/delete_user')
    def delete_user_handler(request):
        return mockserver.make_response(status=status_code, json=json)

    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='deactivate_user_' + BUID,
        kwargs=default_stq_kwargs(),
        expect_fail=True,
    )
    assert bank_applications.get_processing_apps_handle.times_called == 1
    assert bank_core_client.client_deactivate_handler.times_called == 1
    assert bank_core_client.request_check_handler.times_called == 1
    assert bank_applications.delete_passport_bank_phone.times_called == 1
    assert bank_applications.get_applications_handle.times_called == 1
    assert bank_applications.delete_application_handle.times_called == 1
    assert delete_user_handler.times_called == 1
    assert mock_stq_reschedule.times_called == 0


async def test_stq_user_already_deactivated(
        taxi_bank_userinfo,
        mockserver,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
        pgsql,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    utils.update_buid_status(pgsql, BUID, 'DEACTIVATED')
    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='deactivate_user_' + BUID,
        kwargs=default_stq_kwargs(),
        expect_fail=False,
    )
    assert not bank_applications.get_processing_apps_handle.has_calls
    assert not bank_core_client.client_deactivate_handler.has_calls
    assert not bank_core_client.request_check_handler.has_calls
    assert not bank_applications.delete_passport_bank_phone.has_calls
    assert not bank_applications.get_applications_handle.has_calls
    assert not bank_applications.delete_application_handle.has_calls
    assert not bank_userinfo.delete_user_handler.has_calls
    assert not mock_stq_reschedule.has_calls


@pytest.mark.parametrize('set_reason_code', [True, False])
async def test_stq_ok_slr_0003(
        mockserver,
        stq_runner,
        bank_applications,
        bank_core_client,
        bank_userinfo,
        set_reason_code,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    kwargs = default_stq_kwargs()
    if set_reason_code:
        kwargs['reason_code'] = 'SLR-0003'
    await stq_runner.bank_userinfo_deactivate_user.call(
        task_id='registration_fail_slr_0003_' + BUID,
        kwargs=kwargs,
        expect_fail=False,
    )
    assert bank_applications.get_processing_apps_handle.times_called == 1
    assert bank_core_client.client_deactivate_handler.times_called == 0
    assert bank_core_client.request_check_handler.times_called == 0
    assert bank_applications.delete_passport_bank_phone.times_called == 1
    assert bank_applications.get_applications_handle.times_called == 1
    assert bank_applications.delete_application_handle.times_called == 1
    assert bank_userinfo.delete_user_handler.times_called == 1
    assert mock_stq_reschedule.times_called == 0
