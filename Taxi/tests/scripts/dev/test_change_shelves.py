import csv
import os
import argparse

from collections import defaultdict

from stall import keyword
from scripts.dev.change_shelves import (FIELDS, main, SHELF_EXID,
                                        STORE_EXID, INDEX, ERROR)


# pylint: disable=too-many-statements,too-many-locals
async def test_change(tap, dataset, uuid):
    with tap.plan(18, 'Смена статуса при наличии стоков'):
        store1 = await dataset.store()
        shelves1 = [
            await dataset.shelf(store=store1, type='store') for _ in range(2)
        ]
        new_title = f'КФ-{keyword.keyword()}'

        store2 = await dataset.store()
        shelves2 = [
            await dataset.shelf(store=store2, width=200) for _ in range(2)
        ]

        await dataset.stock(count=300, reserve=100, shelf=shelves1[0])
        await dataset.stock(count=300, reserve=100, shelf=shelves2[0])

        fake_shelf_exid = uuid()

        with open('change_shelves.csv', 'w', newline='') as f:
            writer = csv.writer(f,
                                delimiter=';',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL,
                                )
            writer.writerow(FIELDS)
            # полка не отключается при наличии остатков
            writer.writerow([
                store1.external_id,
                shelves1[0].external_id,
                'status',
                'disabled'
            ])
            # тег не меняется при наличии остатков
            writer.writerow([
                store1.external_id,
                shelves1[0].external_id,
                'tags',
                'refrigerator'
            ])
            # обработка параметров типа int
            writer.writerow([
                store1.external_id,
                shelves1[0].external_id,
                'width',
                100
            ])
            # required поля не обнуляются
            writer.writerow([
                store1.external_id,
                shelves1[1].external_id,
                'status',
                None
            ])
            # title меняется, пробелы удаляются
            writer.writerow([
                f'  {store1.external_id}  ',
                f'  {shelves1[1].external_id}  ',
                '  title  ',
                f'  {new_title}  ',
            ])
            # rack меняется
            writer.writerow([
                store1.external_id,
                shelves1[1].external_id,
                'rack',
                'КФ'
            ])
            # некорректный тип поля
            writer.writerow([
                store1.external_id,
                shelves1[1].external_id,
                'width',
                'abc'
            ])
            # некорректное имя поля
            writer.writerow([
                store1.external_id,
                shelves1[1].external_id,
                'wrong_field',
                'КФ'
            ])
            # полка не удаляется при наличии остатков
            writer.writerow([
                store2.external_id,
                shelves2[0].external_id,
                'status',
                'removed'
            ])
            # поле не доступно для изменения
            writer.writerow([
                store2.external_id,
                shelves2[0].external_id,
                'external_id',
                '123'
            ])
            # поле не апдейтится в None
            writer.writerow([
                store2.external_id,
                shelves2[0].external_id,
                'width',
                ''
            ])
            # полка без остатков удаляется
            writer.writerow([
                store2.external_id,
                shelves2[1].external_id,
                'status',
                'removed'
            ])
            # полка без остатков меняет тег
            writer.writerow([
                store2.external_id,
                shelves2[1].external_id,
                'tags',
                'refrigerator'
            ])
            # полка не существует
            writer.writerow([
                store1.external_id,
                fake_shelf_exid,
                'status',
                'disabled'
            ])

        args = argparse.Namespace(apply=True, csv='change_shelves.csv')
        await main(args)

        shelf_errors = defaultdict(list)
        with open('errors_change_shelves.csv', newline='') as f:
            reader = csv.DictReader(
                f,
                fieldnames=[INDEX, STORE_EXID, SHELF_EXID, ERROR],
                delimiter=';',
                quotechar='"',
                skipinitialspace=True,
            )
            for row in reader:
                shelf_errors[row[SHELF_EXID]].append([row[INDEX], row[ERROR]])

        with await shelves1[0].reload() as shelf:
            tap.eq(shelf.status, 'active', 'есть сток, статус не изменен')
            tap.eq(shelf.tags, [], 'есть сток, тег не изменен')
            tap.eq(shelf.type, 'store', 'есть сток, тип не изменен')
            tap.eq(shelf.width, 100, 'есть сток, ширина изменена')
            tap.eq(
                shelf_errors[shelf.external_id],
                [['4', 'Нельзя менять поля status, tags полок со стоками']],
                'в ответе скрипта правильные ошибки для полки'
            )

        with await shelves1[1].reload() as shelf:
            tap.eq(shelf.status, 'active', 'статус не изменен на None')
            tap.eq(shelf.title, new_title, 'название не изменено')
            tap.eq(shelf.rack, 'КФ', 'стелаж изменен')
            tap.eq(shelf.width, None, 'ширина не изменена')
            tap.eq(
                shelf_errors[shelf.external_id],
                [['8', 'Неверный тип параметра width'],
                 ['9', 'Неизвестное имя изменяемого параметра wrong_field']],
                'в ответе скрипта правильные ошибки для полки'
            )

        with await shelves2[0].reload() as shelf:
            tap.eq(shelf.status, 'active', 'есть сток, статус не изменен')
            tap.eq(shelf.tags, [], 'теги не изменены')
            tap.eq(
                shelf_errors[shelf.external_id],
                [['11', 'Поле external_id не изменяемо'],
                 ['12', 'Нельзя менять поля status полок со стоками']],
                'в ответе скрипта правильные ошибки для полки')

        with await shelves2[1].reload() as shelf:
            tap.eq(shelf.status, 'removed', 'нет стока, статус изменен')
            tap.eq(shelf.tags, ['refrigerator'], 'нет стока, тег изменен')
            tap.eq(
                shelf_errors[shelf.external_id],
                [],
                'в ответе скрипта нет ошибок для полки'
            )

        tap.eq(
            shelf_errors.get(fake_shelf_exid),
            [['15', 'Полка не найдена']],
            'в ответе скрипта указаны не найденные полки'
        )

        tap.eq(
            shelf_errors.get(SHELF_EXID),
            [['index', 'error']],
            'названия столбцов'
        )

        os.remove('change_shelves.csv')
        os.remove('errors_change_shelves.csv')
