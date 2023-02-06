from datetime import datetime, date, time

from dateutil.tz import tzutc
from mouse import Mouse
import pytest

from libstall.model import coerces
from libstall.model.storable import Attribute
from libstall.money import Money
from stall.csv import parse, build


class SomeTable(Mouse):

    attribute1 = Attribute(
        types=str,
        required=True,
        raise_er_coerce=True,
    )
    attribute2 = Attribute(
        types=int,
        required=False,
        coerce=lambda x: None if x == '' else coerces.maybe_int(x),
        raise_er_coerce=True,
    )
    attribute3 = Attribute(
        types=float,
        required=True,
        coerce=lambda x: None if x == '' else coerces.maybe_float(x),
        raise_er_coerce=True,
    )
    attribute4 = Attribute(
        types=Money,
        required=False,
        coerce=lambda x: None if x == '' else Money(x),
        raise_er_coerce=True,
    )
    attribute5 = Attribute(
        types=datetime,
        required=False,
        coerce=lambda x: None if x == '' else coerces.date_time(x),
        raise_er_coerce=True,
    )
    attribute6 = Attribute(
        types=date,
        required=False,
        coerce=lambda x: None if x == '' else coerces.date(x),
        raise_er_coerce=True,
    )
    attribute7 = Attribute(
        types=time,
        required=False,
        coerce=lambda x: None if x == '' else coerces.time(x),
        raise_er_coerce=True,
    )
    attribute8 = Attribute(
        types=int,
        required=False,
        validate=lambda x: x > 10,
        coerce=lambda x: None if x == '' else coerces.maybe_int(x),
        raise_er_coerce=True,
    )
    attribute9 = Attribute(
        types=(list, tuple),
        required=False,
        raise_er_coerce=True,
        default=lambda: [],
        coerce=lambda x: x.split(',') if isinstance(x, str) else x
    )
    wrong_attribute = Attribute(
        types=int,
        required=False,
        coerce=lambda x: None if x == '' else coerces.maybe_int(x),
        raise_er_coerce=True,
    )


@pytest.mark.parametrize(
    'variant',
    [
        ('\n', ','),
        ('\n', ';'),
        ('\r\n', '\t'),
    ]
)
async def test_parse_correct(tap, variant):
    with tap.plan(11, 'Корректный csv'):
        row_sep, col_sep = variant
        header = [f'attribute{i}' for i in range(
            1, len(SomeTable.meta.fields.keys()))]
        rows = [
            [
                'test', '1', '2.5', '300.05', '2021-01-01 02:00:00',
                '2012-01-01', '00:00', '11', '"1,2,3"'
            ],
            [
                'test2', '2', '3.5', '3.55', '1970-01-01 00:00:00',
                '2020-01-01', '20:00', '12', '"1,2,3"'
            ],
        ]

        csv_with_header = row_sep.join(
            col_sep.join(row) for row in [header] + rows
        )

        result_dict = {
            'attribute1': 'test2',
            'attribute2': 2,
            'attribute3': 3.5,
            'attribute4': Money(3.55),
            'attribute5': datetime(1970, 1, 1, 0, 0, tzinfo=tzutc()),
            'attribute6': date(2020, 1, 1),
            'attribute7': time(20, 0),
            'attribute8': 12,
            'attribute9': ['1', '2', '3'],
        }

        result, errors = parse(
            csv_with_header,
            parsing_class=SomeTable,
        )
        tap.eq(len(result), 2, 'Пришло два объекта')
        tap.eq(len(errors), 0, 'Нет ошибок')
        for attr, value in result_dict.items():
            tap.eq(
                getattr(result[-1], attr),
                value,
                f'{attr} типа {type(value)} совпадают с parsing_class'
            )


async def test_parse_with_none(tap):
    with tap.plan(3, 'csv с пустым полем'):
        header = [f'attribute{i}' for i in range(1, 9)]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + [
                [
                    'test3', '', '3.5', '3.55', '1970-01-01 00:00:00',
                    '2020-01-01', '20:00', '12'
                ],
            ]
        )
        result, errors = parse(
            csv_with_header,
            parsing_class=SomeTable,
        )
        tap.eq(len(result), 1, 'Пришел один объект')
        tap.eq(result[0].attribute2, None, 'Пришло None поле')
        tap.eq(errors, [], 'Нет ошибок')


async def test_parse_incorrect_coerce(tap):
    with tap.plan(4, 'Ошибка coerce'):
        header = [f'attribute{i}' for i in range(1, 9)]
        rows = [
            [
                'test', '1', '2.5', '300.05', '2021-01-01 02:00:00',
                '2012-01-01', '00:00', '11'
            ],
            [
                'test2', '2', '3.5', '3.55', '1970-01-01 00:00:00',
                '2020-01-01', '20:00', '12'
            ],
        ]

        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows + [
                [
                    'test3', 'aaa', '3.5', '3.55', '1970-01-01 00:00:00',
                    '2020-01-01', '20:00', '12'
                ],
            ]
        )
        errors = parse(
            csv_with_header,
            parsing_class=SomeTable,
        )[1]
        tap.eq(len(errors), 1, 'Ошибка найдена')
        tap.eq(errors[0].line, 3, 'Строка с ошибкой')
        tap.eq(errors[0].column, 'attribute2', 'Колонка с ошибкой')
        tap.eq(errors[0].code, 'ER_COERCE', 'Код ошибки')


async def test_parse_incorrect_valid(tap):
    with tap.plan(4, 'Ошибка validate'):
        header = [f'attribute{i}' for i in range(1, 9)]
        rows = [
            [
                'test', '1', '2.5', '300.05', '2021-01-01 02:00:00',
                '2012-01-01', '00:00', '11'
            ],
            [
                'test2', '2', '3.5', '3.55', '1970-01-01 00:00:00',
                '2020-01-01', '20:00', '12'
            ],
        ]

        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows + [
                [
                    'test3', '1', '3.5', '3.55', '1970-01-01 00:00:00',
                    '2020-01-01', '20:00', '1'
                ]
            ]
        )
        errors = parse(
            csv_with_header,
            parsing_class=SomeTable,
        )[1]
        tap.eq(len(errors), 1, 'Ошибка найдена')
        tap.eq(errors[0].line, 3, 'Строка с ошибкой')
        tap.eq(errors[0].column, 'attribute8', 'Колонка с ошибкой')
        tap.eq(errors[0].code, 'ER_VALIDATE', 'Код ошибки')


async def test_parse_required(tap):
    with tap.plan(4, 'Ошибка required'):
        header = [f'attribute{i}' for i in range(1, 9)]
        rows = [
            [
                'test', '1', '2.5', '300.05', '2021-01-01 02:00:00',
                '2012-01-01', '00:00', '11'
            ],
            [
                'test2', '2', '3.5', '3.55', '1970-01-01 00:00:00',
                '2020-01-01', '20:00', '12'
            ],
        ]

        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows + [
                [
                    'test3', '1', '', '3.55', '1970-01-01 00:00:00',
                    '2020-01-01', '20:00', '12'
                ],
            ]
        )
        errors = parse(
            csv_with_header,
            parsing_class=SomeTable,
        )[1]
        tap.eq(len(errors), 1, 'Ошибка найдена')
        tap.eq(errors[0].line, 3, 'Строка с ошибкой')
        tap.eq(errors[0].column, 'attribute3', 'Колонка с ошибкой')
        tap.eq(errors[0].code, 'ER_FIELD_UNDEFINED', 'Код ошибки')


async def test_build_objects(tap):
    with tap.plan(1, 'Объекты в csv'):
        objects = [
            SomeTable(
                attribute1='test',
                attribute2=1,
                attribute3=4.0
            ),
            SomeTable(
                attribute1='test2',
                attribute2=2,
                attribute3=5.0,
            ),
        ]
        result_csv = build(
            objects,
            ['attribute1', 'attribute2'],
        )
        right_csv = 'attribute1;attribute2\r\ntest;1\r\ntest2;2\r\n'
        tap.eq(result_csv, right_csv, 'Csv сгенерирован верно')


async def test_build_dicts(tap):
    with tap.plan(1, 'Словари в csv'):
        objects = [
            {
                'attribute1': 'test',
                'attribute2': 1,
                'attribute3': 4.0
            },
            {
                'attribute1': 'test2',
                'attribute2': 2,
                'attribute3': 5.0,
            },
        ]
        result_csv = build(
            objects,
            ['attribute1', 'attribute2'],
        )
        right_csv = 'attribute1;attribute2\r\ntest;1\r\ntest2;2\r\n'
        tap.eq(result_csv, right_csv, 'Csv сгенерирован верно')


async def test_build_types(tap):
    with tap.plan(1, 'Объекты в csv'):
        objects = [
            SomeTable(
                attribute1='test',
                attribute2=1,
                attribute3=4.1,
                attribute4=Money('300.01'),
                attribute5=datetime(1970, 1, 1, 0, 0, 0),
                attribute6=date(1970, 1, 1),
                attribute7=time(0, 0, 0),
            ),
        ]
        attributes = [f'attribute{i+1}' for i in range(7)]
        result_csv = build(
            objects,
            attributes,
        )
        right_csv = '\r\n'.join(
            [
                ';'.join(attributes),
                'test;1;4.1;300.01;1970-01-01 00:00:00;1970-01-01;00:00:00\r\n',
            ]
        )
        tap.eq(result_csv, right_csv, 'Csv сгенерирован верно')


async def test_renamed_import(tap):
    with tap.plan(4, 'Проверка импорта с переименованными полями'):

        header = [f'attribute{i}' for i in range(1, 8)]
        header.append('renamed')
        rows = [
            [
                'test', '1', '2.5', '300.05', '2021-01-01 02:00:00',
                '2012-01-01', '00:00', '11'
            ],
            [
                'test2', '2', '3.5', '3.55', '1970-01-01 00:00:00',
                '2020-01-01', '20:00', '12'
            ],
        ]

        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )

        result, errors = parse(
            csv_with_header,
            parsing_class=SomeTable,
            renames={
                'renamed': 'attribute8',
            }
        )
        tap.eq(len(result), 2, 'Пришло два объекта')
        tap.eq(len(errors), 0, 'Нет ошибок')
        tap.eq(result[0].attribute8, 11, 'Атрибут распаршен верно')
        tap.eq(result[1].attribute8, 12, 'Атрибут распаршен верно')


async def test_renamed_export(tap):
    with tap.plan(1, 'Проверка экспорта с переименованными полями'):
        objects = [
            SomeTable(
                attribute1='test',
                attribute2=1,
                attribute3=4.0
            ),
            SomeTable(
                attribute1='test2',
                attribute2=2,
                attribute3=5.0,
            ),
        ]
        result_csv = build(
            objects,
            ['attribute1', 'attribute2'],
            renames={
                'attribute1': 'renamed'
            }
        )
        right_csv = 'renamed;attribute2\r\ntest;1\r\ntest2;2\r\n'
        tap.eq(result_csv, right_csv, 'Csv сгенерирован верно')
