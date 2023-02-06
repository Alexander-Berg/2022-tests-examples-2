from collections import defaultdict

import pytest

from stall.model.shelf import Shelf
from stall.scripts.modify_racks import (
    modify_racks, WAREHOUSE_GROUP, DEPTH, WIDTH,
    HEIGHT, INDEX, SHELF_QTY, TAGS, TYPE
)


RACK_PARAMS = {
    WAREHOUSE_GROUP: 'Бананы',
    DEPTH: '400',
    WIDTH: '1000',
    HEIGHT: '300',
    INDEX: 2
}


async def test_uncritical_duplication(tap, dataset):
    with tap.plan(7, 'Некорректный параметр, дублирующиеся названия'):
        store = await dataset.store()
        await dataset.shelf(store=store, title='AA-1', rack='AA')
        for i in range(1, 3):
            await dataset.shelf(
                store=store, title=f'AA-{i}', rack='AA', status='disabled'
            )
        await dataset.shelf(
            store=store, title='AA-2', rack='AA', status='removed'
        )

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={
                WAREHOUSE_GROUP: 'abc',
                DEPTH:           '400',
                WIDTH:           '1000',
                HEIGHT:          '300',
                TYPE:            'incoming',
                TAGS:            '',
                SHELF_QTY:       '2',
                INDEX:           2
            },
            apply=True
        )
        tap.eq(
            [err['error'] for err in errors],
            ['Некорректное значение abc параметра warehouse_group'],
            '1 ошибка о некорректном параметре'
        )

        shelves = defaultdict(list)
        for shelf in await Shelf.list(
                by='full',
                db={'mode': 'slave'},
                conditions=[
                    ('store_id', store.store_id),
                    ('rack', 'AA'),
                ],
        ):
            shelves[shelf.status == 'active'].append(shelf)

        tap.eq(len(shelves[True]), 2, '1 полка активировалась')
        tap.eq(len(shelves[False]), 2, '2 остались не активны')

        tap.eq(
            {shelf.title for shelf in shelves[True]},
            {'AA-1', 'AA-2'},
            'названия активных полок корректные'
        )
        tap.eq(
            {shelf.title for shelf in shelves[False]},
            {'AA-1', 'AA-2'},
            'названия не активных полок корректные'
        )

        with tap.subtest(
                8,
                'Все параметры кроме некорректного установлены для активных'
        ) as taps:
            for shelf in shelves[True]:
                taps.eq(shelf.warehouse_group, None, 'warehouse_group')
                taps.eq(shelf.width, 1000, 'width')
                taps.eq(shelf.height, 300, 'height')
                taps.eq(shelf.depth, 400, 'depth')

        with tap.subtest(8, 'Параметры не активных не установлены') as taps:
            for shelf in shelves[False]:
                taps.eq(shelf.warehouse_group, None, 'warehouse_group')
                taps.eq(shelf.width, None, 'width')
                taps.eq(shelf.height, None, 'height')
                taps.eq(shelf.depth, None, 'depth')


async def test_critical_duplication(tap, dataset):
    with tap.plan(3, 'Дублирующиеся названия в активных полках'):
        store = await dataset.store()
        await dataset.shelf(store=store, title='AA-1', rack='AA')
        await dataset.shelf(store=store, title='AA-1', rack='AA')

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={
                **RACK_PARAMS,
                SHELF_QTY: '1',
                INDEX: 2
            },
            apply=True
        )
        tap.in_ok(
            'Пересчет полок на стеллаже не будет совершен',
            [err['error'] for err in errors],
            'ожидаемые ошибки'
        )

        shelves = (await Shelf.list(
            by='full',
            db={'mode': 'slave'},
            conditions=[
                ('store_id', store.store_id),
                ('rack', 'AA'),
                ('status', 'active'),
            ]
        )).list

        tap.eq(len(shelves), 2, 'полки все еще активны')

        with tap.subtest(8, 'Все параметры установлены') as taps:
            for shelf in shelves:
                taps.eq(shelf.warehouse_group, 'banany', 'warehouse_group')
                taps.eq(shelf.width, 1000, 'width')
                taps.eq(shelf.height, 300, 'height')
                taps.eq(shelf.depth, 400, 'depth')


async def test_activation_wrong_titles(tap, dataset):
    with tap.plan(6, 'Нет подходящих имен полок для активации'):
        store = await dataset.store()
        active_shelf = await dataset.shelf(store=store, title='AA-1', rack='AA')
        disabled_shelf = await dataset.shelf(
            store=store, title='AA2', rack='AA', status='disabled'
        )
        removed_shelf = await dataset.shelf(
            store=store, title='AA3', rack='AA', status='removed'
        )

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={
                **RACK_PARAMS,
                SHELF_QTY: '2'
            },
            apply=True)
        tap.ok(
            'Пересчет полок на стеллаже не будет совершен' in [
                err['error'] for err in errors
            ],
            'ожидаемые ошибки'
        )

        with await active_shelf.reload() as shelf:
            tap.eq(shelf.status, 'active', 'статус активной полки не изменился')
            tap.eq(shelf.title, 'AA-1', 'название активной полки не изменилось')

        with tap.subtest(5, 'Параметры активной полки') as taps:
            await active_shelf.reload()
            taps.eq(active_shelf.status, 'active', 'статус старый')
            taps.eq(active_shelf.warehouse_group, 'banany', 'warehouse_group')
            taps.eq(active_shelf.width, 1000, 'width')
            taps.eq(active_shelf.height, 300, 'height')
            taps.eq(active_shelf.depth, 400, 'depth')

        with tap.subtest(8, 'Параметры остальных полок не задеты') as taps:
            for shelf in [disabled_shelf, removed_shelf]:
                await shelf.reload()
                taps.eq(shelf.warehouse_group, None, 'warehouse_group')
                taps.eq(shelf.width, None, 'width')
                taps.eq(shelf.height, None, 'height')
                taps.eq(shelf.depth, None, 'depth')

        all_shelves = (await Shelf.list(
            by='full',
            db={'mode': 'slave'},
            conditions=[
                ('store_id', store.store_id),
                ('rack', 'AA'),
            ]
        )).list

        tap.eq(len(all_shelves), 3, 'новых полок нет')


async def test_ignore_err_in_activation(tap, dataset):
    with tap.plan(9, 'Стеллаж можно собрать без некорректных полок'):
        store = await dataset.store()
        active_shelves = [
            await dataset.shelf(
                store=store,
                title=f'AA-{i}',
                rack='AA'
            ) for i in range(1, 3)
        ]
        incorrect_shelves = [
            await dataset.shelf(
                store=store,
                title=f'AA{i}',
                rack='AA',
                status='disabled'
            ) for i in range(3, 5)
        ]
        removed_shelves = [
            await dataset.shelf(
                store=store,
                title=f'AA-{i}',
                rack='AA',
                status='removed'
            ) for i in range(3, 6)
        ]

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={
                **RACK_PARAMS,
                SHELF_QTY: '4',
            },
            apply=True
        )
        tap.eq([err['error'] for err in errors], [], 'нет ошибок')

        for active_shelf in active_shelves:
            with await active_shelf.reload() as shelf:
                tap.eq(shelf.status, 'active', 'статус активной полки старый')

        shelves = defaultdict(list)
        for shelf in removed_shelves:
            await shelf.reload()
            shelves[shelf.status].append(shelf)
        tap.eq(len(shelves['active']), 2, '2 полки активированы')
        tap.eq(len(shelves['removed']), 1, 'остальные все еще удалены')

        tap.eq(
            {shelf.title for shelf in shelves['active']},
            {'AA-3', 'AA-4'},
            'названия активированных полок корректные'
        )

        for shelf in incorrect_shelves:
            await shelf.reload()
        tap.not_in_ok(
            'active',
            {shelf.status for shelf in incorrect_shelves},
            'полки с неподходящими названиями не активировались'
        )

        with tap.subtest(16, 'Все параметры установлены правильно') as taps:
            for shelf in [*active_shelves, *shelves['active']]:
                taps.eq(shelf.warehouse_group, 'banany', 'warehouse_group')
                taps.eq(shelf.width, 1000, 'width')
                taps.eq(shelf.height, 300, 'height')
                taps.eq(shelf.depth, 400, 'depth')

        all_shelves = (await Shelf.list(
            by='full',
            db={'mode': 'slave'},
            conditions=[
                ('store_id', store.store_id),
                ('rack', 'AA'),
            ]
        )).list

        tap.eq(len(all_shelves), 7, 'новых полок нет')


async def test_remove_rack(tap, dataset):
    with tap.plan(2, 'Можно удалить стеллаж с некорректными полками'):
        store = await dataset.store()
        for i in range(1, 3):
            await dataset.shelf(
                store=store,
                title=f'AA{i}',
                rack='AA'
            )

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={
                **RACK_PARAMS,
                SHELF_QTY: '0',
            },
            apply=True
        )
        tap.eq([err['error'] for err in errors], [], 'нет ошибок')

        shelves = (await Shelf.list(
            by='full',
            db={'mode': 'slave'},
            conditions=[
                ('store_id', store.store_id),
                ('rack', 'AA'),
                ('status', 'active')
            ]
        )).list

        tap.eq(len(shelves), 0, 'активных полок нет')


async def test_deactivate_incorrect(tap, dataset):
    with tap.plan(2, 'Ошибка деактивации полок с некорректными названиями'):
        store = await dataset.store()
        shelf1 = await dataset.shelf(store=store, title='AA-1', rack='AA')
        shelf2 = await dataset.shelf(store=store, title='AA2', rack='AA')

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={
                **RACK_PARAMS,
                SHELF_QTY: '1',
            },
            apply=True
        )
        tap.eq(
            [err['error'] for err in errors],
            ['Полки не подходят под шаблон <стелаж>-<номер>: AA2',
             'Нарушена последовательность в названиях полок',
             'Пересчет полок на стеллаже не будет совершен'
             ],
            'ожидаемые ошибки'
        )

        with tap.subtest(10, 'Все параметры установлены правильно') as taps:
            for shelf in [shelf1, shelf2]:
                await shelf.reload()
                taps.eq(shelf.status, 'active', 'статус старый')
                taps.eq(shelf.warehouse_group, 'banany', 'warehouse_group')
                taps.eq(shelf.width, 1000, 'width')
                taps.eq(shelf.height, 300, 'height')
                taps.eq(shelf.depth, 400, 'depth')


@pytest.mark.parametrize(
    'warehouse_group, exp_warehouse_group, exp_errors',
    [
        ('Бананы', 'banany', []),
        ('abc', None,
         ['Некорректное значение abc параметра warehouse_group']
         )
    ]
)
async def test_create_new_shelves(
        tap, dataset, warehouse_group, exp_warehouse_group, exp_errors
):
    with tap.plan(5, 'Активация недостающих полок, создание новых'):
        store = await dataset.store()
        await dataset.shelf(store=store, title='AA-1', rack='AA', order=11)
        await dataset.shelf(
            store=store,
            title='AA-3',
            rack='AA',
            status='disabled'
        )
        await dataset.shelf(
            store=store,
            title='AA-2',
            rack='AA',
            status='removed'
        )

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={
                WAREHOUSE_GROUP: warehouse_group,
                DEPTH: '400',
                WIDTH: '1000',
                HEIGHT: '300',
                INDEX: 2,
                SHELF_QTY: '5',
            },
            apply=True
        )
        tap.eq(
            [err['error'] for err in errors],
            exp_errors,
            'ожидаемые ошибки'
        )

        all_shelves = (await Shelf.list(
            by='full',
            db={'mode': 'slave'},
            conditions=[
                ('store_id', store.store_id),
                ('rack', 'AA'),
            ]
        )).list
        tap.eq(
            [sh.status for sh in all_shelves],
            ['active'] * 5,
            '5 активных полок'
        )

        tap.eq(
            {shelf.title for shelf in all_shelves},
            {f'AA-{i}' for i in range(1, 6)},
            'названия полок корректные'
        )

        with tap.subtest(20, 'Все параметры установлены правильно') as taps:
            for shelf in all_shelves:
                taps.eq(
                    shelf.warehouse_group,
                    exp_warehouse_group,
                    'warehouse_group'
                )
                taps.eq(shelf.width, 1000, 'width')
                taps.eq(shelf.height, 300, 'height')
                taps.eq(shelf.depth, 400, 'depth')

        with tap.subtest(
                2, 'order для новых полкок взят у существующей активной'
        ) as taps:
            with [sh for sh in all_shelves if sh.title == 'AA-4'][0] as shelf:
                taps.eq(shelf.order, 11, 'order корректный')
            with [sh for sh in all_shelves if sh.title == 'AA-5'][0] as shelf:
                taps.eq(shelf.order, 11, 'order корректный')


async def test_create_new_rack(tap, dataset):
    with tap.plan(4, 'Создание нового стеллажа'):
        store = await dataset.store()

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={
                **RACK_PARAMS,
                SHELF_QTY: '5',
            },
            apply=True
        )
        tap.eq(
            [err['error'] for err in errors],
            [],
            'ожидаемые ошибки'
        )

        all_shelves = (await Shelf.list(
            by='full',
            db={'mode': 'slave'},
            conditions=[
                ('store_id', store.store_id),
                ('rack', 'AA'),
            ]
        )).list

        tap.eq(
            [sh.status for sh in all_shelves],
            ['active'] * 5,
            '5 активных полок создано'
        )
        tap.eq(
            {shelf.title for shelf in all_shelves},
            {f'AA-{i}' for i in range(1, 6)},
            'названия полок корректные'
        )

        with tap.subtest(25, 'Все параметры установлены правильно') as taps:
            for shelf in all_shelves:
                taps.eq(shelf.order, 0, 'warehouse_group')
                taps.eq(shelf.warehouse_group, 'banany', 'warehouse_group')
                taps.eq(shelf.width, 1000, 'width')
                taps.eq(shelf.height, 300, 'height')
                taps.eq(shelf.depth, 400, 'depth')


async def test_create_new_without_apply(tap, dataset):
    with tap.plan(
            3, 'Активация недостающих полок, создание новых, apply=False'
    ):
        store = await dataset.store()
        shelf1 = await dataset.shelf(store=store, title='AA-1', rack='AA')
        shelf2 = await dataset.shelf(
            store=store,
            title='AA-3',
            rack='AA',
            status='disabled'
        )
        shelf3 = await dataset.shelf(
            store=store,
            title='AA-2',
            rack='AA',
            status='removed'
        )

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={
                **RACK_PARAMS,
                SHELF_QTY: '5',
            },
            apply=False
        )
        tap.eq(
            [err['error'] for err in errors],
            [],
            'ожидаемые ошибки'
        )

        with tap.subtest(15, 'параметры не изменились') as taps:
            for shelf in [shelf1, shelf2, shelf3]:
                old_status = shelf.status
                await shelf.reload()
                taps.eq(shelf.status, old_status, 'status')
                taps.eq(shelf.warehouse_group, None, 'warehouse_group')
                taps.eq(shelf.width, None, 'width')
                taps.eq(shelf.height, None, 'height')
                taps.eq(shelf.depth, None, 'depth')

        all_shelves = (await Shelf.list(
            by='full',
            db={'mode': 'slave'},
            conditions=[
                ('store_id', store.store_id),
                ('rack', 'AA'),
            ]
        )).list
        tap.eq(len(all_shelves), 3, 'новых полок нет')


async def test_remove_without_stock(tap, dataset):
    with tap.plan(3, 'Удаление лишних полок, есть стоки на остающихся'):
        store = await dataset.store()
        shelves = [
            await dataset.shelf(
                store=store,
                title=f'AA-{i}',
                rack='AA'
            ) for i in range(1, 5)
        ]
        await dataset.shelf(
            store=store,
            title='AA4',
            rack='AA',
            status='disabled'
        )
        await dataset.stock(count=300, reserve=100, shelf=shelves[0])
        await dataset.stock(count=300, reserve=100, shelf=shelves[1])

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={
                **RACK_PARAMS,
                SHELF_QTY: '3'
            },
            apply=True
        )
        tap.eq(errors, [], 'нет ошибок')

        with tap.subtest(
                15, '3 полки остались активны, параметры установлены'
        ) as taps:
            for shelf in shelves[:3]:
                await shelf.reload()
                taps.eq(shelf.status, 'active', 'полка активна')
                taps.eq(shelf.warehouse_group, 'banany', 'warehouse_group')
                taps.eq(shelf.width, 1000, 'width')
                taps.eq(shelf.height, 300, 'height')
                taps.eq(shelf.depth, 400, 'depth')

        with await shelves[3].reload() as shelf:
            tap.eq(shelf.status, 'disabled', 'полка отключена')


async def test_remove_with_stock(tap, dataset):
    with tap.plan(2, 'Стоки мешают удалению'):
        store = await dataset.store()
        shelves = [
            await dataset.shelf(
                store=store,
                title=f'AA-{i}',
                rack='AA'
            ) for i in range(1, 5)
        ]
        await dataset.stock(count=300, reserve=100, shelf=shelves[2])

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={
                **RACK_PARAMS,
                SHELF_QTY: '2'
            },
            apply=True
        )
        tap.eq(
            [err['error'] for err in errors],
            ['Не можем деактивировать полки из-за стоков'],
            'Ошибка из-за стоков'
        )

        with tap.subtest(
            20, 'полки остались активны, параметры установлены'
        ) as taps:
            for shelf in shelves:
                await shelf.reload()
                taps.eq(shelf.status, 'active', 'полка активна')
                taps.eq(shelf.warehouse_group, 'banany', 'warehouse_group')
                taps.eq(shelf.width, 1000, 'width')
                taps.eq(shelf.height, 300, 'height')
                taps.eq(shelf.depth, 400, 'depth')


async def test_during_stowage(tap, dataset):
    with tap.plan(2, 'Идет раскладка'):
        store = await dataset.store()
        shelves = [
            await dataset.shelf(
                store=store,
                title=f'AA-{i}',
                rack='AA'
            ) for i in range(1, 5)
        ]

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={**RACK_PARAMS,
                    SHELF_QTY: '2'},
            apply=True,
            conflict_shelves=[sh.shelf_id for sh in shelves]
        )
        tap.eq(
            [err['error'] for err in errors],
            ['Не можем деактивировать полки из-за созданных на них документов'],
            'Ошибка из-за стоков'
        )

        with tap.subtest(
            20, 'полки остались активны, параметры установлены'
        ) as taps:
            for shelf in shelves:
                await shelf.reload()
                taps.eq(shelf.status, 'active', 'полка активна')
                taps.eq(shelf.warehouse_group, 'banany', 'warehouse_group')
                taps.eq(shelf.width, 1000, 'width')
                taps.eq(shelf.height, 300, 'height')
                taps.eq(shelf.depth, 400, 'depth')


async def test_shelf_with_order(tap, dataset):
    with tap.plan(2, 'На полки создан документ'):
        store = await dataset.store()
        shelves = [
            await dataset.shelf(
                store=store,
                title=f'AA-{i}',
                rack='AA'
            ) for i in range(1, 5)
        ]

        errors = await modify_racks(
            store=store,
            rack='AA',
            params={
                **RACK_PARAMS,
                SHELF_QTY: '2',
                TYPE:      'incoming',
                TAGS:      'refrigerator',
            },
            apply=True,
            conflict_shelves=[sh.shelf_id for sh in shelves]
        )
        tap.eq(
            [err['error'] for err in errors],
            [
                'Не можем деактивировать полки'
                ' из-за созданных на них документов',
                'Нельзя менять поля type, tags полок '
                'с созданным на них документом'
            ],
            'Ошибка из-за стоков'
        )

        with tap.subtest(
            28, 'полки остались активны, параметры (кроме type) установлены'
        ) as taps:
            for shelf in shelves:
                await shelf.reload()
                taps.eq(shelf.status, 'active', 'полка активна')
                taps.eq(shelf.warehouse_group, 'banany', 'warehouse_group')
                taps.eq(shelf.width, 1000, 'width')
                taps.eq(shelf.height, 300, 'height')
                taps.eq(shelf.depth, 400, 'depth')
                taps.eq(shelf.type, 'store', 'type')
                taps.eq(shelf.tags, [], 'tags')
