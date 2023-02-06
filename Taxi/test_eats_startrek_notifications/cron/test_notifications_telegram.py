# pylint: disable=redefined-outer-name
# pylint: disable=unused-variable
import pytest

from eats_startrek_notifications.generated.cron import run_cron


@pytest.mark.config(
    EATS_STARTREK_NOTIFICATIONS_SETTINGS={
        'telegram_notifications': [
            {
                'telegram_chat_id': '288478886',
                'startrek_filter': 'Queue: "Очередь" Status: "В работе"',
                'message_template': (
                    '@{issue_assignee_telegram}\n`test` **message**'
                ),
                'restart_timedelta': '1d 1h 1m',
            },
        ],
    },
)
@pytest.mark.parametrize('count_crontasks', [1, 2])
async def test_notifications_telegram(
        cron_context, mockserver, patch_get_startrack_tickets, count_crontasks,
):
    @mockserver.json_handler('/staff/v3/persons', prefix=True)
    def handler_persons_telegram(request):
        return {
            'links': {},
            'page': 1,
            'limit': 50,
            'result': [
                {
                    'telegram_accounts': [
                        {
                            'value': 'TestLoginTG',
                            'value_lower': 'testlogintg',
                            'private': False,
                            'id': 0,
                        },
                    ],
                    'login': 'testloginstaff',
                },
            ],
            'total': 1,
            'pages': 1,
        }

    @mockserver.json_handler(
        '/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/sendMessage',
    )
    def _get_send_message(request):
        return {'ok': True}

    tickets = [
        {
            'key': 'TEST-1',
            'summary': 'summary 1',
            'assignee': {'display': 'Name', 'id': 'testloginstaff'},
        },
        {'key': 'TEST-2', 'summary': 'summary 2'},
    ]

    patch_get_startrack_tickets(tickets)

    for _ in range(count_crontasks):
        await run_cron.main(
            [
                'eats_startrek_notifications.crontasks.notifications_telegram',
                '-t',
                '0',
            ],
        )

    async with cron_context.pg.master.acquire() as connection:
        count_filters = await connection.fetchval(
            'select count(*) from filters',
        )
        assert count_filters == 1

        count_notifications = await connection.fetchval(
            'select count(*) from notifications',
        )
        assert count_notifications == len(tickets)
