# flake8: noqa
# pylint: disable=import-error,wildcard-import
from psycopg2 import extras
import pytest

from eats_restapp_support_chat_plugins.generated_tests import *


@pytest.mark.parametrize(
    'owner_id,role,chat_id,expected_result',
    [
        ('222', 'ROLE_MANAGER', 'chat1', {('1', 'chat1'): 3}),
        (
            '222',
            'ROLE_OPERATOR',
            'chat1',
            {('1', 'chat1'): 3, ('2', 'chat1'): 1},
        ),
        ('partner_1', 'ROLE_MANAGER', 'chat1', {('1', 'chat1'): 3}),
    ],
)
async def test_stq_handle_event(
        stq_runner,
        mockserver,
        pgsql,
        owner_id,
        role,
        chat_id,
        expected_result,
):
    @mockserver.json_handler('/client-notify/v1/push')
    def client_notify_handler(data):
        return {'notification_id': '123123'}

    await stq_runner.eats_restapp_support_chat_handle_event.call(
        task_id='test',
        args=[owner_id, chat_id, {'$date': '2021-03-02T23:00:00+0300'}, role],
        kwargs={'log_extra': {}},
        expect_fail=False,
    )
    pg_cursor = pgsql['eats_restapp_support_chat'].cursor(
        cursor_factory=extras.RealDictCursor,
    )
    pg_cursor.execute(
        f'select partner_id, chat_id, new_message_count '
        f'from eats_restapp_support_chat.partners_chats;',
    )
    rows = pg_cursor.fetchall()
    result = {
        (row['partner_id'], row['chat_id']): row['new_message_count']
        for row in rows
    }
    assert result == expected_result

    assert client_notify_handler.times_called == len(expected_result)

    expected_partner_id_chat_id = {
        owner_id[0]: owner_id[1] for owner_id in expected_result
    }

    partner_id_chat_id = {}
    for _ in range(client_notify_handler.times_called):
        request_data = client_notify_handler.next_call()['data'].json
        assert request_data['service'] == 'eats-partner'
        assert request_data['intent'] == 'support_chat_new_message'
        assert (
            request_data['data']['payload']['eventData']['event']
            == 'new_message'
        )
        partner_id_chat_id[request_data['client_id']] = request_data['data'][
            'payload'
        ]['eventData']['chat_id']

    assert partner_id_chat_id == expected_partner_id_chat_id
