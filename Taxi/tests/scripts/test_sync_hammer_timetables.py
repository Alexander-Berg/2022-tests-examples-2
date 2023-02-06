import pytest
from stall.scripts.sync_hammer_timetables import sync_hammer_timetables


async def test_sync(tap, dataset, cfg, uuid):
    with tap.plan(15, 'Синк расписаний'):
        prefix = uuid()
        store_1 = await dataset.store(external_id=prefix + '123')
        store_2 = await dataset.store(
            company_id=store_1.company_id,
            external_id=prefix + 'Букашка',
            options_setup={
                'exp_mc_hammer_timetable': [{
                    'type': 'everyday',
                    'begin': '00:00',
                    'end': '03:00',
                }]
            }
        )
        store_3 = await dataset.store(
            company_id=store_1.company_id,
            options_setup={
                'exp_mc_hammer_timetable': [{
                    'type': 'everyday',
                    'begin': '00:00',
                    'end': '03:00',
                }]
            }
        )

        cfg.set('mode', 'testing')
        cfg.set(
            'business.store.exp_mc_hammer_timetable_source.yt.testing',
            '//cool/table'
        )

        class FakeYtClient:
            result = []

            def read_table(self, table):
                tap.eq(table, '//cool/table', 'Запрос к нужной таблице')
                return self.result

        client = FakeYtClient()
        client.result = [
            {
                'place_id': prefix + '123',
                'start_time': '04:00',
                'end_time': '23:00',
            },
            {
                'place_id': prefix + '123',
                'start_time': '00:01',
                'end_time': '00:02',
            },
            {
                'place_id': prefix + 'Букашка',
                'start_time': '23:00',
                'end_time': '01:00',
            },
            {
                'place_id': prefix + 'Unknown store',
                'start_time': '00:11',
                'end_time': '22:09',
            }
        ]

        tap.note('Тест без применения')
        await sync_hammer_timetables(client, apply=False)

        store_1 = await store_1.reload()
        tap.eq(
            store_1.options_setup.exp_mc_hammer_timetable,
            [],
            'Расписание дефолтное'
        )
        tap.ok(await store_3.reload(), 'Перезабрали склад 4')
        tap.eq(
            store_3.options_setup.exp_mc_hammer_timetable,
            [
                {'type': 'everyday', 'begin': '00:00', 'end': '03:00'},
            ],
            'Расписание не сбросилось'
        )

        tap.note('Тест на один склад')
        await sync_hammer_timetables(
            client, apply=True, store_id=store_1.store_id)

        tap.ok(await store_1.reload(), 'Перезабрали склад 1')
        tap.eq(
            store_1.options_setup.exp_mc_hammer_timetable,
            [
                {'type': 'everyday', 'begin': '00:01', 'end': '00:02'},
                {'type': 'everyday', 'begin': '04:00', 'end': '23:00'},
            ],
            'Расписание изменилось'
        )
        tap.ok(await store_2.reload(), 'Перезабрали склад 2')
        tap.eq(
            store_2.options_setup.exp_mc_hammer_timetable,
            [
                {'type': 'everyday', 'begin': '00:00', 'end': '03:00'},
            ],
            'Расписание не изменилось у второго'
        )

        tap.note('Тест на компанию')
        await sync_hammer_timetables(
            client, apply=True, company_id=store_1.company_id)

        for store in (store_1, store_2, store_3):
            await store.reload()

        tap.eq(
            store_1.options_setup.exp_mc_hammer_timetable,
            [
                {'type': 'everyday', 'begin': '00:01', 'end': '00:02'},
                {'type': 'everyday', 'begin': '04:00', 'end': '23:00'}
            ],
            'Расписание осталось измененное'
        )

        tap.eq(
            store_2.options_setup.exp_mc_hammer_timetable,
            [
                {'type': 'everyday', 'begin': '23:00', 'end': '01:00'},
            ],
            'Расписание у второго изменилось'
        )
        tap.eq(
            store_3.options_setup.exp_mc_hammer_timetable,
            [],
            'Расписание у третьего изменилось'
        )

        tap.note('Повторный прогон')
        old_lsns = (store_1.lsn, store_2.lsn, store_3.lsn)
        await sync_hammer_timetables(
            client, apply=True, company_id=store_1.company_id)

        for store in (store_1, store_2, store_3):
            await store.reload()

        tap.eq(
            (store_1.lsn, store_2.lsn, store_3.lsn),
            old_lsns,
            'Остались старые lsn, не было изменений'
        )


@pytest.mark.parametrize('wrong_data, delete_place', [
    ({}, True),
    ({}, False),
    ({'start_time': 'success'}, False),
    ({'start_time': '00:00', 'end_time': '00:01'}, True),
    ({'start_time': '1234:54:78', 'end_time': '00:01'}, False),
    ({'start_time': '00:00', 'end_time': ''}, False),
])
async def test_sync_wrong_input(
        tap, dataset, cfg, uuid,
        wrong_data, delete_place
):
    with tap.plan(2, 'Одна из строк в yt кривая'):
        prefix = uuid()
        store_1 = await dataset.store(external_id=prefix + '123')
        store_2 = await dataset.store(
            company_id=store_1.company_id,
            external_id=prefix + '321',
        )
        cfg.set('mode', 'testing')

        class FakeYtClient:
            result = []

            def read_table(self, table):  # pylint: disable=unused-argument
                return self.result

        client = FakeYtClient()

        wrong_row = {
            'place_id': prefix + '123',
            **wrong_data,
        }
        if delete_place:
            wrong_row.pop('place_id')
        client.result = [
            wrong_row,
            {
                'place_id': prefix + '321',
                'start_time': '00:01',
                'end_time': '00:02',
            },
        ]

        await sync_hammer_timetables(
            client, apply=True, company_id=store_1.company_id)

        for store in (store_1, store_2):
            await store.reload()

        tap.eq(
            store_1.options_setup.exp_mc_hammer_timetable,
            [],
            'Расписание дефолтное'
        )
        tap.eq(
            store_2.options_setup.exp_mc_hammer_timetable,
            [
                {'type': 'everyday', 'begin': '00:01', 'end': '00:02'},
            ],
            'Расписание обновилось'
        )
