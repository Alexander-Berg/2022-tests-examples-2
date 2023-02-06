import pytest

from tests_bank_applications import common

APPLICATION_ID_1 = '7948e3a9-623c-4524-1111-9e4264d27a01'
APPLICATION_ID_2 = '7948e3a9-623c-4524-1111-9e4264d27a02'

WRONG_APLLICATION_ID = '7948e3a9-0000-0000-1111-9e4264d27a02'

WRONG_TOKEN = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJzdWIiOiJzdXBwb3J0LWFiYy11.'
)


def check_application(pgsql, application_id, json):
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT status, initiator, reason, comment FROM '
        'bank_applications.change_phone_applications '
        'WHERE application_id = %s',
        [application_id],
    )
    records = cursor.fetchall()
    assert records[0][0] == 'FAILED'
    assert records[0][1]['initiator_id'] == 'support-abc'
    assert records[0][2] == 'CANCELLED_BY_SUPPORT'
    if 'comment' in json.keys():
        assert records[0][3] == json['comment']
    assert len(records) == 1

    cursor.execute(
        'SELECT status FROM bank_applications.applications '
        'WHERE application_id = %s',
        [application_id],
    )
    records = cursor.fetchall()
    assert records[0][0] == 'FAILED'


@pytest.mark.parametrize('validation_type', ['REGULAR', 'LOSTWITHCARANTINE'])
@pytest.mark.parametrize(
    'json_data',
    [
        {'application_id': APPLICATION_ID_1, 'comment': 'this is the way'},
        {'application_id': APPLICATION_ID_1},
    ],
)
async def test_change_phone_close_application_ok(
        taxi_bank_applications,
        access_control_mock,
        pgsql,
        json_data,
        stq_runner,
        validation_type,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/close_application',
        headers=headers,
        json=json_data,
    )

    assert response.status_code == 200
    check_application(pgsql, application_id=APPLICATION_ID_1, json=json_data)
    assert access_control_mock.apply_policies_handler.times_called == 1

    await stq_runner.bank_applications_change_number_timelimit_polling.call(
        task_id='stq_task_id',
        kwargs={
            'application_id': APPLICATION_ID_1,
            'validation_type': validation_type,
        },
        expect_fail=False,
    )
    check_application(pgsql, application_id=APPLICATION_ID_1, json=json_data)


async def test_change_phone_close_application_wrong_application_id(
        taxi_bank_applications, access_control_mock, pgsql,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/close_application',
        headers=headers,
        json={
            'application_id': WRONG_APLLICATION_ID,
            'comment': 'this is the way',
        },
    )

    assert response.status_code == 404
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_close_application_finished_application(
        taxi_bank_applications, access_control_mock, pgsql,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/close_application',
        headers=headers,
        json={
            'application_id': APPLICATION_ID_2,
            'comment': 'this is the way',
        },
    )

    assert response.status_code == 409
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_change_phone_close_application_access_failed(
        taxi_bank_applications, access_control_mock, pgsql,
):
    headers = common.get_support_headers(token=WRONG_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/close_application',
        headers=headers,
        json={
            'application_id': APPLICATION_ID_1,
            'comment': 'this is the way',
        },
    )

    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1
