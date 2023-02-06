from datetime import time

from libstall.model.coerces import time as coerce_time
from stall.model.check_project import CheckProject


async def test_check_project(tap, uuid, now):
    with tap.plan(6, 'тестируем модель'):
        _now = now()
        cp1 = CheckProject(
            title=uuid(),
            schedule={'begin': _now, 'end': _now},
        )
        cp2 = CheckProject({
            'title': uuid(),
            'schedule': {'begin': _now, 'end': _now},
        })

        tap.ok(await cp1.save(), 'первое cp')
        tap.ok(cp1.check_project_id, 'есть id')
        tap.ok(cp1.external_id, 'есть external')
        tap.ok(await cp2.save(), 'второе cp')
        tap.ok(cp2.check_project_id, 'есть id')
        tap.ok(cp2.external_id, 'есть external')


async def test_dataset(tap, dataset, uuid, now):
    with tap.plan(24, 'тестим датасет'):
        empty_cp = await dataset.check_project()
        tap.ok(empty_cp, 'сохранился в базу')
        tap.ok(
            empty_cp.title.startswith('Тестовый проект расписания локалок'),
            'норм тайтл',
        )
        tap.eq(empty_cp.status, 'active', 'статус активный')
        tap.eq(
            empty_cp.stores.pure_python(),
            {'store_id': [], 'company_id': [], 'cluster_id': []},
            'пустые лавки',
        )
        tap.eq(
            empty_cp.products.pure_python(),
            {'product_id': [], 'product_group_id': []},
            'пустые продукты',
        )
        tap.ok(
            isinstance(empty_cp.schedule.timetable, dataset.TimeTable),
            'timetable - TimeTable'
        )
        tap.eq(
            empty_cp.schedule.timetable.value[0]['type'], 'everyday', 'тип tt'
        )
        tap.eq(
            coerce_time(empty_cp.schedule.timetable.value[0]['begin']),
            time(4, 20),
            'начало tt',
        )
        tap.eq(
            coerce_time(empty_cp.schedule.timetable.value[0]['end']),
            time(4, 20),
            'конец tt',
        )
        tap.ok(empty_cp.schedule.begin, 'есть begin')
        tap.ok(empty_cp.schedule.end, 'есть end')
        tap.eq(empty_cp.vars, {}, 'пустые vars')
        tap.eq(empty_cp.shelf_types, [], 'пустые shelf_types')

        zhopka_external_id = uuid()
        empty_cp_wtitle = await dataset.check_project(
            external_id=zhopka_external_id,
            stores={'foo': 'bar'},
            title='zhopka',
        )
        tap.eq(
            empty_cp_wtitle.external_id, zhopka_external_id, 'нужный external'
        )
        tap.eq(empty_cp_wtitle.title, 'zhopka', 'нужный тайтл')
        tap.eq(
            empty_cp_wtitle.stores.pure_python(),
            {'store_id': [], 'company_id': [], 'cluster_id': []},
            'stores',
        )

        store = await dataset.store()
        companies = [await dataset.company() for _ in range(2)]
        cluster = await dataset.cluster()

        product = await dataset.product()
        product_group = await dataset.product_group()

        _now = now()
        special_cp = await dataset.check_project(
            status='disabled',
            company_id=companies[0].company_id,
            company=companies[1],
            cluster_id=cluster.cluster_id,
            store=store,
            product_id=product.product_id,
            product_group_id='fake_id',
            product_group=product_group,
            schedule={'foo': 'bar', 'begin': _now, 'end': _now},
            shelf_types=['store'],
            vars={'foo': 'bar'},
        )

        tap.eq(special_cp.status, 'disabled', 'status')
        tap.eq(
            special_cp.stores,
            {
                'company_id': [companies[1].company_id],
                'store_id': [store.store_id],
                'cluster_id': [cluster.cluster_id],
            },
            'stores ok',
        )
        tap.eq(
            special_cp.products,
            {
                'product_id': [product.product_id],
                'product_group_id': [product_group.group_id],
            },
            'products ok',
        )
        tap.eq(
            special_cp.schedule.timetable.pure_python(),
            [],
            'schedule.timetable ok',
        )
        tap.eq(
            special_cp.schedule.begin.date(),
            _now.date(),
            'schedule.begin.date() ok',
        )
        tap.eq(
            special_cp.schedule.end.date(),
            _now.date(),
            'schedule.end.date() ok',
        )
        tap.eq(special_cp.vars, {'foo': 'bar'}, 'vars ok')
        tap.eq(special_cp.shelf_types, ['store'], 'shelf_types ok')
