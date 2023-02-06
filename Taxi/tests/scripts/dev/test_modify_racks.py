import argparse
from collections import defaultdict
import csv
import os

from scripts.dev.modify_racks import (
    FIELDS, main, SHELF_EXID, SHELF_RACK,
    STORE_EXID, INDEX, ERROR, WAREHOUSE_GROUP,
    HEIGHT, WIDTH, DEPTH, TYPE, TAGS
)
from stall.model.shelf import Shelf


OLD_PARAMS = {
    HEIGHT: 300, WIDTH: 1000, DEPTH: 400, TYPE: 'store', TAGS: ['freezer2_2']
}
NEW_PARAMS = {
    WAREHOUSE_GROUP: 'Бананы',
    HEIGHT:          400,
    WIDTH:           1000,
    DEPTH:           300,
    TYPE:            'parcel',
    TAGS:            ['refrigerator']
}


# pylint: disable=too-many-statements,too-many-locals, too-many-branches
async def test_modify(tap, dataset, uuid):
    with tap.plan(31, 'Ошибки корректно возвращаются'):
        store1 = await dataset.store()
        for shelf_index, status in enumerate(
                ['active', 'disabled', 'removed'], start=1
        ):
            await dataset.shelf(
                store=store1,
                rack='H',
                title=f'H-{shelf_index}',
                status=status,
                order=shelf_index,
                warehouse_group='chipsy',
                **OLD_PARAMS
            )

        for i in range(1, 5):
            await dataset.shelf(
                store=store1,
                rack='I',
                title=f'I-{i}',
                warehouse_group='chipsy',
                **OLD_PARAMS
            )

        store2 = await dataset.store()
        rack_2a_active = [
            await dataset.shelf(
                store=store2, rack='H', title=f'H-{i}'
            ) for i in range(1, 5)
        ]
        await dataset.stock(count=300, reserve=100, shelf=rack_2a_active[-1])
        await dataset.stock(count=300, reserve=100, shelf=rack_2a_active[-2])

        rack_2c_active = [
            await dataset.shelf(
                store=store2, rack='J', title=f'J-{i}'
            ) for i in range(1, 4)
        ]
        await dataset.stock(count=300, reserve=100, shelf=rack_2c_active[1])
        await dataset.stock(count=300, reserve=100, shelf=rack_2c_active[2])

        for i in range(1, 3):
            await dataset.shelf(
                store=store2, rack='F', title=f'F-{i}'
            )

        store3 = await dataset.store()
        h3_shelf = await dataset.shelf(store=store3, rack='H', title='H-1')
        await dataset.order(
            store=store3, type='stowage', shelves=[h3_shelf.shelf_id])

        fake_store_exid = uuid()

        with open('modify_racks.csv', 'w', newline='') as f:
            writer = csv.writer(f,
                delimiter=';',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writerows([
                FIELDS,
                # все активируется, 1 полка добавляется, параметры не меняются
                [store1.external_id, 'H', None,
                 None, None, None, None, None, 4],
                # 2 удаляются, стоков нет, параметры все неверные
                [store1.external_id, 'I', 'no',
                 'no', 'no', 'no', 'no', 'no', 2],
                # стеллажа нет, удалять нечего
                [store1.external_id, 'J', None,
                 None, None, None, None, None, 0],
                # 2 удаляются, есть стоки, параметры установиилсь
                [store2.external_id, 'H', 'Бананы',
                 1000, 400, 300, 'parcel', 'refrigerator', 2],
                # повтор стеллажа, игнорируется
                [store2.external_id, 'H', 'Чипсы',
                 '500', '900', '200', None, None, 10],
                # стеллаж создается, пробелы игнорируются,
                # 1 некорректный параметр
                [f'  {store2.external_id}  ', '  I  ', ' water ', ' 800 ',
                 ' 100 ', ' 200 ', '  collection ', '  safe ', '   3  '],
                # недостаточно полок без стоков, ничего не обновляется
                [store2.external_id, 'J', 'Бананы', 1000, 400, 300,
                 'parcel', 'refrigerator', 1],
                # нужное количество полок, параметры обновляются
                [store2.external_id, 'F', 'Бананы',
                 1000, 400, 300, 'parcel', 'refrigerator', None],
                # полки не отключаются во время раскладки
                [store3.external_id, 'H', None,
                 None, None, None, 'parcel', 'refrigerator', 0],
                # несуществующая лавка
                [fake_store_exid, 'H', 'Бананы',
                 1000, 400, 300, 'parcel', 'refrigerator', 5],
            ])

        args = argparse.Namespace(apply=True, csv='modify_racks.csv')
        await main(args)

        rack_errors = defaultdict(lambda: defaultdict(list))
        with open('errors_modify_racks.csv', newline='') as f:
            reader = csv.DictReader(
                f,
                fieldnames=[INDEX, STORE_EXID, SHELF_RACK, SHELF_EXID, ERROR],
                delimiter=';',
                quotechar='"',
                skipinitialspace=True,
            )
            for row in reader:
                rack = row.pop(SHELF_RACK)
                store_exid = row.pop(STORE_EXID)
                rack_errors[store_exid][rack].append(dict(row))

        shelves1 = defaultdict(lambda: defaultdict(list))
        for shelf in await Shelf.list(
                by='full',
                db={'mode': 'slave'},
                conditions=[('store_id', store1.store_id)],
                sort=(),
        ):
            shelves1[shelf.rack][shelf.status].append(shelf)

        tap.eq(
            [err['error'] for err in rack_errors[store1.external_id]['H']],
            [],
            'ошибки стелажа H лавки 1'
        )
        tap.eq(
            len(shelves1['H']['active']),
            4,
            'полки активировались и создались'
        )
        tap.eq(
            {shelf.title for shelf in shelves1['H']['active']},
            {f'H-{i}' for i in range(1, 5)},
            'названия корректные'
        )
        with tap.subtest(18, 'параметры не апдейтятся в None') as taps:
            for shelf in shelves1['H']['active']:
                if shelf.title != 'H-4':
                    taps.eq(
                        shelf.warehouse_group, 'chipsy', 'warehouse_group')
                    taps.eq(shelf.width, OLD_PARAMS[WIDTH], 'width')
                    taps.eq(shelf.height, OLD_PARAMS[HEIGHT], 'height')
                    taps.eq(shelf.depth, OLD_PARAMS[DEPTH], 'depth')
                    taps.eq(shelf.type, OLD_PARAMS[TYPE], 'type')
                    taps.eq(shelf.tags, OLD_PARAMS[TAGS], 'tags')

        tap.eq(
            [err['error'] for err in rack_errors[store1.external_id]['I']],
            [
                'Некорректное значение no параметра warehouse_group',
                *[
                    f'Неверный тип параметра {field}'
                    for field in [WIDTH, DEPTH, HEIGHT]
                ],
                *[
                    f'Некорректное значение no параметра {field}'
                    for field in [TAGS, TYPE]
                ]
            ],
            'ошибки стелажа I лавки 1'
        )
        tap.eq(len(shelves1['I']['disabled']), 2, '2 полки деактивировались')
        tap.eq(len(shelves1['I']['active']), 2, '2 полки осталось')
        tap.eq(
            {shelf.title for shelf in shelves1['I']['active']},
            {f'I-{i}' for i in range(1, 3)},
            'названия активных полок корректные'
        )
        with tap.subtest(24, 'параметры не апдейтятся на неправильные') as taps:
            for shelf in [*shelves1['I']['active'], *shelves1['I']['disabled']]:
                taps.eq(
                    shelf.warehouse_group, 'chipsy', 'warehouse_group')
                taps.eq(shelf.width, OLD_PARAMS[WIDTH], 'width')
                taps.eq(shelf.height, OLD_PARAMS[HEIGHT], 'height')
                taps.eq(shelf.depth, OLD_PARAMS[DEPTH], 'depth')
                taps.eq(shelf.type, OLD_PARAMS[TYPE], 'type')
                taps.eq(shelf.tags, OLD_PARAMS[TAGS], 'tags')

        tap.eq(
            [err['error'] for err in rack_errors[store1.external_id]['J']],
            [],
            'ошибки стелажа J лавки 1'
        )
        tap.eq(
            len(shelves1['J']),
            0,
            'полки не создались'
        )

        shelves2 = defaultdict(lambda: defaultdict(list))
        for shelf in await Shelf.list(
                by='full',
                db={'mode': 'slave'},
                conditions=[('store_id', store2.store_id)],
                sort=(),
        ):
            shelves2[shelf.rack][shelf.status].append(shelf)

        tap.eq(
            [err['error'] for err in rack_errors[store2.external_id]['H']],
            ['Параметры стеллажа уже заданы в строке 5',
             'Не можем деактивировать полки из-за стоков',
             'Нельзя менять поля type, tags полок со стоками'],
            'ошибки стелажа H лавки 2'
        )
        tap.eq(len(shelves2['H']['active']), 4, 'полки осталось')
        with tap.subtest(16, 'параметры установилсь') as taps:
            for shelf in shelves2['H']['active']:
                taps.eq(shelf.warehouse_group, 'banany', WAREHOUSE_GROUP)
                taps.eq(shelf.width, NEW_PARAMS[WIDTH], WIDTH)
                taps.eq(shelf.height, NEW_PARAMS[HEIGHT], HEIGHT)
                taps.eq(shelf.depth, NEW_PARAMS[DEPTH], DEPTH)
        tap.eq(
            sorted([sh.type for sh in shelves2['H']['active']]),
            [NEW_PARAMS[TYPE], NEW_PARAMS[TYPE],
             OLD_PARAMS[TYPE], OLD_PARAMS[TYPE]],
            'type установился у полок без стоков'
        )
        tap.eq(
            sorted([sh.tags for sh in shelves2['H']['active']]),
            [[], [], NEW_PARAMS[TAGS], NEW_PARAMS[TAGS]],
            'tags установился у полок без стоков'
        )

        tap.eq(
            [err['error'] for err in rack_errors[store2.external_id]['I']],
            ['Некорректное значение water параметра warehouse_group'],
            'ошибки стелажа I лавки 2'
        )
        tap.eq(len(shelves2['I']['active']), 3, '3 полки создалось')
        tap.eq(len(shelves2['I']), 1, 'не активных полок нет')
        with tap.subtest(12, 'корректные параметры установиилсь') as taps:
            for shelf in shelves2['I']['active']:
                taps.eq(
                    shelf.warehouse_group,
                    None,
                    'некорректный параметр пропущен'
                )
                taps.eq(shelf.width, 800, 'width')
                taps.eq(shelf.height, 100, 'height')
                taps.eq(shelf.depth, 200, 'depth')

        tap.eq(
            [err['error'] for err in rack_errors[store2.external_id]['J']],
            ['Не можем деактивировать полки из-за стоков',
             'Нельзя менять поля type, tags полок со стоками'],
            'ошибки стелажа J лавки 2'
        )
        tap.eq(len(shelves2['J']['active']), 3, 'статусы не изменились')
        with tap.subtest(12, 'параметры установиилсь') as taps:
            for shelf in shelves2['J']['active']:
                taps.eq(shelf.warehouse_group, 'banany', WAREHOUSE_GROUP)
                taps.eq(shelf.width, NEW_PARAMS[WIDTH], WIDTH)
                taps.eq(shelf.height, NEW_PARAMS[HEIGHT], HEIGHT)
                taps.eq(shelf.depth, NEW_PARAMS[DEPTH], DEPTH)
        tap.eq(
            sorted([sh.type for sh in shelves2['J']['active']]),
            [NEW_PARAMS[TYPE], OLD_PARAMS[TYPE], OLD_PARAMS[TYPE]],
            'type установился у полок без стоков'
        )
        tap.eq(
            sorted([sh.tags for sh in shelves2['J']['active']]),
            [[], [], NEW_PARAMS[TAGS]],
            'tags установился у полок без стоков'
        )

        tap.eq(
            [err['error'] for err in rack_errors[store2.external_id]['F']],
            [],
            'ошибки стелажа F лавки 2'
        )
        tap.eq(len(shelves2['F']['active']), 2, 'статусы не изменились')
        with tap.subtest(12, 'параметры установиилсь') as taps:
            for shelf in shelves2['F']['active']:
                taps.eq(shelf.warehouse_group, 'banany', WAREHOUSE_GROUP)
                taps.eq(shelf.width, NEW_PARAMS[WIDTH], WIDTH)
                taps.eq(shelf.height, NEW_PARAMS[HEIGHT], HEIGHT)
                taps.eq(shelf.depth, NEW_PARAMS[DEPTH], DEPTH)
                taps.eq(shelf.type, NEW_PARAMS[TYPE], TYPE)
                taps.eq(shelf.tags, NEW_PARAMS[TAGS], TAGS)

        tap.eq(
            [err['error'] for err in rack_errors[fake_store_exid]['H']],
            ['Лавка не найдена'],
            'ошибки несуществующей лавки'
        )

        shelves3 = defaultdict(lambda: defaultdict(list))
        for shelf in await Shelf.list(
            by='full',
            db={'mode': 'slave'},
            conditions=[('store_id', store3.store_id)],
            sort=(),
        ):
            shelves3[shelf.rack][shelf.status].append(shelf)
        tap.eq(len(shelves3['H']['active']), 1, 'статусы не изменились')
        tap.eq(
            [err['error'] for err in rack_errors[store3.external_id]['H']],
            ['Не можем деактивировать полки '
             'из-за созданных на них документов',
             'Нельзя менять поля type, tags '
             'полок с созданным на них документом'],
            'ошибки стелажа H лавки 2'
        )

        os.remove('modify_racks.csv')
        os.remove('errors_modify_racks.csv')


async def test_all_stores_exists(tap, dataset, cfg):
    with tap.plan(1, 'Нет падений из-за удаления ключей словаря'):
        cfg.set('cursor.limit', 1)

        store1 = await dataset.store()
        await dataset.shelf(
            store=store1, rack='H', title='H-1', status='active')

        store2 = await dataset.store()
        await dataset.shelf(
            store=store2, rack='H', title='H-1', status='active')

        with open('modify_racks.csv', 'w', newline='') as f:
            writer = csv.writer(f,
                                delimiter=';',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL,
                                )
            writer.writerows([
                FIELDS,
                [store1.external_id, 'H',
                 None, None, None, None, None, None, 0],
                [store2.external_id, 'H',
                 None, None, None, None, None, None, 0],
            ])

        args = argparse.Namespace(apply=True, csv='modify_racks.csv')
        await main(args)

        rack_errors = defaultdict(lambda: defaultdict(list))
        with open('errors_modify_racks.csv', newline='') as f:
            reader = csv.DictReader(
                f,
                fieldnames=[INDEX, STORE_EXID, SHELF_RACK, SHELF_EXID, ERROR],
                delimiter=';',
                quotechar='"',
                skipinitialspace=True,
            )
            for row in reader:
                rack = row.pop(SHELF_RACK)
                store_exid = row.pop(STORE_EXID)
                rack_errors[store_exid][rack].append(dict(row))

        tap.eq(list(rack_errors.keys()), ['store_external'], 'Нет ошибок')

        os.remove('modify_racks.csv')
        os.remove('errors_modify_racks.csv')


async def test_wrong_title_row(tap, dataset):
    with tap.plan(3, 'Ошибка при неправильных названиях столбцов'):
        store1 = await dataset.store()
        for shelf_index, status in enumerate(
                ['active', 'disabled', 'removed'], start=1
        ):
            await dataset.shelf(
                store=store1,
                rack='H',
                title=f'H-{shelf_index}',
                status=status,
                order=shelf_index,
                warehouse_group='chipsy',
                **OLD_PARAMS
            )

        with open('modify_racks.csv', 'w', newline='') as f:
            writer = csv.writer(f,
                                delimiter=';',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL,
                                )
            writer.writerows([
                FIELDS[::-1],
                [store1.external_id, 'H',
                 None, None, None, None, None, None, 4]
            ])

        args = argparse.Namespace(apply=True, csv='modify_racks.csv')
        await main(args)

        errors = []
        with open('errors_modify_racks.csv', newline='') as f:
            reader = csv.DictReader(
                f,
                delimiter=';',
                quotechar='"',
                skipinitialspace=True,
            )
            for row in reader:
                errors.append(row)
        tap.eq(len(errors), 1, '1 ошибка')
        tap.eq(
            errors[0][ERROR],
            'Наименования столбцов не соответствуют ожидаемым: '
            'store_external, shelf_rack, warehouse_group,'
            ' width, height, depth, type, tags, shelf_qty',
            'текст ошибки правильный'
        )

        shelves = (await Shelf.list(
            by='full',
            db={'mode': 'slave'},
            conditions=[
                ('store_id', store1.store_id),
                ('status', 'active'),
            ],
            sort=(),
        )).list

        tap.eq(len(shelves), 1, 'полки не активировались и не создались')

        os.remove('modify_racks.csv')
        os.remove('errors_modify_racks.csv')


async def test_wrong_separators(tap, dataset):
    with tap.plan(3, 'Ошибка в сепараторах'):
        store1 = await dataset.store()
        for shelf_index, status in enumerate(
                ['active', 'disabled', 'removed'], start=1
        ):
            await dataset.shelf(
                store=store1,
                rack='H',
                title=f'H-{shelf_index}',
                status=status,
                order=shelf_index,
                warehouse_group='chipsy',
                **OLD_PARAMS
            )

        with open('modify_racks.csv', 'w', newline='') as f:
            writer = csv.writer(f,
                                delimiter=',',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL,
                                )
            writer.writerows([
                FIELDS[::-1],
                [store1.external_id, 'H',
                 None, None, None, None, None, None, 4]
            ])

        args = argparse.Namespace(apply=True, csv='modify_racks.csv')
        await main(args)

        errors = []
        with open('errors_modify_racks.csv', newline='') as f:
            reader = csv.DictReader(
                f,
                delimiter=';',
                quotechar='"',
                skipinitialspace=True,
            )
            for row in reader:
                errors.append(row)
        tap.eq(len(errors), 1, '1 ошибка')
        tap.eq(
            errors[0][ERROR],
            'Сепаратор не ; или '
            'наименования столбцов не соответствуют ожидаемым: '
            'store_external, shelf_rack, warehouse_group,'
            ' width, height, depth, type, tags, shelf_qty',
            'текст ошибки правильный'
        )

        shelves = (await Shelf.list(
            by='full',
            db={'mode': 'slave'},
            conditions=[
                ('store_id', store1.store_id),
                ('status', 'active'),
            ],
            sort=(),
        )).list

        tap.eq(len(shelves), 1, 'полки не активировались и не создались')

        os.remove('modify_racks.csv')
        os.remove('errors_modify_racks.csv')
