# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest
from tests_bank_communications import utils
from bank_communications_plugins.generated_tests import *

bank_uid = '7948e3a9-623c-4524-a390-9e4264d27a11'


def get_kwargs():
    return {
        'communication_id': '67754336-d4d1-43c1-aadb-cabd06674ea6',
        'bank_uid': bank_uid,
        'body_tanker_key': 'text',
        'title_tanker_key': 'title',
        'template_parameters': {
            'text': 'You\'ve got push from bank!',
            'title': 'Bank Title',
        },
    }


def get_headers():
    return {
        'X-Yandex-BUID': bank_uid,
        'X-Yandex-UID': '1',
        'X-YaBank-PhoneID': 'phone_id1',
        'X-YaBank-SessionUUID': '1',
        'X-Request-Application': 'platform=app_1,app_name=android',
        'X-Request-Language': 'ru',
        'X-Ya-User-Ticket': 'user_ticket',
    }


async def test_push_ack_ok(
        taxi_bank_communications, stq_runner, pgsql, mockserver,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _mock_send(request):
        return mockserver.make_response(headers={'TransitID': 'id'})

    kwargs = get_kwargs()
    utils.insert_push_subscription(pgsql, 'uuid', bank_uid)
    await stq_runner.bank_communications_push_send.call(
        task_id='id', kwargs=kwargs, expect_fail=False,
    )

    push = utils.get_push_by_communication_id(
        pgsql, kwargs['communication_id'],
    )
    assert push['status'] == 'SENT'

    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_ack',
        headers=get_headers(),
        json={'notification_id': push['notification_id']},
    )

    assert response.status_code == 200
    push = utils.get_push_by_communication_id(
        pgsql, kwargs['communication_id'],
    )
    assert push['status'] == 'DELIVERED'


@pytest.mark.parametrize('push_status', [None, 'READY_TO_SENT'])
async def test_no_valid_status(
        taxi_bank_communications, stq_runner, pgsql, mockserver, push_status,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _mock_send(request):

        return mockserver.make_response(
            status=400, headers={'TransitID': 'id'},
        )

    kwargs = get_kwargs()
    sub_id = utils.insert_push_subscription(pgsql, 'uuid', bank_uid)
    if push_status:
        utils.insert_push_notification(
            pgsql, kwargs['communication_id'], push_status, sub_id,
        )

    await stq_runner.bank_communications_push_send.call(
        task_id='id', kwargs=kwargs, expect_fail=True,
    )

    assert _mock_send.has_calls
    push = utils.get_push_by_communication_id(
        pgsql, kwargs['communication_id'],
    )

    assert push['status'] == 'READY_TO_SENT'

    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_ack',
        headers=get_headers(),
        json={'notification_id': push['notification_id']},
    )
    assert response.status_code == 409

    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_ack',
        headers=get_headers(),
        json={'notification_id': '228'},
    )
    assert response.status_code == 404


async def test_no_valid_buid(
        taxi_bank_communications, stq_runner, pgsql, mockserver,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _mock_send(request):
        return mockserver.make_response(headers={'TransitID': 'id'})

    kwargs = get_kwargs()
    utils.insert_push_subscription(pgsql, 'uuid', bank_uid)
    await stq_runner.bank_communications_push_send.call(
        task_id='id', kwargs=kwargs, expect_fail=False,
    )

    push = utils.get_push_by_communication_id(
        pgsql, kwargs['communication_id'],
    )
    assert push['status'] == 'SENT'

    response = await taxi_bank_communications.post(
        '/v1/communications/v1/push_ack',
        headers={
            'X-Yandex-BUID': '228',
            'X-Yandex-UID': '1',
            'X-YaBank-PhoneID': 'phone_id1',
            'X-YaBank-SessionUUID': '1',
            'X-Request-Application': 'platform=app_1,app_name=android',
            'X-Request-Language': 'ru',
            'X-Ya-User-Ticket': 'user_ticket',
        },
        json={'notification_id': push['notification_id']},
    )
    assert response.status_code == 404
