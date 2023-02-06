import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers
from tests_bank_applications import plus_db_helpers


@pytest.mark.parametrize(
    'application_status', ['PROCESSING', 'CREATED', '', '123'],
)
async def test_invalid_status(
        taxi_bank_applications,
        mockserver,
        pgsql,
        bank_notifications_mock,
        application_status,
):
    application_id = plus_db_helpers.insert_plus_application(
        pgsql, status='CREATED',
    )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/plus/complete_application',
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'buid': common.DEFAULT_YANDEX_BUID,
            'status': application_status,
        },
    )
    assert bank_notifications_mock.send_events_handler.times_called == 0
    assert response.status_code == 400


async def test_app_not_found(
        taxi_bank_applications, mockserver, pgsql, bank_notifications_mock,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/plus/complete_application',
        headers=common.headers_with_idempotency(),
        json={
            'application_id': '02761e13-fbe2-4212-821a-62bbaab122c7',
            'buid': common.DEFAULT_YANDEX_BUID,
            'status': 'SUCCESS',
        },
    )
    assert bank_notifications_mock.send_events_handler.times_called == 0
    assert response.status_code == 404


@pytest.mark.parametrize('application_status', ['SUCCESS', 'FAILED'])
async def test_ok_already_submitted(
        taxi_bank_applications,
        mockserver,
        pgsql,
        bank_notifications_mock,
        application_status,
):
    application_id = plus_db_helpers.insert_plus_application(
        pgsql, status=application_status,
    )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/plus/complete_application',
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'buid': common.DEFAULT_YANDEX_BUID,
            'status': application_status,
        },
    )
    assert bank_notifications_mock.send_events_handler.times_called == 0
    assert response.status_code == 200


@pytest.mark.parametrize(
    'status_code,response',
    [
        (400, {'code': 'BadRequest', 'message': 'some msg1'}),
        (404, {'code': 'NotFound', 'message': 'some msg2'}),
        (409, {'code': 'Conflict', 'message': 'some msg3'}),
        (500, {'code': 'ServerError', 'message': 'some msg4'}),
    ],
)
async def test_send_notification_error(
        taxi_bank_applications,
        mockserver,
        pgsql,
        bank_notifications_mock,
        status_code,
        response,
):
    application_id = plus_db_helpers.insert_plus_application(
        pgsql, status='CREATED',
    )

    bank_notifications_mock.set_http_status_code(status_code)
    bank_notifications_mock.set_response(response)

    response = await taxi_bank_applications.post(
        'applications-internal/v1/plus/complete_application',
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'buid': common.DEFAULT_YANDEX_BUID,
            'status': 'SUCCESS',
        },
    )
    assert bank_notifications_mock.send_events_handler.times_called == 1
    assert response.status_code == status_code


@pytest.mark.parametrize('current_status', ['SUCCESS', 'FAILED'])
@pytest.mark.parametrize('new_status', ['SUCCESS', 'FAILED'])
async def test_update(
        taxi_bank_applications,
        mockserver,
        pgsql,
        testpoint,
        bank_notifications_mock,
        current_status,
        new_status,
):
    application_id = plus_db_helpers.insert_plus_application(
        pgsql, status='CREATED',
    )

    @testpoint('update_data_race')
    async def _update_data_race(data):
        plus_db_helpers.update_plus_application_status(
            pgsql, application_id, current_status,
        )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/plus/complete_application',
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'buid': common.DEFAULT_YANDEX_BUID,
            'status': new_status,
        },
    )
    assert bank_notifications_mock.send_events_handler.times_called == 1
    assert response.status_code == 200

    app = plus_db_helpers.select_plus_application(pgsql, application_id)
    assert app == (
        application_id,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        new_status,
        None,
        {},
    )


async def test_token_already_in_history(
        taxi_bank_applications,
        mockserver,
        pgsql,
        testpoint,
        bank_notifications_mock,
):
    application_id = plus_db_helpers.insert_plus_application(
        pgsql, status='CREATED',
    )

    @testpoint('update_data_race')
    async def _update_data_race(data):
        plus_db_helpers.update_plus_application_status(
            pgsql, application_id, 'SUCCESS',
        )
        plus_db_helpers.insert_plus_application_history(
            pgsql,
            application_id,
            'SUCCESS',
            'complete_' + common.DEFAULT_IDEMPOTENCY_TOKEN,
        )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/plus/complete_application',
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'buid': common.DEFAULT_YANDEX_BUID,
            'status': 'FAILED',
        },
    )
    assert response.status_code == 500
    assert bank_notifications_mock.send_events_handler.times_called == 1

    app = plus_db_helpers.select_plus_application(pgsql, application_id)
    assert app == (
        application_id,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'SUCCESS',
        None,
        {},
    )
    app_history = plus_db_helpers.select_plus_application_history(
        pgsql, application_id,
    )
    assert len(app_history) == 1


async def test_idempotency(
        taxi_bank_applications,
        mockserver,
        pgsql,
        testpoint,
        bank_notifications_mock,
):
    application_id = plus_db_helpers.insert_plus_application(
        pgsql, status='CREATED',
    )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/plus/complete_application',
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'buid': common.DEFAULT_YANDEX_BUID,
            'status': 'FAILED',
        },
    )
    assert response.status_code == 200

    response2 = await taxi_bank_applications.post(
        'applications-internal/v1/plus/complete_application',
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'buid': common.DEFAULT_YANDEX_BUID,
            'status': 'FAILED',
        },
    )
    assert response2.status_code == 200

    assert bank_notifications_mock.send_events_handler.times_called == 1

    app = plus_db_helpers.select_plus_application(pgsql, application_id)
    assert app == (
        application_id,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'FAILED',
        None,
        {},
    )
    app_history = plus_db_helpers.select_plus_application_history(
        pgsql, application_id,
    )
    assert len(app_history) == 1


async def test_ok_status_failed(
        taxi_bank_applications, mockserver, pgsql, bank_notifications_mock,
):
    application_id = plus_db_helpers.insert_plus_application(
        pgsql, status='CREATED',
    )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/plus/complete_application',
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'buid': common.DEFAULT_YANDEX_BUID,
            'status': 'FAILED',
            'errors': ['error1', 'error2', 'error3'],
        },
    )
    assert bank_notifications_mock.send_events_handler.times_called == 1
    assert response.status_code == 200

    app = plus_db_helpers.select_plus_application(pgsql, application_id)
    assert app == (
        application_id,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'FAILED',
        'error1, error2, error3',
        {},
    )
    app_history = plus_db_helpers.select_plus_application_history(
        pgsql, application_id,
    )
    assert app_history[0] == (
        application_id,
        'complete_' + common.DEFAULT_IDEMPOTENCY_TOKEN,
        'UPDATE',
        'FAILED',
    )
    common_app = db_helpers.get_application(pgsql, application_id)
    assert common_app == (
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'PLUS',
        'FAILED',
        'error1, error2, error3',
    )


async def test_ok_status_success(
        taxi_bank_applications, mockserver, pgsql, bank_notifications_mock,
):
    application_id = plus_db_helpers.insert_plus_application(
        pgsql, status='CREATED',
    )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/plus/complete_application',
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'buid': common.DEFAULT_YANDEX_BUID,
            'status': 'SUCCESS',
        },
    )
    assert bank_notifications_mock.send_events_handler.times_called == 1
    assert response.status_code == 200

    app = plus_db_helpers.select_plus_application(pgsql, application_id)
    assert app == (
        application_id,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'SUCCESS',
        None,
        {},
    )
    app_history = plus_db_helpers.select_plus_application_history(
        pgsql, application_id,
    )
    assert app_history[0] == (
        application_id,
        'complete_' + common.DEFAULT_IDEMPOTENCY_TOKEN,
        'UPDATE',
        'SUCCESS',
    )
    common_app = db_helpers.get_application(pgsql, application_id)
    assert common_app == (
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'PLUS',
        'SUCCESS',
        None,
    )
