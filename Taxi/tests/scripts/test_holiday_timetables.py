import pytest
from libstall.json_pp import dumps as json
from stall.scripts.holiday_timetable import switch_to_holiday, \
    restore_timetables, HOLIDAY_TIMETABLE_1


async def test_set_restore_store(tap, dataset):
    company = await dataset.company()
    tt1 = [{
        'type': 'monday',
        'begin': '10:00',
        'end': '23:30',
    }]
    store1 = await dataset.store(
        cluster='Москва',
        timetable=tt1,
        company=company,
    )
    tt2 = [
        {
            'type': 'monday',
            'begin': '11:00',
            'end': '20:30',
        },
        {
            'type': 'tuesday',
            'begin': '12:00',
            'end': '20:15',
        },
    ]
    store2 = await dataset.store(
        cluster='Краснодар',
        timetable=tt2,
        company=company,
    )
    tt_israel = [{
        'type': 'everyday',
        'begin': '09:00',
        'end': '23:30',
    }]
    store_israel = await dataset.store(
        cluster='Тель-Авив',
        timetable=tt_israel,
        company=company,
    )

    with tap:
        with tap.subtest(None, 'Проверка, что расписание лавок устанавливается '
                               'верно при нескольких запусках'):
            for _ in range(2):
                await switch_to_holiday(company_id=company.company_id)

                await store1.reload()
                await store2.reload()
                await store_israel.reload()

                tap.eq_ok(
                    json(
                        store1.timetable.pure_python(strip_seconds=True),
                        sort_keys=True
                    ),
                    json(
                        HOLIDAY_TIMETABLE_1.pure_python(strip_seconds=True),
                        sort_keys=True
                    ),
                    'Holiday timetable is set'
                )
                tap.eq_ok(
                    json(
                        store2.timetable.pure_python(strip_seconds=True),
                        sort_keys=True
                    ),
                    json(
                        HOLIDAY_TIMETABLE_1.pure_python(
                            strip_seconds=True
                        ),
                        sort_keys=True
                    ),
                    'Holiday timetable is set'
                )
                tap.eq_ok(
                    json(
                        store_israel.timetable,
                        sort_keys=True
                    ),
                    json(dataset.TimeTable(tt_israel), sort_keys=True),
                    'Israel timetable did not change'
                )
        with tap.subtest(None,
                         'Проверка, что расписание лавок востанавливается '
                         'верно при нескольких запусках'
                         ):
            for _ in range(2):
                await restore_timetables(company_id=company.company_id)

                await store1.reload()
                await store2.reload()
                await store_israel.reload()

                tap.eq_ok(
                    json(
                        store1.timetable,
                        sort_keys=True
                    ),
                    json(dataset.TimeTable(tt1), sort_keys=True),
                    'Old timetable is restored'
                )
                tap.eq_ok(
                    json(
                        store2.timetable,
                        sort_keys=True
                    ),
                    json(dataset.TimeTable(tt2), sort_keys=True),
                    'Old timetable is restored'
                )
                tap.eq_ok(
                    json(
                        store_israel.timetable,
                        sort_keys=True
                    ),
                    json(dataset.TimeTable(tt_israel), sort_keys=True),
                    'Israel timetable did not change'
                )


ZONE = [[{'lon': 66.0, 'lat': 33.0},
         {'lon': 66.0, 'lat': 33.5},
         {'lon': 66.5, 'lat': 33.0},
         {'lon': 66.0, 'lat': 33.0}],
        [{'lon': 66.3, 'lat': 33.6},
         {'lon': 66.4, 'lat': 33.6},
         {'lon': 66.3, 'lat': 33.7},
         {'lon': 66.3, 'lat': 33.6}]]


@pytest.mark.parametrize(
    'tt, new_tt',
    [
        # совпаление
        ([{
            'type': 'everyday',
            'begin': '11:00',
            'end': '22:15',
        }],
         [{
             'type': 'everyday',
             'begin': '11:00',
             'end': '22:15',
         }]),
        # полностью изменяется
        ([{
            'type': 'everyday',
            'begin': '07:00',
            'end': '23:13',
        }],
         [{
             'type': 'everyday',
             'begin': '11:00',
             'end': '22:15',
         }]),
        # полностью изменяется
        ([{
            'type': 'everyday',
            'begin': '00:00',
            'end': '00:00',
        }],
         [{
             'type': 'everyday',
             'begin': '11:00',
             'end': '22:15',
         }]),
        # полностью изменяется
        ([{
            'type': 'everyday',
            'begin': '07:00',
            'end': '01:00',
        }],
         [{
             'type': 'everyday',
             'begin': '11:00',
             'end': '22:15',
         }]),
        # end изменяется
        ([{
            'type': 'friday',
            'begin': '13:00',
            'end': '23:30',
        }],
         [{
             'type': 'friday',
             'begin': '13:00',
             'end': '22:15',
         }]),
        # begin изменяется
        ([{
            'type': 'friday',
            'begin': '07:00',
            'end': '19:00',
        }],
         [{
             'type': 'friday',
             'begin': '11:00',
             'end': '19:00',
         }]),
        # begin изменяется, begin > end
        ([{
            'type': 'everyday',
            'begin': '23:13',
            'end': '14:00',
        }],
         [{
             'type': 'everyday',
             'begin': '11:00',
             'end': '14:00',
         }]),
        # end изменяется, begin > end
        ([{
            'type': 'everyday',
            'begin': '16:00',
            'end': '06:00',
        }],
         [{
             'type': 'everyday',
             'begin': '16:00',
             'end': '22:15',
         }]),
        # 2 отрезка в оригинальной таблице, 1 в финальной
        ([
             {
                 'type': 'friday',
                 'begin': '07:00',
                 'end': '19:00',
             },
             {
                 'type': 'monday',
                 'begin': '00:00',
                 'end': '07:00',
             }
         ],
         [{
             'type': 'friday',
             'begin': '11:00',
             'end': '19:00',
         }]),
        # 2 отрезка в оригинальной таблице, 2 в финальной
        ([
             {
                 'type': 'friday',
                 'begin': '07:00',
                 'end': '19:00',
             },
             {
                 'type': 'monday',
                 'begin': '13:00',
                 'end': '23:30',
             }
         ],
         [
             {
                 'type': 'friday',
                 'begin': '11:00',
                 'end': '19:00',
             },
             {
                 'type': 'monday',
                 'begin': '13:00',
                 'end': '22:15',
             }
         ]),
    ])
async def test_set_restore_zones_simple(tap, dataset, tt, new_tt):
    company = await dataset.company()
    store = await dataset.store(
        cluster='Москва',
        company=company,
    )
    zone = await dataset.zone(
        store=store,
        effective_from='2021-01-01',
        delivery_type='foot',
        zone=ZONE,
        timetable=tt,
        status='active'
    )

    with tap:
        await switch_to_holiday(company_id=company.company_id)

        await zone.reload()

        tap.eq_ok(
            json(
                zone.timetable,
                sort_keys=True
            ),
            json(dataset.TimeTable(new_tt), sort_keys=True),
            'Holiday timetable is set in zone'
        )
        tap.eq_ok(zone.status, 'active', 'Status is not changed')

        await restore_timetables(company_id=company.company_id)

        await zone.reload()

        tap.eq_ok(
            json(
                zone.timetable,
                sort_keys=True
            ),
            json(dataset.TimeTable(tt), sort_keys=True),
            'Old timetable is restored'
        )
        tap.eq_ok(zone.status, 'active', 'Status is not changed')


async def test_set_restore_zones_split(tap, dataset):
    company = await dataset.company()
    store = await dataset.store(
        cluster='Москва',
        company=company,
    )
    tt = [{
        'type': 'everyday',
        'begin': '19:00',
        'end': '12:00',
    }]
    zone = await dataset.zone(
        store=store,
        effective_from='2021-01-01',
        delivery_type='foot',
        zone=ZONE,
        timetable=tt,
        status='active'
    )

    with tap:
        with tap.subtest(None, 'Проверка, что расписание зон устанавливается '
                               'верно при нескольких запусках'):
            for _ in range(2):
                await switch_to_holiday(company_id=company.company_id)

                await zone.reload()

                exp_tt = [
                    {
                        'type': 'everyday',
                        'begin': '11:00',
                        'end': '12:00',
                    },
                    {
                        'type': 'everyday',
                        'begin': '19:00',
                        'end': '22:15',
                    }
                ]

                tap.eq_ok(
                    json(
                        zone.timetable,
                        sort_keys=True
                    ),
                    json(dataset.TimeTable(exp_tt), sort_keys=True),
                    'Holiday timetable is set in zone'
                )
                tap.eq_ok(zone.status, 'active', 'Status is not changed')

        with tap.subtest(None, 'Проверка, что расписание зон востанавливается '
                               'верно при нескольких запусках'):
            for _ in range(2):
                await restore_timetables(company_id=company.company_id)

                await zone.reload()

                tap.eq_ok(
                    json(
                        zone.timetable,
                        sort_keys=True
                    ),
                    json(dataset.TimeTable(tt), sort_keys=True),
                    'Old timetable is restored'
                )
                tap.eq_ok(zone.status, 'active', 'Status is not changed')


@pytest.mark.parametrize(
    'tt',
    [
        [{
            'type': 'monday',
            'begin': '00:00',
            'end': '07:00',
        }],
        [{
            'type': 'monday',
            'begin': '23:00',
            'end': '06:00',
        }],
        [{
            'type': 'monday',
            'begin': '23:00',
            'end': '00:00',
        }],
        [
            {
                'type': 'monday',
                'begin': '23:00',
                'end': '00:00',
            },
            {
                'type': 'monday',
                'begin': '23:00',
                'end': '06:00',
            }
        ],
    ]
)
async def test_set_restore_zones_disable(tap, dataset, tt):
    company = await dataset.company()
    store = await dataset.store(
        cluster='Москва',
        company=company,
    )
    zone = await dataset.zone(
        store=store,
        effective_from='2021-01-01',
        delivery_type='foot',
        zone=ZONE,
        timetable=tt,
        status='active'
    )

    with tap:
        with tap.subtest(None, 'Проверка, что статус зон устанавливается '
                               'верно при нескольких запусках'):
            for _ in range(2):
                await switch_to_holiday(company_id=company.company_id)

                await zone.reload()

                tap.eq_ok(
                    json(
                        zone.timetable,
                        sort_keys=True
                    ),
                    json(dataset.TimeTable(tt), sort_keys=True),
                    'Active night zone timetable in night zone is not changed'
                )
                tap.eq_ok(zone.status, 'disabled', 'Night zone disabled')

        with tap.subtest(None, 'Проверка, что статус зон востанавливается '
                               'верно при нескольких запусках'):
            for _ in range(2):
                await restore_timetables(company_id=company.company_id)

                await zone.reload()

                tap.eq_ok(
                    json(
                        zone.timetable,
                        sort_keys=True
                    ),
                    json(dataset.TimeTable(tt), sort_keys=True),
                    'Active night zone timetable is not changed'
                )
                tap.eq_ok(zone.status, 'active',
                          'Active night zone status is restored')


async def test_set_restore_no_changes(tap, dataset):
    company = await dataset.company()
    tt = [{
        'type': 'monday',
        'begin': '00:00',
        'end': '07:00',
    }]
    store = await dataset.store(
        cluster='Москва',
        company=company,
    )
    zone = await dataset.zone(
        store=store,
        effective_from='2021-01-01',
        delivery_type='foot',
        zone=ZONE,
        timetable=tt,
        status='template'
    )

    store_israel = await dataset.store(
        cluster='Тель-Авив',
        company=company,
    )
    zone_israel = await dataset.zone(
        store=store_israel,
        effective_from='2021-01-01',
        delivery_type='foot',
        zone=ZONE,
        timetable=tt,
        status='active'
    )

    with tap:
        await switch_to_holiday(company_id=company.company_id)

        await zone.reload()
        await zone_israel.reload()

        tap.eq_ok(
            json(
                zone.timetable,
                sort_keys=True
            ),
            json(dataset.TimeTable(tt), sort_keys=True),
            'Template night zone timetable is not changed'
        )
        tap.eq_ok(zone.status, 'template',
                  'Template night zone status is not changed')

        tap.eq_ok(
            json(
                zone_israel.timetable,
                sort_keys=True
            ),
            json(dataset.TimeTable(tt), sort_keys=True),
            'Israel night zone timetable is not changed'
        )
        tap.eq_ok(zone_israel.status, 'active',
                  'Israel night zone is not changed')

        await restore_timetables(company_id=company.company_id)

        await zone.reload()
        await zone_israel.reload()

        tap.eq_ok(
            json(
                zone.timetable,
                sort_keys=True
            ),
            json(dataset.TimeTable(tt), sort_keys=True),
            'Template night zone timetable is not changed'
        )
        tap.eq_ok(zone.status, 'template',
                  'Template night zone status is not changed')

        tap.eq_ok(
            json(
                zone_israel.timetable,
                sort_keys=True
            ),
            json(dataset.TimeTable(tt), sort_keys=True),
            'Israel night zone timetable is not changed'
        )
        tap.eq_ok(zone_israel.status, 'active',
                  'Israel night zone status is not changed')
