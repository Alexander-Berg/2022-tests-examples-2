# pylint: disable=protected-access
import pytest

from taxi_support_chat.generated.stq3 import stq_context
from taxi_support_chat.stq import stq_task


@pytest.mark.parametrize(
    'args, expected_webhook_data, expected_create_task, expected_no_call',
    [
        (
            [
                'test_pd_id_call-session-id-0001',
                {
                    'message_id': 'msg-id-0001',
                    'user_phone': '+79001234567',
                    'contact_point_id': '88001000200',
                    'call_id': 'call-session-id-0001',
                    'user_name': None,
                    'call_record_id': None,
                    'message_input': None,
                    'timestamp': '2022-01-14T14:46:12+0000',
                },
                'ABONENT_HANGUP',
            ],
            {
                'source': 'ivr',
                'id': 'call-session-id-0001',
                'direction': 'incoming',
                'num_from': '+79001234567',
                'num_to': '88001000200',
                'hangup_disposition': 'caller_bye',
                'completed_at': '2022-01-14T14:46:12+0000',
            },
            {},
            False,
        ),
        (
            [
                'test_pd_id_call-session-id-0002',
                {
                    'message_id': 'msg-id-0002',
                    'user_phone': '+79001234567',
                    'contact_point_id': '+74950328686',
                    'call_id': 'call-session-id-0002',
                    'user_name': None,
                    'call_record_id': None,
                    'message_input': None,
                    'timestamp': '2022-01-14T14:46:12+0000',
                },
                None,
            ],
            {
                'direction': 'incoming',
                'id': 'call-session-id-0002',
                'num_from': '+79001234567',
                'hangup_disposition': 'callee_bye',
                'num_to': '+74950328686',
                'answered_at': '2018-07-18T11:20:00+0000',
                'completed_at': '2022-01-14T14:46:12+0000',
                'source': 'ivr',
            },
            {},
            True,
        ),
    ],
)
async def test_stq_hangup_process(
        stq3_context: stq_context.Context,
        args,
        expected_webhook_data,
        expected_create_task,
        expected_no_call,
        stq,
        mock_chatterbox_py3,
):
    @mock_chatterbox_py3('/v1/webhooks/chatterbox_id/call_with_tvm/')
    def _v1_webhooks_task_id_call_with_tvm_post(request):
        assert 'chatterbox_id' in request.path
        assert request.json == expected_webhook_data
        return {}

    await stq_task.handle_logbroker_hangup(stq3_context, *args)

    if expected_webhook_data:
        assert _v1_webhooks_task_id_call_with_tvm_post.times_called == 1

    if expected_no_call:
        chat_doc = await stq3_context.mongo.user_chat_messages.find_one(
            {'messages.id': args[1]['message_id']},
        )
        assert not chat_doc['open']
        assert not chat_doc['visible']
        assert stq.support_chat_create_chatterbox_task.next_call()
