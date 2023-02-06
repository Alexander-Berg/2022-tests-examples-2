# pylint: disable=too-many-arguments,redefined-outer-name
import datetime

import bson
import pytest

from chatterbox import stq_task


@pytest.mark.parametrize(
    ('task_id', 'expected_ticket', 'expected_messages'),
    [
        (
            bson.ObjectId('5b2cae5cb2682a976914caa1'),
            {
                '_id': bson.ObjectId('5b2cae5cb2682a976914caa1'),
                'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
                'external_id': 'user_chat_message_id_1',
                'line': 'first',
                'status': 'ready_to_archive',
                'support_admin': 'superuser',
                'type': 'chat',
                'chat_type': 'market',
                'meta_info': {
                    'order_id': '11111',
                    'user_email': '111@mail.ru',
                    'user_phone': '+79110000000',
                },
                'history': [],
                'inner_comments': [
                    {'comment': 'Comment111', 'login': 'superuser'},
                ],
            },
            {
                'messages': [
                    {
                        'sender': {'id': 'support_login', 'role': 'support'},
                        'text': 'support text',
                    },
                    {
                        'sender': {'id': 'client_login', 'role': 'client'},
                        'text': 'client text',
                    },
                ],
                'hidden_comments': [
                    {'comment': 'Comment111', 'login': 'superuser'},
                ],
            },
        ),
        (
            bson.ObjectId('5b2cae5cb2682a976914caa2'),
            {
                '_id': bson.ObjectId('5b2cae5cb2682a976914caa2'),
                'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
                'external_id': 'user_chat_message_id_2',
                'line': 'first',
                'status': 'ready_to_archive',
                'support_admin': 'superuser',
                'type': 'chat',
                'chat_type': 'market',
                'meta_info': {},
                'history': [],
                'inner_comments': [],
            },
            {
                'messages': [
                    {
                        'sender': {'id': 'support_login', 'role': 'support'},
                        'text': 'support text',
                    },
                    {
                        'sender': {'id': 'client_login', 'role': 'client'},
                        'text': 'client text',
                    },
                ],
                'hidden_comments': [],
            },
        ),
    ],
)
async def test_send_archive_ticket_to_market(
        cbox,
        mock,
        patch,
        mock_chat_get_history,
        load_json,
        task_id,
        expected_ticket,
        expected_messages,
):
    messages = load_json('chat_messages.json')
    mock_chat_get_history({'messages': messages})

    @mock
    @patch('taxi.clients.market_crm.MarketCrmApiClient.send_ticket')
    async def _mock_send_ticket(ticket, messages, **kwargs):
        assert ticket == expected_ticket
        assert messages == expected_messages

    await stq_task.send_archive_ticket_to_market(cbox.app, task_id)

    assert len(_mock_send_ticket.calls) == 1
