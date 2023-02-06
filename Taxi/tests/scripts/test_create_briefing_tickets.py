import datetime as dt
import pytest

from aiohttp import web

from stall.scripts.create_briefing_tickets import CreateBriefingTickets
from stall.client.staff import StaffClient
from stall.client.tracker import TrackerClient
from stall.model.briefing_tickets import BriefingTickets

NEW_TICKET = 'LAVKAOT-004'


def get_date(days_ago):
    return dt.datetime.strftime(
        dt.datetime.now() - dt.timedelta(days=days_ago),
        '%Y-%m-%d'
    )


# pylint: disable=too-many-locals, unused-argument
async def test_create_first_tickets(tap, dataset, uuid, ext_api):
    requests = []

    async def handler(request):
        requests.append(request)
        test_uid = uuid()
        _id = uuid()
        join_at = get_date(days_ago=3)
        is_dismissed = False
        if len(requests) == 1:
            return web.json_response(
                {
                    'result': [{
                        'chief': {'login': 'chief'},
                        'id': _id,
                        'uid': test_uid,
                        'login': 'login',
                        'official': {
                            'is_dismissed': is_dismissed,
                            'join_at': join_at,
                            'position': {
                                'ru': 'Директор склада',
                            }
                        },
                        'work_email': 'login@yandex-team.ru',
                        'name': {
                            'last': {'ru': 'login'},
                            'first': {'ru': 'login'}
                        }
                    }]
                }
            )
        if len(requests) == 2:
            return web.json_response(
                {
                    'result': []
                }
            )

    async def tracker_handler(request):
        return web.json_response(
            {
                'key': NEW_TICKET,
                'createdAt': f'{get_date(days_ago=0)}T00:00:00.000+03:00'
            },
            status=201,
        )

    staff_client = StaffClient()
    tracker = TrackerClient()
    with tap.plan(6, 'Создаем first_briefing тикет новеньким'):
        async with await ext_api(staff_client, handler) as client:
            staff_users = await client.get_users_by_query(
                fields=[],
                query='',
            )

            users = [await dataset.briefing_ticket(staff_uid=uid)
                     for uid, _ in staff_users.items()]

            tap.eq_ok(len(users), 1, 'Пользователь создан')
            uid = users[0].staff_uid

            bt = CreateBriefingTickets()
            need_tickets = await bt.users_that_need_tickets(staff_users)
            tap.eq_ok(len(need_tickets), 1,
                      'Только одному пользавателю нужен тикет')
            info = need_tickets[uid]
            tap.ok(
                'first_briefing' in info['ticket_types'],
                'нужно создать first_briefing'
            )
        async with await ext_api(tracker, tracker_handler) as client:
            tap.ok(await client.create_briefing(need_tickets), 'Создали тикеты')

            user = await BriefingTickets.load(
                uid,
                by='staff_uid'
            )
            tap.eq(
                len(user.created_tickets),
                1,
                'created_tickets пользователя появился один briefing_tickets'
            )
            tap.ok(
                'first_briefing' in user.created_tickets,
                'vars пользователя появился first_briefing'
            )


@pytest.mark.parametrize(
    'tickets', [
        {
            'first_briefing': {
                'last_date': get_date(days_ago=400),
                'ticket': 'LAVKAOT-002'
            },

        },
        {
            'first_briefing': {
                'last_date': get_date(days_ago=400),
                'ticket': 'LAVKAOT-002'
            },
            'workplace_briefing': {
                'last_date': get_date(days_ago=400),
                'ticket': 'LAVKAOT-003'
            },
        }
    ],
)
async def test_workplace_briefing(tap, dataset, uuid, ext_api, tickets):
    requests = []

    async def handler(request):
        requests.append(request)
        test_uid = uuid()
        _id = uuid()
        join_at = get_date(days_ago=10)
        is_dismissed = False
        if len(requests) == 1:
            return web.json_response(
                {
                    'result': [{
                        'chief': {'login': 'chief'},
                        'id': _id,
                        'uid': test_uid,
                        'login': 'login',
                        'official': {
                            'is_dismissed': is_dismissed,
                            'join_at': join_at,
                            'position': {
                                'ru': 'Директор склада',
                            }
                        },
                        'work_email': 'login@yandex-team.ru',
                        'name': {
                            'last': {'ru': 'login'},
                            'first': {'ru': 'login'}
                        }
                    }]
                }
            )
        if len(requests) == 2:
            return web.json_response(
                {
                    'result': []
                }
            )
    client = StaffClient()

    with tap.plan(8, 'Если у пользователя не было тикетов - создаем'):
        async with await ext_api(client, handler) as client:
            staff_users = await client.get_users_by_query(
                fields=[],
                query='',
            )

            users = [await dataset.briefing_ticket(
                staff_uid=uid,
                created_tickets=tickets,
            )
                     for uid, _ in staff_users.items()]

            tap.eq_ok(len(users), 1, 'Пользоватлеь создан')
            uid = users[0].staff_uid

            bt = CreateBriefingTickets()
            need_tickets = await bt.users_that_need_tickets(staff_users)
            tap.eq_ok(len(need_tickets), 1,
                      'Только одному пользавателю нужен тикет')
            info = need_tickets[uid]
            tap.eq_ok(len(info['ticket_types']), 1, 'один тикет нужно создать')
            tap.ok(
                'workplace_briefing' in info['ticket_types'],
                'нужно создать workplace_briefing'
            )

            async def tracker_handler(request):
                return web.json_response(
                    {
                        'key': NEW_TICKET,
                        'createdAt':
                            f'{get_date(days_ago=0)}T00:00:00.000+03:00'
                    },
                    status=201,
                )
            tracker = TrackerClient()

            async with await ext_api(tracker, tracker_handler) as client:
                tap.ok(await client.create_briefing(need_tickets),
                       'Создали тикеты')

                user = await BriefingTickets.load(
                    uid,
                    by='staff_uid'
                )
                tap.eq(
                    len(user.created_tickets),
                    2,
                    'два тикета'
                )
                tap.ok(
                    'workplace_briefing' in user.created_tickets,
                    'создан workplace_briefing'
                )

                tap.ok(
                    user.created_tickets['workplace_briefing']['last_date']
                    > get_date(days_ago=1),
                    'Дата стоит новая'
                )


async def test_dont_create(tap, dataset, uuid, ext_api):
    requests = []

    async def handler(request):
        requests.append(request)
        test_uid = uuid()
        _id = uuid()
        join_at = get_date(days_ago=10)
        is_dismissed = False
        if len(requests) == 1:
            return web.json_response(
                {
                    'result': [{
                        'chief': {'login': 'chief'},
                        'id': _id,
                        'uid': test_uid,
                        'login': 'login',
                        'official': {
                            'is_dismissed': is_dismissed,
                            'join_at': join_at,
                            'position': {
                                'ru': 'Директор склада',
                            }
                        },
                        'work_email': 'login@yandex-team.ru',
                        'name': {
                            'last': {'ru': 'login'},
                            'first': {'ru': 'login'}
                        }
                    }]
                }
            )
        if len(requests) == 2:
            return web.json_response(
                {
                    'result': []
                }
            )
    client = StaffClient()

    with tap.plan(2, 'Если у пользователя не подошел срок не создаем тикет'):
        async with await ext_api(client, handler) as client:
            staff_users = await client.get_users_by_query(
                fields=[],
                query='',
            )

            users = [await dataset.briefing_ticket(
                staff_uid=uid,
                created_tickets={
                    'first_briefing': {
                        'last_date': get_date(days_ago=1),
                        'ticket': 'LAVKAOT-002'
                    },
                },
            )
                     for uid, _ in staff_users.items()]

            tap.eq_ok(len(users), 1, 'Пользоватлеь создан')

            bt = CreateBriefingTickets()
            need_tickets = await bt.users_that_need_tickets(staff_users)
            tap.eq_ok(len(need_tickets), 0,
                      'Никому не нужен тикет')


# pylint: disable=too-many-locals, unused-argument
async def test_create_user_in_db(tap, dataset, uuid, ext_api):
    requests = []
    test_uid = uuid()
    test_login = 'login'
    async def handler(request):
        requests.append(request)
        _id = uuid()
        join_at = get_date(days_ago=3)
        is_dismissed = False
        if len(requests) == 1:
            return web.json_response(
                {
                    'result': [{
                        'chief': {'login': 'chief'},
                        'id': _id,
                        'uid': test_uid,
                        'login': test_login,
                        'official': {
                            'is_dismissed': is_dismissed,
                            'join_at': join_at,
                            'position': {
                                'ru': 'Директор склада',
                            }
                        },
                        'work_email': 'login@yandex-team.ru',
                        'name': {
                            'last': {'ru': 'login'},
                            'first': {'ru': 'login'}
                        }
                    }]
                }
            )
        if len(requests) == 2:
            return web.json_response(
                {
                    'result': []
                }
            )

    async def tracker_handler(request):
        return web.json_response(
            {
                'key': NEW_TICKET,
                'createdAt': f'{get_date(days_ago=0)}T00:00:00.000+03:00'
            },
            status=201,
        )

    staff_client = StaffClient()
    tracker = TrackerClient()
    with tap.plan(8, 'Создаем first_briefing тикет новеньким'):
        async with await ext_api(staff_client, handler) as client:
            staff_users = await client.get_users_by_query(
                fields=[],
                query='',
            )

            tap.eq_ok(len(staff_users), 1, 'Пользоватлеь создан')

            bt = CreateBriefingTickets()
            need_tickets = await bt.users_that_need_tickets(staff_users)
            tap.eq_ok(len(need_tickets), 1,
                      'Только одному пользавателю нужен тикет')
            info = need_tickets[test_uid]

            tap.ok(
                'first_briefing' in info['ticket_types'],
                'нужно создать first_briefing'
            )
        async with await ext_api(tracker, tracker_handler) as client:
            tap.ok(await client.create_briefing(need_tickets), 'Создали тикеты')

            user = await BriefingTickets.load(
                test_uid,
                by='staff_uid'
            )
            tap.ok(user, 'Пользовтаель создан')
            tap.eq(user.staff_login, test_login, 'Правильный логин')

            tap.eq(
                len(user.created_tickets),
                1,
                'created_tickets пользователя появился один briefing_tickets'
            )
            tap.ok(
                'first_briefing' in user.created_tickets,
                'vars пользователя появился first_briefing'
            )

