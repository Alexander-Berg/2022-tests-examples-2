from tests_bank_applications import common

HANDLE_URL = '/applications-support/v1/simplified_identification/start_procaas_for_submitted'  # noqa


def check_application(pgsql, application_id, expected_apps_count):
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT application_id '
        'FROM bank_applications.simplified_identification '
        f'WHERE application_id=\'{application_id}\' AND status=\'SUBMITTED\' AND user_id_type=\'BUID\';',  # noqa
    )
    records = list(cursor)
    assert len(records) == expected_apps_count


async def test_start_procaas_for_submitted_application_ok(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    application_id = '11111111-1111-1111-1111-111111111111'
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': application_id},
    )
    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 2
    assert access_control_mock.apply_policies_handler.times_called == 1
    check_application(pgsql, application_id, 1)


async def test_start_procaas_for_submitted_processing_returns_500(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    application_id = '11111111-1111-1111-1111-111111111111'
    taxi_processing_mock.http_status_code = 500
    taxi_processing_mock.response = {'code': '500', 'message': 'error'}
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': application_id},
    )
    assert response.status_code == 500
    assert taxi_processing_mock.create_event_handler.times_called == 3
    assert access_control_mock.apply_policies_handler.times_called == 1
    check_application(pgsql, application_id, 1)


async def test_start_procaas_for_submitted_access_deny(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(''),
        json={'application_id': '11111111-1111-1111-1111-111111111111'},
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_start_procaas_for_submitted_application_not_found(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    application_id = '99999999-1111-1111-1111-111111111111'
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': application_id},
    )
    assert response.status_code == 404
    assert not taxi_processing_mock.create_event_handler.has_calls
    assert access_control_mock.apply_policies_handler.times_called == 1
    check_application(pgsql, application_id, 0)


async def test_start_procaas_for_submitted_app_in_invalid_status(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    application_id = '22222222-1111-1111-1111-111111111111'
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': application_id},
    )
    assert response.status_code == 409
    assert not taxi_processing_mock.create_event_handler.has_calls
    assert access_control_mock.apply_policies_handler.times_called == 1
    check_application(pgsql, application_id, 0)


async def test_start_procaas_for_submitted_invalid_application_id(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    application_id = '0000'
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': application_id},
    )
    assert response.status_code == 400
    assert not taxi_processing_mock.create_event_handler.has_calls
    assert not access_control_mock.apply_policies_handler.has_calls


async def test_start_procaas_for_submitted_application_idempotency_token_is_null(  # noqa
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    application_id = '33333333-1111-1111-1111-111111111111'
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': application_id},
    )
    check_application(pgsql, application_id, 1)
    assert response.status_code == 500
    assert not taxi_processing_mock.create_event_handler.has_calls
    assert access_control_mock.apply_policies_handler.times_called == 1
