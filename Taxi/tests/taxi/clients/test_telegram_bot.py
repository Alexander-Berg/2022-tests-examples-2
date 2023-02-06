# pylint: disable=invalid-name, unused-variable
import pytest

from taxi.clients import telegram_bot


TEST_API_KEY = '1234:test_api_key'


@pytest.mark.parametrize(
    'request_message, right_result',
    [
        ('ab', ['ab']),
        (('a' * 4000 + '\n' + 'b' * 4000), ['a' * 4000, 'b' * 4000]),
        (('a' * 4000 + ' ' + 'b' * 4000), ['a' * 4000, 'b' * 4000]),
        (('a' * 4095 + 'b' * 4000), ['a' * 4095 + 'b', 'b' * 3999]),
        (('ы' * 4095 + 'ф' * 4000), ['ы' * 4095 + 'ф', 'ф' * 3999]),
    ],
)
async def test_send_message(loop, patch, request_message, right_result):
    test_result = []

    @patch('telegram.Bot.send_message')
    def send_message(*args, **kwargs):
        message = args[1]
        if len(message) > 4096:
            raise ValueError
        test_result.append(message)

    await telegram_bot.send_message(
        loop, 'some_chat_id', request_message, TEST_API_KEY,
    )

    assert test_result == right_result


@pytest.mark.parametrize(
    'message_count,result, message',
    [
        (0, [], 'сообщение_{}'),
        (0, [], 'message___{}'),
        (1, [11], 'сообщение_{}'),
        (1, [11], 'message___{}'),
        (400, [4091, 1399], 'сообщение_{}'),
        (400, [4091, 1399], 'message___{}'),
        (800, [4091, 4087, 2911], 'сообщение_{}'),
        (800, [4091, 4087, 2911], 'message___{}'),
    ],
)
async def test_send_multi_messages(
        loop, patch, message_count, result, message,
):
    test_result = []

    @patch('telegram.Bot.send_message')
    def send_message(*args, **kwargs):
        message = args[1]
        if len(message) > 4096:
            raise ValueError

        test_result.append(len(message))

    messages = [message.format(i) for i in range(1, message_count + 1)]
    await telegram_bot.send_multi_messages(
        loop, 'some_chat_id', messages, TEST_API_KEY,
    )

    assert test_result == result, test_result
