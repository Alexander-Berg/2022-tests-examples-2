# pylint: disable=redefined-outer-name
import collections

import pytest

from operation_tracker_bot.generated.cron import run_cron


@pytest.mark.config(
    OPERATION_TRACKER_BOT_TRACKER_USERS={
        'amneziya': {'queues': [{'name': 'TEST'}]},
    },
    OPERATION_TRACKER_BOT_TRACKER_GROUPS=[100500],
)
async def test_tracker_scheduled_send(mockserver, patch):
    sent_messages = collections.defaultdict(list)

    @mockserver.json_handler('/client-staff/v3/persons')
    def _handler(request):
        return mockserver.make_response(
            json={
                'accounts': [
                    {
                        'id': 60939,
                        'private': False,
                        'type': 'telegram',
                        'value': 'beli4i',
                        'value_lower': 'beli4i',
                    },
                ],
                'login': 'amneziya',
                'name': {
                    'first': {
                        'en': 'Alisa',
                        'ru': '\u0410\u043b\u0438\u0441\u0430',
                    },
                    'last': {'en': 'Lavrentyeva', 'ru': 'Лаврентьева'},
                    'middle': '',
                },
                'official': {'is_dismissed': False},
            },
        )

    @patch('taxi.clients.startrack.StartrackAPIClient.search')
    async def _search(*args, **kwargs):
        return [{'key': 'TEST-1'}]

    @patch('operation_tracker_bot.internal.telegram.ProxiedBot.send_message')
    async def _send(chat_id, text, **kwargs):
        sent_messages[chat_id].append(text)

    await run_cron.main(
        ['operation_tracker_bot.crontasks.tracker_scheduled_send', '-t', '0'],
    )
    assert sent_messages == {
        100500: ['@beli4i\nhttps://st.yandex-team.ru/TEST-1\n'],
    }
