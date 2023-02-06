import pytest

from tests_bank_applications import common

PARENT_APP_ID = 'd25720f2-7230-4138-9bef-63f56f778b04'


async def request(taxi_bank_applications):
    return await taxi_bank_applications.post(
        'applications-internal/v1/plus/create_application',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={
            'yandex_buid': common.DEFAULT_YANDEX_BUID,
            'yandex_uid': common.DEFAULT_YANDEX_UID,
            'parent_application_id': PARENT_APP_ID,
        },
    )


async def test_plus_create_application(
        taxi_bank_applications, pgsql, stq, bank_notifications_mock,
):
    response = await request(taxi_bank_applications)

    assert response.status_code == 200
    actual_data = response.json()
    assert 'application_id' in actual_data

    sql = (
        'SELECT * FROM bank_applications.create_plus_subscription_applications'
    )
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql)
    application = cursor.fetchone()
    assert application[:5] == (
        actual_data['application_id'],
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'CREATED',
        {'parent_application_id': PARENT_APP_ID},
    )

    sql = (
        'SELECT * FROM '
        'bank_applications.create_plus_subscription_applications_history'
    )
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql)
    application_history = cursor.fetchone()
    assert application_history[:4] == (
        'create_' + common.DEFAULT_IDEMPOTENCY_TOKEN,
        actual_data['application_id'],
        'INSERT',
        'CREATED',
    )

    sql = 'SELECT * FROM bank_applications.applications'
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql)
    base_application = list(cursor.fetchone())
    base_application[9] = ''
    assert base_application[:14] == [
        actual_data['application_id'],
        common.DEFAULT_YANDEX_BUID,
        'PLUS',
        'CREATED',
        None,
        None,
        {'initiator_id': common.DEFAULT_YANDEX_BUID, 'initiator_type': 'BUID'},
        None,
        None,
        '',
        True,
        'BUID',
        1,
        'INSERT',
    ]

    assert stq.core_cashback_plus_subscription_for_new_user.times_called == 1
    call_info = stq.core_cashback_plus_subscription_for_new_user.next_call()
    kwargs = call_info['kwargs']
    kwargs.pop('log_extra')
    assert kwargs == {
        'orderId': actual_data['application_id'],
        'uid': int(common.DEFAULT_YANDEX_UID),
        'buid': common.DEFAULT_YANDEX_BUID,
    }

    assert bank_notifications_mock.send_events_handler.times_called == 1

    second_response = await request(taxi_bank_applications)

    assert second_response.status_code == 200
    assert (
        response.json().get('application_id') == actual_data['application_id']
    )


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
    bank_notifications_mock.set_http_status_code(status_code)
    bank_notifications_mock.set_response(response)
    response = await request(taxi_bank_applications)
    assert bank_notifications_mock.send_events_handler.times_called == 1
    assert response.status_code == status_code
