import pytest

from stall.model.courier_shift import CourierShiftEvent


@pytest.mark.parametrize('target_status', ['complete', 'leave'])
async def test_simple(tap, api, dataset, uuid, target_status):
    with tap.plan(10, f'Попытка закрыть смену в статус "{target_status}"'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store = await dataset.store(company=company, cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        event_started_id = uuid()
        shift = await dataset.courier_shift(
            store=store,
            status='processing',
            courier=courier,
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': event_started_id,
                    'type': 'started',
                }),
            ],
        )

        t = await api(token=company.token)
        await t.post_ok('api_external_courier_shifts_stop', json={
            'id': courier.external_id,
            'status': target_status,
            'ticket': 'LAVKADEV-4917',
            'support_login': 'alexeypoloz',
        })
        t.status_is(200, diag=True)
        t.json_is('current_slot_shift_id', shift.courier_shift_id, 'ID')

        await shift.reload()
        tap.eq(shift.status, target_status, 'смена закрыта')
        tap.eq(len(shift.shift_events), 3, '+2 новых события')

        event = shift.shift_events[-2]
        tap.eq(
            event.shift_event_id,
            f'{event_started_id}:stopped',
            'started shift_event_id'
        )
        tap.eq(event.type, 'stopped', 'событие stopped')
        tap.eq(event.detail['ticket'], 'LAVKADEV-4917', 'Тикет саппорта')
        tap.eq(event.detail['support_login'], 'alexeypoloz', 'Логин саппорта')

        event = shift.shift_events[-1]
        tap.eq(event.type, target_status, 'событие изменения статуса')
