# pylint: disable=unused-variable


async def test_list_empty(api, tap, dataset):
    with tap.plan(5):
        store   = await dataset.store()
        user    = await dataset.user(store=store)

        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shift_schedules_list',
                json={}
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_is('courier_shift_schedules', [])


async def test_list_nonempty(api, dataset, tap):
    with tap.plan(16, 'Не пустой список'):
        company1 = await dataset.company()
        company2 = await dataset.company()

        store1 = await dataset.store(company=company1)
        store2 = await dataset.store(company=company2)

        schedule1 = await dataset.courier_shift_schedule(store=store1)
        schedule2 = await dataset.courier_shift_schedule(store=store2)

        shift1 = await dataset.courier_shift(courier_shift_schedule=schedule1)
        shift2 = await dataset.courier_shift(courier_shift_schedule=schedule2)

        user    = await dataset.user(store=store1)
        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shift_schedules_list',
                json={}
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_has('courier_shift_schedules')
            t.json_has('courier_shift_schedules.0')
            t.json_hasnt('courier_shift_schedules.1')

            t.json_has('courier_shift_schedules.0.courier_shift_schedule_id')
            t.json_has('courier_shift_schedules.0.time_till')
            t.json_has('courier_shift_schedules.0.vars')

            await t.post_ok(
                'api_admin_courier_shift_schedules_list',
                json={'cursor': t.res['json']['cursor']},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_has('courier_shift_schedules')
            t.json_hasnt('courier_shift_schedules.0')


async def test_list_none_store_company(tap, api, dataset):
    with tap.plan(6, 'Фильтрация для юзера без лавки и без компании'):
        schedule = await dataset.courier_shift_schedule()
        await dataset.courier_shift(courier_shift_schedule=schedule)

        user = await dataset.user(store_id=None, company_id=None)
        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shift_schedules_list',
                json={}
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')
            t.json_has('courier_shift_schedules')
            t.json_hasnt('courier_shift_schedules.0')


async def test_list_store_none(tap, api, dataset):
    with tap.plan(6, 'Фильтрация для юзера без лавки, но с пермитом'):
        company1 = await dataset.company()
        store1 = await dataset.store(company=company1)

        # свой
        schedule1 = await dataset.courier_shift_schedule(store=store1)

        # пользователя без лавки, но из своей компании
        schedule2 = await dataset.courier_shift_schedule(
            store_id=None,
            company_id=company1.company_id,
        )

        # чужой
        schedule3 = await dataset.courier_shift_schedule()

        await dataset.courier_shift(courier_shift_schedule=schedule1)
        await dataset.courier_shift(courier_shift_schedule=schedule2)
        await dataset.courier_shift(courier_shift_schedule=schedule3)

        user = await dataset.user(store_id=None, company_id=company1.company_id)
        with user.role as role:
            # разрешен доступ ко всем расписаниям (в том числе без store_id)
            role.add_permit('out_of_store', True)
            # но только своя компания
            role.remove_permit('out_of_company')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_courier_shift_schedules_list',
                json={}
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('cursor')

            tap.eq(len(t.res['json']['courier_shift_schedules']), 2, 'оба')

            res = t.res['json']['courier_shift_schedules']
            tap.eq_ok(
                sorted([res[0]['courier_shift_schedule_id'],
                        res[1]['courier_shift_schedule_id']]),
                sorted([schedule1.courier_shift_schedule_id,
                        schedule2.courier_shift_schedule_id]),
                'Пришли правильные объекты'
            )
