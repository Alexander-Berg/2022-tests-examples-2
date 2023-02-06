# flake8: noqa
# pylint: disable=import-error,wildcard-import
import psycopg2
import pytest

from testsuite.utils import callinfo


@pytest.mark.pgsql('eats_restapp_support_chat', files=['insert_chats.sql'])
@pytest.mark.parametrize(
    'partner_id,params,expected_response_code,message_count,expected_unread_message_count',
    [
        ('20', {'chat_id': '30'}, 200, 0, 0),
        ('21', {'chat_id': '31'}, 200, 0, 1),
        (
            # not exist partner_id for chat_id
            '22',
            {'chat_id': '30'},
            200,
            None,
            None,
        ),
        (
            # not exist chat_id for partner_id
            '20',
            {'chat_id': '31'},
            200,
            None,
            None,
        ),
    ],
)
async def test_chat_read(
        taxi_eats_restapp_support_chat,
        mockserver,
        pgsql,
        testpoint,
        partner_id,
        params,
        expected_response_code,
        message_count,
        expected_unread_message_count,
):
    @mockserver.json_handler('/client-notify/v1/push')
    def client_notify_handler(data):
        return {'notification_id': '123123'}

    @testpoint('unread_messages_count')
    def unread_messages_count(data):
        return data

    response = await taxi_eats_restapp_support_chat.post(
        '/4.0/restapp-front/support_chat/v1/chat/read',
        headers={'X-YaEda-PartnerId': partner_id},
        params=params,
    )
    assert response.status == expected_response_code

    if message_count is not None:
        cursor = pgsql['eats_restapp_support_chat'].cursor(
            cursor_factory=psycopg2.extras.DictCursor,
        )
        cursor.execute(
            'SELECT new_message_count '
            'FROM eats_restapp_support_chat.partners_chats '
            'WHERE partner_id = \'{}\' AND chat_id = \'{}\''.format(
                partner_id, params['chat_id'],
            ),
        )
        assert message_count == cursor.fetchone()['new_message_count']

        if expected_unread_message_count == 0:
            data = await client_notify_handler.wait_call()
            request_data = data['data'].json
            assert request_data['service'] == 'eats-partner'
            assert request_data['intent'] == 'support_chat_no_unread_messages'
            assert request_data['client_id'] == partner_id
            assert (
                request_data['data']['payload']['eventData']['event']
                == 'no_unread_messages'
            )
        elif expected_unread_message_count > 0:
            unread_count = await unread_messages_count.wait_call()
            assert unread_count['data'] == expected_unread_message_count
            assert not client_notify_handler.has_calls
