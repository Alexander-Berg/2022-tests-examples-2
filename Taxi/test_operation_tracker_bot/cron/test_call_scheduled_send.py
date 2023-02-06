# pylint: disable=redefined-outer-name

import collections

import pytest

from operation_tracker_bot.generated.cron import run_cron


@pytest.mark.config(
    OPERATION_TRACKER_BOT_TARIFF_QUEUES=[
        {'name': 'TEST', 'statuses': ['approved']},
    ],
    OPERATION_TRACKER_BOT_TARIFF_GROUPS=[100500],
    OPERATION_TRACKER_BOT_TARIFF_MAIN_CONF={
        'only_last_calls': True,
        'regexp': '(?:[Сс]озда|[Оо]тредактирова).* черновик',
        'summoner_name': 'amneziya',
    },
)
async def test_calls_scheduled_send(mockserver, patch):
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

    last_cron = '2021-04-06T15:33:11.540000+03:00'
    expected_date_from = '2021-04-06T15:32:11.540000+03:00'

    @patch(
        'operation_tracker_bot.internal.cron.SimpleCronsClient.get_tasks_list',
    )
    async def _list(*args, **kwargs):
        return {
            'tasks': [
                {
                    'is_enabled': True,
                    'last_launches': [
                        {
                            'id': '7845b6dc42ee4091ae55dc9849bd3bb6',
                            'launch_status': 'finished',
                            'start_time': last_cron,
                        },
                    ],
                    'name': (
                        'operation_tracker_bot-crontasks-calls_scheduled_send'
                    ),
                    'service': 'operation_tracker_bot',
                    'monitoring_status': 'ok',
                },
            ],
        }

    @patch('taxi.clients.startrack.StartrackAPIClient.search')
    async def _search(*args, **kwargs):
        assert kwargs['json_filter']['updated']['from'] == expected_date_from
        return [{'key': 'TEST-1'}]

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _comments(*args, **kwargs):
        return [
            {
                'id': 124076883,
                'longId': '606c622adc0a211beb20a316',
                'text': 'Создала черновик',
                'createdBy': {
                    'id': 'amneziya',
                    'display': 'Алиса Лаврентьева',
                },
                'updatedBy': {
                    'id': 'amneziya',
                    'display': 'Алиса Лаврентьева',
                },
                'summonees': [
                    {'id': 'amneziya', 'display': 'Алиса Лаврентьева'},
                ],
                'createdAt': last_cron,
                'updatedAt': last_cron,
                'version': 1,
                'type': 'standard',
                'transport': 'internal',
            },
        ]

    sent_messages = collections.defaultdict(list)

    @patch('operation_tracker_bot.internal.telegram.ProxiedBot.send_message')
    async def _send(chat_id, text, **kwargs):
        sent_messages[chat_id].append(text)

    await run_cron.main(
        ['operation_tracker_bot.crontasks.calls_scheduled_send', '-t', '0'],
    )
    assert sent_messages == {
        100500: [
            '@beli4i\nВас призвали в тикете:'
            ' https://st.yandex-team.ru/TEST-1\nСоздала черновик',
        ],
    }
