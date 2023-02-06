from stall.model.courier_shift_schedule import CourierShiftSchedule


async def test_simple(tap, dataset, now):
    with tap.plan(17, 'Операции сохранения / загрузки / удаления'):
        store = await dataset.store()

        schedule = CourierShiftSchedule({
            'store_id': store.store_id,
            'company_id': store.company_id,
        })
        tap.ok(schedule, 'инстанцирован')

        tap.eq(
            schedule.courier_shift_schedule_id,
            None,
            'идентификатора до сохранения нет'
        )
        tap.ok(await schedule.save(), 'сохранен')
        tap.ok(schedule.courier_shift_schedule_id, 'идентификатор назначился')
        schedule_id = schedule.courier_shift_schedule_id

        tap.eq(schedule.time_till, None, 'time_till нет')
        tap.eq(schedule.vars.get('total', None), None, 'vars.total нет')
        time = now().replace(microsecond=0)
        schedule.time_till = time
        schedule.vars['total'] = 1
        tap.ok(await schedule.save(), 'сохранен еще раз')
        tap.eq(
            schedule.courier_shift_schedule_id,
            schedule_id,
            'идентификатор не поменялся'
        )
        tap.eq(schedule.time_till, time, 'time_till сохранено верно')
        tap.eq(schedule.vars['total'], 1, 'vars.total сохранено верно')

        loaded = await CourierShiftSchedule.load(schedule_id)
        tap.ok(loaded, 'загружено')
        tap.isa_ok(loaded, CourierShiftSchedule, 'тип')
        tap.eq(loaded.time_till, schedule.time_till, 'time_till загружено')
        tap.eq(
            loaded.vars['total'],
            schedule.vars['total'],
            'vars.total загружено'
        )
        tap.eq(
            loaded.courier_shift_schedule_id,
            schedule.courier_shift_schedule_id,
            'id'
        )

        tap.ok(await schedule.rm(), 'удалён')
        tap.ok(not await CourierShiftSchedule.load(schedule_id), 'удалён в БД')
