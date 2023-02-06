from datetime import date, time, datetime, timezone
from collections import namedtuple

import pytest

from stall.script import (
    parse_uuid, parse_date, parse_time, parse_datetime, csv2dicts, objects2csv
)


async def test_parse_uuid(tap):
    with tap.plan(5, 'parse_uuid'):
        tap.ok(
            parse_uuid('d62eb1df-865e-47ac-a2b1-72cd3bcd0338'),
            'UUID c тире'
        )
        tap.ok(parse_uuid('d62eb1df865e47aca2b172cd3bcd0338'), 'UUID без тире')

        tap.ok(not parse_uuid(None), 'None')
        tap.ok(not parse_uuid(''), 'Пустая строка')
        tap.ok(not parse_uuid('asd'), 'Неверное значение')


async def test_parse_date(tap):
    with tap.plan(5, 'parse_date'):
        tap.eq(parse_date('2020-12-01'), date(2020, 12, 1), 'RFC')
        tap.eq(parse_date('3.7.2020'), date(2020, 7, 3), 'RU')

        tap.ok(not parse_date(None), 'None')
        tap.ok(not parse_date(''), 'Пустая строка')
        tap.ok(not parse_date('fgh1'), 'Неверное значение')


async def test_parse_time(tap):
    with tap.plan(4, 'parse_time'):
        tap.eq(parse_time('11:30:44'), time(11, 30, 44), 'RFC')

        tap.ok(not parse_time(None), 'None')
        tap.ok(not parse_time(''), 'Пустая строка')
        tap.ok(not parse_time('fgh1'), 'Неверное значение')


async def test_parse_datetime(tap):
    with tap.plan(4, 'parse_datetime'):
        tap.eq(
            parse_datetime('2020-12-01 11:30:44'),
            datetime(2020, 12, 1, 11, 30, 44, tzinfo=timezone.utc),
            'RFC'
        )

        tap.ok(not parse_datetime(None), 'None')
        tap.ok(not parse_datetime(''), 'Пустая строка')
        tap.ok(not parse_datetime('fgh1'), 'Неверное значение')


@pytest.mark.parametrize(
    'variant',
    [
        ('\n', ','),
        ('\n', ';'),
        ('\r\n', '\t'),
    ]
)
def test_csv2dicts(tap, variant):
    row_sep, col_sep = variant

    with tap.plan(4):
        header = ['колонка_один', 'колонка_два', 'колонка_три']
        rows = [
            ['"идет , бычок"', 'качается', '100'],
            ['"водка ; пиво"', 'сосиска', '200'],
            ['"foo \t bar"', 'spam', '300'],
        ]

        csv_with_header = row_sep.join(
            col_sep.join(row) for row in [header] + rows
        )
        csv_no_header = row_sep.join(col_sep.join(row) for row in rows)

        result_with_header = csv2dicts(csv_with_header)
        result_no_header = csv2dicts(csv_no_header, header)
        tap.eq(
            result_with_header,
            result_no_header,
            'корректно разбираем csv с хедером и без',
        )

        result = result_with_header
        tap.eq(len(result), len(rows), 'все строки на месте')
        tap.eq(list(result[0].keys()), header, 'корректный хедер')
        tap.eq(
            [list(row.values()) for row in result],
            [[i.strip('"') for i in row] for row in rows],
            'корректные значения ячеек',
        )


def test_csv_single_col(tap):
    with tap.plan(1):
        r = csv2dicts('col\n\r1\n\r2\n\r')
        tap.eq(r, [{'col': '1'}, {'col': '2'}], 'таблица с одной колонкой')


def test_csv_russian(tap):
    with tap.plan(1):
        r = csv2dicts('колонка;"колонка два"\n\r1;раз\n\r2;"раз два"\n\r')
        tap.eq(
            r,
            [
                {'колонка': '1', 'колонка_два': 'раз'},
                {'колонка': '2', 'колонка_два': 'раз два'}
            ],
            'таблица в российском формате',
        )


def test_csv_real1(tap):
    with tap.plan(1, 'падение на реальных данных'):
        r = csv2dicts(
            "external_id\r\n"
            "4aef430779b342ff8cca6ab5d8eb4880\r\n"
            "a6ea8d13c80442ddb334700f92b1b8e3\r\n"
            "75cf073494b94ae7b7bd1ae03782653c\r\n"
            "e8adf7e11d5d4313b03897d3376c3677\r\n"
            "d6dd7ad1f2254e15831fa04e811f4995\r\n",
        )
        tap.eq(
            r,
            [
                {'external_id': '4aef430779b342ff8cca6ab5d8eb4880'},
                {'external_id': 'a6ea8d13c80442ddb334700f92b1b8e3'},
                {'external_id': '75cf073494b94ae7b7bd1ae03782653c'},
                {'external_id': 'e8adf7e11d5d4313b03897d3376c3677'},
                {'external_id': 'd6dd7ad1f2254e15831fa04e811f4995'},
            ],
            'тестовые данные',
        )


def test_objects2csv(tap):
    with tap.plan(2, 'Проверка конвертации объектов/словарей в CSV'):
        # словари
        d = {
            'empty_str': '',
            'not_empty_str': 'not empty string',
            'empty_list': [],
            'not_empty_list': [123, 'qweqwe'],
            'None_values': None,
        }
        expected = \
            "empty_str;not_empty_str;empty_list;not_empty_list;None_values\n"\
            ";not empty string;;123,qweqwe;\n"\
            ";not empty string;;123,qweqwe;\n"\
            ";not empty string;;123,qweqwe;\n"
        tap.eq(
            objects2csv([d, d, d], fieldnames=list(d.keys())),
            expected,
            'конвертация словарей в CSV'
        )

        # объекты
        TestObject = namedtuple(
            'TestObject',
            "empty_str not_empty_str empty_list not_empty_list None_values"
        )
        obj = TestObject('', 'not empty string', [], [123, 'qweqwe'], None)
        tap.eq(
            objects2csv([obj, obj, obj], fieldnames=list(d.keys())),
            expected,
            'конвертация объектов в CSV'
        )
