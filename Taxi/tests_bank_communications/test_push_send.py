# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest
from tests_bank_communications import utils
from bank_communications_plugins.generated_tests import *


def get_kwargs():
    return {
        'communication_id': '67754336-d4d1-43c1-aadb-cabd06674ea6',
        'bank_uid': '7948e3a9-623c-4524-a390-9e4264d27a11',
        'body_tanker_key': 'text',
        'title_tanker_key': 'title',
        'template_parameters': {
            'text': 'You\'ve got push from bank!',
            'title': 'Bank Title',
        },
    }


async def test_no_active_subscription(stq_runner, pgsql):
    kwargs = get_kwargs()
    await stq_runner.bank_communications_push_send.call(
        task_id='id', kwargs=kwargs, expect_fail=False,
    )

    push = utils.get_push_by_communication_id(
        pgsql, kwargs['communication_id'],
    )
    assert push['status'] == 'NO_ACTIVE_SUBSCRIPTION'
    assert push['notification_text'] is None
    assert push['uuid'] is None


async def test_push_sent(stq_runner, pgsql, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _mock_send(request):
        assert request.method == 'POST'
        assert request.json.get('payload').get('yamp').get('a')
        assert request.json['payload']['yamp']['d'] == {
            'e': 'Bank Title',
            'g': 'You\'ve got push from bank!',
        }
        assert request.json['repack'] == {'fcm': {'repack_payload': ['yamp']}}
        assert request.json['subscriptions'] == [{'uuid': ['uuid']}]
        assert request.query['service'] == 'bank'
        assert request.query['user'] == '11111111-1111-1111-1111-111111111111'

        return mockserver.make_response(headers={'TransitID': 'id'})

    kwargs = get_kwargs()
    utils.insert_push_subscription(
        pgsql, 'uuid', '7948e3a9-623c-4524-a390-9e4264d27a11',
    )
    await stq_runner.bank_communications_push_send.call(
        task_id='id', kwargs=kwargs, expect_fail=False,
    )

    push = utils.get_push_by_communication_id(
        pgsql, kwargs['communication_id'],
    )
    assert push['status'] == 'SENT'
    assert push['notification_text'] == 'You\'ve got push from bank!'
    assert push['uuid'] == 'uuid'


@pytest.mark.parametrize('push_status', ['NO_ACTIVE_SUBSCRIPTION', 'SENT'])
async def test_push_final_status(
        stq_runner, pgsql, mockserver, xiva_mock, push_status,
):
    kwargs = get_kwargs()
    utils.insert_push_notification(
        pgsql,
        kwargs['communication_id'],
        push_status,
        '67754336-d4d1-43c1-aadb-cabd06674e00',
    )
    await stq_runner.bank_communications_push_send.call(
        task_id='id', kwargs=kwargs, expect_fail=False,
    )

    assert not xiva_mock.send_handle.has_calls


async def test_ready_to_sent(stq_runner, pgsql, mockserver, xiva_mock):
    kwargs = get_kwargs()
    utils.insert_push_notification(
        pgsql,
        kwargs['communication_id'],
        'READY_TO_SENT',
        '67754336-d4d1-43c1-aadb-cabd06674e00',
    )
    await stq_runner.bank_communications_push_send.call(
        task_id='id', kwargs=kwargs, expect_fail=False,
    )

    assert xiva_mock.send_handle.has_calls
    push = utils.get_push_by_communication_id(
        pgsql, kwargs['communication_id'],
    )
    assert push['status'] == 'SENT'
    assert push['notification_text'] == 'notification_text'
    assert push['uuid'] == 'uuid'


@pytest.mark.parametrize('push_status', [None, 'READY_TO_SENT'])
async def test_xiva_error(stq_runner, pgsql, mockserver, push_status):
    @mockserver.json_handler('/xiva/v2/send')
    def _mock_send(request):

        return mockserver.make_response(
            status=400, headers={'TransitID': 'id'},
        )

    kwargs = get_kwargs()
    sub_id = utils.insert_push_subscription(
        pgsql, 'uuid', '7948e3a9-623c-4524-a390-9e4264d27a11',
    )
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


@pytest.mark.parametrize('locale', ['ru', 'en'])
async def test_locale(stq_runner, pgsql, mockserver, xiva_mock, locale):
    kwargs = get_kwargs()
    kwargs['body_tanker_key'] = 'code'
    kwargs['template_parameters'] = {
        'code': '123',
        'name': 'Bob',
        'title': 'Notification',
    }
    utils.insert_push_subscription(
        pgsql, 'uuid', '7948e3a9-623c-4524-a390-9e4264d27a11', locale=locale,
    )
    await stq_runner.bank_communications_push_send.call(
        task_id='id', kwargs=kwargs, expect_fail=False,
    )

    push = utils.get_push_by_communication_id(
        pgsql, kwargs['communication_id'],
    )
    assert push['status'] == 'SENT'
    assert push['title'] == 'Notification'
    if locale == 'ru':
        assert push['notification_text'] == 'Привет Bob, твой код 123!'
    elif locale == 'en':
        assert push['notification_text'] == 'Hi Bob, your code 123!'
    else:
        assert False


@pytest.mark.config(
    BANK_COMMUNICATIONS_RULES_SECURE={
        'code': {
            'routes': [
                {
                    'type': 'push',
                    'parts': {
                        'body': {'tanker_key': 'code'},
                        'title': {'tanker_key': 'title'},
                    },
                },
            ],
        },
    },
)
async def test_push_send_handle(taxi_bank_communications, stq):
    headers = {'X-Idempotency-Token': '67754336-d4d1-43c1-aadb-cabd06674ea6'}
    body = {
        'buid': '7948e3a9-623c-4524-a390-9e4264d27a11',
        'type': 'code',
        'locale': 'ru',
        'template_parameters': {'code': '123', 'title': 'Notification'},
    }

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=body,
    )

    assert response.status_code == 200
    assert stq.bank_communications_push_send.has_calls
    next_stq_call = stq.bank_communications_push_send.next_call()
    assert next_stq_call['queue'] == 'bank_communications_push_send'
    assert next_stq_call['kwargs']['template_parameters'] == {
        'code': '123',
        'title': 'Notification',
    }
    assert next_stq_call['kwargs']['body_tanker_key'] == 'code'
    assert next_stq_call['kwargs']['title_tanker_key'] == 'title'
    assert (
        next_stq_call['kwargs']['bank_uid']
        == '7948e3a9-623c-4524-a390-9e4264d27a11'
    )


@pytest.mark.config(
    BANK_COMMUNICATIONS_RULES_SECURE={
        'text': {
            'routes': [
                {
                    'type': 'push',
                    'parts': {
                        'body': {'tanker_key': 'text'},
                        'title': {'tanker_key': 'title'},
                        'deeplink': {'tanker_key': 'deeplink'},
                    },
                },
            ],
        },
    },
)
async def test_push_send_deeplink(
        taxi_bank_communications, stq_runner, mockserver, pgsql, stq,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _mock_send(request):
        assert request.method == 'POST'
        assert request.json.get('payload').get('yamp').get('a')
        assert request.json['payload']['yamp']['d'] == {
            'e': 'Bank Title',
            'g': 'You\'ve got push from bank!',
            'w': 'https:\\/\\/yandex.ru',
        }
        assert request.json['repack'] == {'fcm': {'repack_payload': ['yamp']}}
        assert request.json['subscriptions'] == [{'uuid': ['uuid']}]
        assert request.query['service'] == 'bank'
        assert request.query['user'] == '11111111-1111-1111-1111-111111111111'

        return mockserver.make_response(headers={'TransitID': 'id'})

    headers = {'X-Idempotency-Token': '67754336-d4d1-43c1-aadb-cabd06674ea6'}
    body = {
        'buid': '7948e3a9-623c-4524-a390-9e4264d27a11',
        'type': 'text',
        'locale': 'ru',
        'template_parameters': {
            'text': '123',
            'title': 'Notification',
            'deeplink': 'https:\\/\\/yandex.ru',
        },
    }

    response = await taxi_bank_communications.post(
        '/communications-internal/v1/send', headers=headers, json=body,
    )
    assert response.status_code == 200

    utils.insert_push_subscription(
        pgsql, 'uuid', '7948e3a9-623c-4524-a390-9e4264d27a11',
    )

    assert stq.bank_communications_push_send.has_calls
    next_stq_call = stq.bank_communications_push_send.next_call()
    assert next_stq_call['kwargs']['deeplink_tanker_key'] == 'deeplink'
    await stq_runner.bank_communications_push_send.call(
        task_id='id',
        kwargs={
            'communication_id': '67754336-d4d1-43c1-aadb-cabd06674ea6',
            'bank_uid': '7948e3a9-623c-4524-a390-9e4264d27a11',
            'body_tanker_key': 'text',
            'title_tanker_key': 'title',
            'deeplink_tanker_key': 'deeplink',
            'template_parameters': {
                'text': 'You\'ve got push from bank!',
                'title': 'Bank Title',
                'deeplink': 'https:\\/\\/yandex.ru',
            },
        },
        expect_fail=False,
    )
    assert _mock_send.has_calls
