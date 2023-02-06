from stall.model.briefing_tickets import BriefingTickets


async def test_briefing(tap, uuid):
    with tap.plan(5, 'Создание объекта типа briefing'):
        idstr = uuid()
        ticket = BriefingTickets(
            {
                'staff_uid': idstr,
                'staff_login': 'qwerty',
                'created_tickets': {'tiket': 'ticket'}
            }
        )
        tap.ok(ticket, 'инстанцировано')
        tap.ok(await ticket.save(), 'Сохранено')

        loaded = await BriefingTickets.load(ticket.briefing_tickets_id)
        tap.ok(loaded, f'загружено {loaded.staff_uid}')
        tap.eq(loaded.staff_login, 'qwerty', 'логин')
        tap.ok(loaded.created_tickets, 'тикеты')


async def test_briefing_by_uid(tap, uuid):
    with tap.plan(5, 'Создание объекта типа briefing и поиск по id'):
        idstr = uuid()
        ticket = BriefingTickets(
            {
                'staff_uid': idstr,
                'staff_login': 'qwerty',
                'created_tickets': {'tiket': 'ticket'}
            }
        )
        tap.ok(ticket, 'инстанцировано')
        tap.ok(await ticket.save(), 'Сохранено')

        loaded = await BriefingTickets.load(
            idstr,
            by='staff_uid'
        )
        tap.ok(loaded, f'загружено {loaded.staff_uid}')
        tap.eq(loaded.staff_login, 'qwerty', 'логин')
        tap.ok(loaded.created_tickets, 'тикеты')
