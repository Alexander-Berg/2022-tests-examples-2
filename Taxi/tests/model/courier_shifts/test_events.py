import pytest


@pytest.mark.parametrize('shift_events', [
    [{'type': 'started'}, {'type': 'paused'}],
    [{'type': 'started'}, {'type': 'paused'}, {'type': 'accepted'}],
])
async def test_event_paused_exist(tap, dataset, shift_events):
    with tap.plan(2, 'пауза начата'):
        store = await dataset.store()
        shift = await dataset.courier_shift(
            store=store,
            shift_events=shift_events,
        )

        event = shift.event_paused()

        tap.ok(event, 'событие получено')
        tap.eq(event.type, 'paused', 'пауза получена')


@pytest.mark.parametrize('shift_events', [
    [],
    [{'type': 'paused'}, {'type': 'unpaused'}],
    [{'type': 'paused'}, {'type': 'accepted'}, {'type': 'unpaused'}],
    [{'type': 'paused'}, {'type': 'stopped'}],
    [{'type': 'paused'}, {'type': 'complete'}],
    [{'type': 'paused'}, {'type': 'cancelled'}],
])
async def test_event_paused_none(tap, dataset, shift_events):
    with tap.plan(1, 'пауза не начата'):
        store = await dataset.store()
        shift = await dataset.courier_shift(
            store=store,
            shift_events=shift_events,
        )

        event = shift.event_paused()

        tap.eq(event,  None, 'события нет')


async def test_get_all_pauses(tap, dataset):
    with tap.plan(10, 'получение всех пауз на смене'):
        store = await dataset.store()
        shift = await dataset.courier_shift(
            store=store,
            shift_events=[
                {'type': 'paused'},
                {'type': 'unpaused'},

                {'type': 'schedule_pause'},
                {'type': 'paused'},
                {'type': 'unpaused'},

                {'type': 'paused'},
            ],
        )

        pauses = shift.get_all_pauses()
        tap.eq(len(pauses), 3, 'три паузы на смене')

        tap.ok(not pauses[0].get('schedule_pause'),
               'not pauses.0.schedule_pause')
        tap.ok(pauses[0].get('paused'),
               'pauses.0.paused')
        tap.ok(pauses[0].get('unpaused'),
               'pauses.0.unpaused')

        tap.ok(pauses[1].get('schedule_pause'),
               'pauses.1.schedule_pause')
        tap.ok(pauses[1].get('paused'),
               'pauses.1.paused')
        tap.ok(pauses[1].get('unpaused'),
               'pauses.1.unpaused')

        tap.ok(not pauses[2].get('schedule_pause'),
               'not pauses.2.schedule_pause')
        tap.ok(pauses[2].get('paused'),
               'pauses.2.paused')
        tap.ok(not pauses[2].get('unpaused'),
               'pauses.2.unpaused')
