# pylint: disable=redefined-outer-name
import pytest

from support_info import stq_task


@pytest.mark.config(
    STARTRACK_READONLY_QUEUE_BY_PROFILE={'yutaxi': 'YUTAXIREADONLY'},
)
@pytest.mark.parametrize(
    'message_id, message_text, tags, custom_fields, expected_create_ticket',
    [
        (
            'some_message_id',
            'Hello!',
            ['some', 'tags'],
            {
                'zendesk_profile': 'yutaxi',
                'ticket_subject': 'Some ticket',
                'order_id': 'order_id_1',
                'user_phone': '+1234567890',
            },
            {
                'queue': 'YUTAXIREADONLY',
                'unique': 'some_message_id',
                'description': 'Hello!',
                'summary': 'Some ticket',
                'tags': ['some', 'tags'],
                'custom_fields': {
                    'OrderId': 'order_id_1',
                    'userPhone': '+1234567890',
                },
            },
        ),
    ],
)
async def test_create_readonly_ticket(
        support_info_app_stq,
        mock_st_create_ticket,
        message_id,
        message_text,
        tags,
        custom_fields,
        expected_create_ticket,
):
    await stq_task.create_readonly_ticket(
        support_info_app_stq, message_id, message_text, tags, custom_fields,
    )
    create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
    assert create_ticket_kwargs == expected_create_ticket
