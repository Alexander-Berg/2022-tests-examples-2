# coding: utf-8
import pytest

from taxi.external import telegram_bot


@pytest.mark.parametrize(
    'request_message, right_result',
    [
        ('ab', ['ab']),
        (('a' * 4000 + '\n' + 'b' * 4000), ['a' * 4000, 'b' * 4000]),
        (('a' * 4000 + ' ' + 'b' * 4000), ['a' * 4000, 'b' * 4000]),
        (('a' * 4095 + 'b' * 4000), ['a' * 4095 + 'b', 'b' * 3999]),
        ((u'ы' * 4095 + u'ф' * 4000), [u'ы' * 4095 + u'ф', u'ф' * 3999]),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_send_message(patch, request_message, right_result):
    test_result = []

    @patch('telegram.Bot.send_message')
    def send_message(*args, **kwargs):
        message = args[1]
        if len(message) > 4096:
            raise ValueError
        test_result.append(message)

    yield telegram_bot.send_message('some_chat_id', request_message)

    assert test_result == right_result


@pytest.mark.parametrize(
    'message_count,result, message',
    [
        (0, [], u'сообщение_{}'),
        (0, [], 'message___{}'),
        (1, [11], u'сообщение_{}'),
        (1, [11], 'message___{}'),
        (400, [4091, 1399], u'сообщение_{}'),
        (400, [4091, 1399], 'message___{}'),
        (800, [4091, 4087, 2911], u'сообщение_{}'),
        (800, [4091, 4087, 2911], 'message___{}'),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_send_multi_messages(patch, message_count, result, message):
    test_result = []

    @patch('telegram.Bot.send_message')
    def send_message(*args, **kwargs):
        message = args[1]
        if len(message) > 4096:
            raise ValueError

        test_result.append(len(message))

    messages = [message.format(i) for i in range(1, message_count + 1)]
    yield telegram_bot.send_multi_messages('some_chat_id', messages)

    assert test_result == result, test_result
