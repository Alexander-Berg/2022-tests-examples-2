from taxi_support_chat.generated.stq3 import stq_context
from taxi_support_chat.stq import stq_task


async def test_create_chatterbox_task(
        stq3_context: stq_context.Context, mock_chatterbox_tasks,
):
    chat_id = '5baa0afee4a40b001d682510'
    add_fields = {'owner_phone': '+7999999999'}
    await stq_task.create_chatterbox_task(
        context=stq3_context, chat_id=chat_id, metadata=add_fields,
    )
    assert mock_chatterbox_tasks.calls[0] == {
        'kwargs': {
            'external_id': chat_id,
            'add_fields': {'owner_phone': '+7999999999'},
            'add_tags': None,
            'delete_tags': None,
            'hidden_comment': None,
            'task_type': 'chat',
            'log_extra': None,
        },
    }
