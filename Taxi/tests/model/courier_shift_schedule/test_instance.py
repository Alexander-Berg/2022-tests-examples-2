async def test_instance(tap, dataset, now, uuid):
    with tap.plan(8):
        store = await dataset.store()

        external_id = uuid()
        time = now().replace(microsecond=0)

        schedule = dataset.CourierShiftSchedule({
            'external_id': external_id,
            'store_id': store.store_id,
            'company_id': store.company_id,
            'schedule': [
                {'tags': ['test1'], 'time': time},
            ],
            'time_till': time,
            'vars': {
                'total': 1,
            },
        })

        tap.ok(schedule, 'Объект создан')
        tap.eq(schedule.external_id, external_id, 'external_id')
        tap.eq(schedule.time_till, time, 'time_till')
        tap.eq(schedule.vars['total'], 1, 'vars.total')

        tap.ok(await schedule.save(), 'сохранение')
        tap.ok(await schedule.save(), 'обновление')

        tap.eq(schedule.schedule[0]['tags'], ['test1'], 'tags')
        tap.eq(schedule.schedule[0]['time'], time, 'time')


async def test_dataset(tap, dataset):
    with tap.plan(1):
        store = await dataset.store()
        schedule = await dataset.courier_shift_schedule(
            store=store
        )
        tap.ok(schedule, 'Объект создан')
