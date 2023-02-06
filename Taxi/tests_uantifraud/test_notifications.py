import pytest


async def test_sample_notification(stq_runner, mockserver):
    @mockserver.json_handler('/taxi-antifraud/v1/send_telegram_message')
    def _mock_send_message(request):
        return {}

    await stq_runner.antifraud_notifications_sending.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'chat_id': 'some_chat',
            'text': 'Some message',
            'bot_id': 'some_bot',
        },
    )

    assert _mock_send_message.times_called == 1
    assert _mock_send_message.next_call()['request'].json == {
        'chat_id': 'some_chat',
        'text': 'Some message',
        'bot_id': 'some_bot',
    }


@pytest.mark.parametrize('code', [400, 500])
async def test_fail_notification(stq_runner, mockserver, code):
    @mockserver.json_handler('/taxi-antifraud/v1/send_telegram_message')
    def _mock_send_message(request):
        return mockserver.make_response(status=code)

    await stq_runner.antifraud_notifications_sending.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'chat_id': 'some_chat',
            'text': 'Some message',
            'bot_id': 'some_bot',
        },
        expect_fail=True,
    )
