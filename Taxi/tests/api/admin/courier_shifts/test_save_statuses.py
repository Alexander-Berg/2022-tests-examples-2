import pytest

from stall.model.courier_shift import COURIER_SHIFT_STATUSES


@pytest.mark.parametrize('init_status', COURIER_SHIFT_STATUSES)
async def test_cancel_forbidden(tap, api, dataset, init_status):
    with tap.plan(5, f'Попытка отменить смену в статусе "{init_status}"'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        shift = await dataset.courier_shift(
            store=store,
            status=init_status
        )

        with user.role as role:
            # НЕ имеет право отменять
            role.remove_permit('courier_shifts_cancel')

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_save',
                            json={
                                'courier_shift_id': shift.courier_shift_id,
                                'status': 'cancelled',
                            })

            tap.ok(await shift.reload(), 'смена reloaded')

            if init_status in ('request', 'template', 'waiting', 'processing'):
                # нет прав для отмены
                t.status_is(403, diag=True)
                t.json_is('code', 'ER_ACCESS')
            else:
                # смена не в том статусе, чтобы ее можно было вообще менять
                t.status_is(429, diag=True)
                t.json_is('code', 'ER_COURIER_SHIFT_RO')

            tap.eq(shift.status, init_status, 'смена не изменилась')


@pytest.mark.parametrize(
    'init_status',
    ['template', 'request', 'waiting', 'processing']
)
async def test_cancel_granted(tap, api, dataset, init_status):
    with tap.plan(5, f'Отменяем смену в статусе "{init_status}"'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        shift = await dataset.courier_shift(
            store=store,
            status=init_status
        )

        with user.role as role:
            # имеет право отменять
            role.add_permit('courier_shifts_cancel', True)

            t = await api(user=user)
            await t.post_ok('api_admin_courier_shifts_save',
                            json={
                                'courier_shift_id': shift.courier_shift_id,
                                'status': 'cancelled',
                            })

            tap.ok(await shift.reload(), 'смена reloaded')
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            tap.eq(shift.status, 'cancelled', 'смена отменена')


async def test_save_update_status_err(tap, api, dataset):
    with tap.plan(3, 'Обновление смены не в том статусе'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        cs_target = await dataset.courier_shift(
            store=store,
            delivery_type='car',
            status='released'
        )

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': cs_target.courier_shift_id,
                            'delivery_type': 'rover',
                        })
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_COURIER_SHIFT_RO')


@pytest.mark.parametrize(
    'status_from,status_to',
    (
        ('template', 'cancelled'),
        ('template', 'request'),
        # ('template', 'waiting'),  см. test_save_machine_to_waiting

        ('request', 'template'),
        # ('request', 'waiting'),   см. test_save_machine_to_waiting
        ('request', 'cancelled'),
        ('request', 'closed'),

        # ('waiting', 'request'),   см. test_save_machine_from_waiting
        ('waiting', 'cancelled'),

        ('processing', 'cancelled'),
    )
)
async def test_admin_state_machine_valid(
        tap, api, dataset, status_from, status_to
):
    with tap.plan(7, 'Правильные переходы в КА админа'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        shift = await dataset.courier_shift(store=store, status=status_from)

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'status': status_to,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await shift.reload()
        event = shift.shift_events[-2]
        tap.eq(event.type, status_to, 'событие о изменении статуса')
        tap.eq(event.user_id, user.user_id, 'user_id')
        event = shift.shift_events[-1]
        tap.eq(event.type, 'edit', 'событие об ручном изменении')
        tap.eq(event.user_id, user.user_id, 'user_id')


@pytest.mark.parametrize('status_from', ('template', 'request'))
async def test_admin_machine_to_waiting(tap, api, dataset, status_from):
    with tap.plan(8, f'Переход из {status_from} в waiting'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift = await dataset.courier_shift(store=store, status=status_from)
        courier = await dataset.courier(cluster=cluster)
        user = await dataset.user(role='admin', store=store)

        t = await api(user=user)

        # статус требует курьера
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'status': 'waiting',
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        # курьер требует статус waiting
        # (хак в ручке обрабатывает этот кейс, поэтому вместо 429, получаем 200)

        # новый курьер + правильный статус
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'status': 'waiting',
                            'courier_id': courier.courier_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await shift.reload()
        tap.eq(shift.status, 'waiting', 'статус обновился')
        tap.eq(shift.courier_id, courier.courier_id, 'курьер сбросился')


@pytest.mark.parametrize(
    'json', (
        # удаление курьера переводит смену в request (обработано в ручке)
        {'courier_id': None},

        # перевод смены в request сбрасывает курьера (обработано в ручке)
        {'status': 'request'},

        # статус верный + курьер сброшен
        {'status': 'request', 'courier_id': None}
    )
)
async def test_admin_machine_from_waiting(tap, api, dataset, json):
    with tap.plan(5, 'Переход из waiting в request'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        shift = await dataset.courier_shift(store=store, status='waiting')

        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)

        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            **json
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await shift.reload()
        tap.eq(shift.status, 'request', 'смена предлагается')
        tap.eq(shift.courier_id, None, 'курьер поменялся')


@pytest.mark.parametrize(
    'status_from,status_to',
    (
        ('template', 'closed'),
        ('template', 'leave'),
        ('template', 'absent'),
        ('template', 'processing'),
        ('template', 'complete'),

        ('request', 'leave'),
        ('request', 'absent'),
        ('request', 'processing'),
        ('request', 'complete'),

        ('waiting', 'template'),
        ('waiting', 'closed'),
        ('waiting', 'leave'),
        ('waiting', 'complete'),
        ('waiting', 'absent'),
    )
)
async def test_admin_machine_invalid(
        tap, api, dataset, status_from, status_to
):
    with tap.plan(3, 'Нарушение переходов в КА админа'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)
        shift = await dataset.courier_shift(store=store, status=status_from)

        t = await api(user=user)
        await t.post_ok('api_admin_courier_shifts_save',
                        json={
                            'courier_shift_id': shift.courier_shift_id,
                            'status': status_to,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
