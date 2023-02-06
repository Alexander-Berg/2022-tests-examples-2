# pylint: disable=redefined-outer-name,unused-variable
import bson
import pytest

from taxi_support_chat.generated.stq3 import stq_context
from taxi_support_chat.stq import stq_task


@pytest.mark.config(SUPPORT_CHAT_EATS_APP_COUNT_PUSH=True)
@pytest.mark.parametrize(
    (
        'chat_id',
        'message_id',
        'status',
        'expected_request_calls',
        'zero_messages',
    ),
    [
        (
            bson.ObjectId('5a436ca8779fb3302cc784ea'),
            'support_to_eats_1',
            200,
            2,
            False,
        ),
        (
            bson.ObjectId('5a436ca8779fb3302cc222ea'),
            'support_to_eats_2',
            200,
            0,
            False,
        ),
        (
            bson.ObjectId('5a436ca8779fb3302cc784ea'),
            'support_to_eats_1',
            500,
            2,
            False,
        ),
        (
            bson.ObjectId('5a436ca8779fb3302cc222ea'),
            'support_to_eats_2',
            200,
            1,
            True,
        ),
    ],
)
async def test_task(
        patch_aiohttp_session,
        monkeypatch,
        response_mock,
        stq3_context: stq_context.Context,
        chat_id,
        message_id,
        status,
        expected_request_calls,
        zero_messages,
        mockserver,
):
    @mockserver.json_handler('/eda-api/internal-api/v1/chat/push')
    def mock_eats_push(request):
        return mockserver.make_response(status=status)

    @mockserver.json_handler('/eda-api/internal-api/v1/chat/messages/count')
    def mock_eats_messages_count(request):
        return mockserver.make_response(status=status)

    await stq_task.eats_app_notify_task(
        stq3_context, chat_id, message_id, zero_messages=zero_messages,
    )

    assert (
        mock_eats_push.times_called + mock_eats_messages_count.times_called
        == expected_request_calls
    )
