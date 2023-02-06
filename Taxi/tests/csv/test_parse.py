from datetime import date, time, datetime, timezone
import re

from mouse import Mouse
import pytest

from libstall.model import coerces
from libstall.model.storable import Attribute
from stall.csv import parse


class UUIDParser(Mouse):
    uuid_attr = Attribute(
        types=str,
        required=True,
        validate=lambda x: x and re.match(r'^[0-9a-fA-F\-]{32,}$', x),
        raise_er_coerce=True,
    )


class DateParser(Mouse):
    date_attr = Attribute(
        types=date,
        required=True,
        coerce=coerces.date,
        raise_er_coerce=True,
    )


class TimeParser(Mouse):
    time_attr = Attribute(
        types=time,
        required=True,
        coerce=coerces.time,
        raise_er_coerce=True,
    )


class DateTimeParser(Mouse):
    datetime_attr = Attribute(
        types=datetime,
        required=True,
        coerce=coerces.date_time,
        raise_er_coerce=True,
    )


class StringParser(Mouse):
    str_attr1 = Attribute(
        types=str,
        required=True,
        raise_er_coerce=True,
    )
    str_attr2 = Attribute(
        types=str,
        required=True,
        raise_er_coerce=True,
    )


class ListParser(Mouse):
    list_attr = Attribute(
        types=(list, tuple),
        required=True,
        raise_er_coerce=True,
        default=lambda: [],
        coerce=lambda x: x.split(',') if isinstance(x, str) else x
    )


class MultipleAttrs(Mouse):
    column_one = Attribute(
        types=str,
        required=True,
        raise_er_coerce=True
    )
    column_two = Attribute(
        types=str,
        required=True,
        raise_er_coerce=True
    )
    extra_column = Attribute(
        types=str,
        required=False,
        raise_er_coerce=True
    )


async def test_parse_uuid_right(tap):
    with tap.plan(4, 'UUID верны в csv'):
        header = ['uuid_attr']
        rows = [
            ['d62eb1df-865e-47ac-a2b1-72cd3bcd0338'],
            ['d62eb1df865e47aca2b172cd3bcd0338'],
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )
        result, errors = parse(
            csv_with_header,
            parsing_class=UUIDParser,
        )
        tap.eq(len(result), 2, 'Вернулось два объекта')
        tap.eq(len(errors), 0, 'Ошибок нет')
        uuids = [uuid_obj.uuid_attr for uuid_obj in result]
        tap.in_ok(rows[0][0], uuids, 'Первый uuid верен')
        tap.in_ok(rows[1][0], uuids, 'Второй uuid верен')


@pytest.mark.parametrize('line', [['', ''], ['asd']])
async def test_parse_uuid_wrong(tap, line):
    with tap.plan(5, 'UUID не верны в csv'):
        header = ['uuid_attr']
        rows = [
            line
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )
        result, errors = parse(
            csv_with_header,
            parsing_class=UUIDParser,
        )
        tap.eq(len(result), 0, 'Нет объектов')
        tap.eq(len(errors), 1, 'Одна ошибка')
        tap.eq(errors[0].code, 'ER_VALIDATE', 'Ошибка валидации')
        tap.eq(errors[0].column, 'uuid_attr', 'Колонка uuid_attr')
        tap.eq(errors[0].line, 1, 'Ошибка на строке 2')


async def test_parse_date_right(tap):
    with tap.plan(3, 'Даты верны в csv'):
        header = ['date_attr']
        rows = [
            ['2020-12-01'],
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )

        result, errors = parse(
            csv_with_header,
            parsing_class=DateParser,
        )

        tap.eq(len(result), 1, 'Вернулся один объект')
        tap.eq(len(errors), 0, 'Ошибок нет')
        tap.eq(date(2020, 12, 1), result[0].date_attr, 'Дата в RFC верна')


async def test_parse_date_empty(tap):
    with tap.plan(5, 'Дата отсутствует'):
        header = ['date_attr', 'date_attr2']
        rows = [
            ['', ''],
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )

        print(csv_with_header)

        result, errors = parse(
            csv_with_header,
            parsing_class=DateParser,
        )

        tap.eq(len(result), 0, 'Нет объектов')
        tap.eq(len(errors), 1, 'Одна ошибка')
        tap.eq(errors[0].code, 'ER_FIELD_UNDEFINED', 'Поле не определено')
        tap.eq(errors[0].column, 'date_attr', 'Колонка date_attr')
        tap.eq(errors[0].line, 1, 'Ошибка на строке 2')


async def test_parse_date_wrong(tap):
    with tap.plan(5, 'Дата не верна в csv'):
        header = ['date_attr']
        rows = [
            ['fgh1'],
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )

        result, errors = parse(
            csv_with_header,
            parsing_class=DateParser,
        )

        tap.eq(len(result), 0, 'Нет объектов')
        tap.eq(len(errors), 1, 'Одна ошибка')
        tap.eq(errors[0].code, 'ER_COERCE', 'Неверный формат')
        tap.eq(errors[0].column, 'date_attr', 'Колонка date_attr')
        tap.eq(errors[0].line, 1, 'Ошибка на строке 2')


async def test_parse_time_right(tap):
    with tap.plan(3, 'Правильное время в csv'):
        header = ['time_attr']
        rows = [
            ['11:30:44'],
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )

        result, errors = parse(
            csv_with_header,
            parsing_class=TimeParser,
        )

        tap.eq(len(result), 1, 'Один объект')
        tap.eq(len(errors), 0, 'Нет ошибок')
        tap.eq(time(11, 30, 44), result[0].time_attr, 'Время верно')


async def test_parse_time_empty(tap):
    with tap.plan(5, 'Время отсутствует'):
        header = ['time_attr', 'time_attr2']
        rows = [
            ['', ''],
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )

        result, errors = parse(
            csv_with_header,
            parsing_class=TimeParser,
        )

        tap.eq(len(result), 0, 'Нет объектов')
        tap.eq(len(errors), 1, 'Одна ошибка')
        tap.eq(errors[0].code, 'ER_FIELD_UNDEFINED', 'Поле не определено')
        tap.eq(errors[0].column, 'time_attr', 'Колонка time_attr')
        tap.eq(errors[0].line, 1, 'Ошибка на строке 2')


async def test_parse_time_wrong(tap):
    with tap.plan(5, 'Время не верно в csv'):
        header = ['time_attr']
        rows = [
            ['fgh1'],
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )

        result, errors = parse(
            csv_with_header,
            parsing_class=TimeParser,
        )

        tap.eq(len(result), 0, 'Нет объектов')
        tap.eq(len(errors), 1, 'Одна ошибка')
        tap.eq(errors[0].code, 'ER_COERCE', 'Неверный формат')
        tap.eq(errors[0].column, 'time_attr', 'Колонка time_attr')
        tap.eq(errors[0].line, 1, 'Ошибка на строке 2')


async def test_parse_datetime_right(tap):
    with tap.plan(3, 'parse_datetime'):
        header = ['datetime_attr']
        rows = [
            ['2020-12-01 11:30:44'],
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )

        result, errors = parse(
            csv_with_header,
            parsing_class=DateTimeParser,
        )

        tap.eq(len(result), 1, 'Один объект')
        tap.eq(len(errors), 0, 'Нет ошибок')
        tap.eq(
            datetime(2020, 12, 1, 11, 30, 44, tzinfo=timezone.utc),
            result[0].datetime_attr,
            'Дата/Время верно',
        )


async def test_parse_datetime_empty(tap):
    with tap.plan(5, 'Дата/Время отсутствует'):
        header = ['datetime_attr', 'datetime_attr2']
        rows = [
            ['', ''],
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )

        result, errors = parse(
            csv_with_header,
            parsing_class=DateTimeParser,
        )

        tap.eq(len(result), 0, 'Нет объектов')
        tap.eq(len(errors), 1, 'Одна ошибка')
        tap.eq(errors[0].code, 'ER_FIELD_UNDEFINED', 'Поле не определено')
        tap.eq(errors[0].column, 'datetime_attr', 'Колонка datetime_attr')
        tap.eq(errors[0].line, 1, 'Ошибка на строке 2')


async def test_parse_datetime_wrong(tap):
    with tap.plan(5, 'Дата/Время не верно в csv'):
        header = ['datetime_attr']
        rows = [
            ['fgh1'],
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )

        result, errors = parse(
            csv_with_header,
            parsing_class=DateTimeParser,
        )

        tap.eq(len(result), 0, 'Нет объектов')
        tap.eq(len(errors), 1, 'Одна ошибка')
        tap.eq(errors[0].code, 'ER_COERCE', 'Неверный формат')
        tap.eq(errors[0].column, 'datetime_attr', 'Колонка datetime_attr')
        tap.eq(errors[0].line, 1, 'Ошибка на строке 2')


def test_csv_russian(tap):

    with tap.plan(3):
        header = ['колонка', 'колонка 2']
        rows = [
            ['1', 'раз'],
            ['2', 'раз два'],
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )

        result, errors = parse(
            csv_with_header,
            parsing_class=StringParser,
            renames={
                'колонка': 'str_attr1',
                'колонка 2': 'str_attr2',
            },
        )
        tap.eq(len(result), 2, 'Пришло 2 объекта')
        tap.eq(len(errors), 0, 'Нет ошибок')
        tap.eq(
            [
                [obj.str_attr1, obj.str_attr2] for obj in result
            ],
            rows,
            'таблица в российском формате',
        )


async def test_parse_list(tap):
    with tap.plan(3, 'Список'):
        header = ['list_attr', 'other_field']
        rows = [
            ['1,2,3', 'abc'],
        ]
        csv_with_header = '\n'.join(
            ';'.join(row) for row in [header] + rows
        )

        result, errors = parse(
            csv_with_header,
            parsing_class=ListParser,
        )

        tap.eq(len(result), 1, 'Один объект')
        tap.eq(len(errors), 0, 'Нет ошибок')
        tap.eq(result[0].list_attr, ['1', '2', '3'], 'Список верный')


@pytest.mark.parametrize('input_csv,fieldnames,obj_count,first_obj', [
    # Порядок из CSV файла
    (
        'column_two;column_one;extra_column\n'
        'second;first;extra\n',
        None,
        1,
        {
            'column_one': 'first',
            'column_two': 'second',
            'extra_column': 'extra'
        }
    ),

    # Порядок из файла с лишним полем
    (
        'extra_column;column_one;column_two;something\n'
        'extra1;first1;second1;321\n'
        'extra2;first2;second2;321\n',
        None,
        2,
        {
            'column_one': 'first1',
            'column_two': 'second1',
            'extra_column': 'extra1'
        }
    ),

    # порядок из файла (игнорируем переданный порядок)
    # парсим только запрошенные поля
    (
        'extra_column;column_one;column_two;something\n'
        'extra1;first1;second1;321\n'
        'extra2;first2;second2;321\n',
        ['column_two', 'column_one'],
        2,
        {
            'column_one': 'first1',
            'column_two': 'second1',
            'extra_column': None,

        }
    ),

    # порядок из переданных заголовков
    (
        'first1;second1;321\n'
        'first2;second2;321\n',
        ['column_one', 'column_two'],
        2,
        {
            'column_one': 'first1',
            'column_two': 'second1',
            'extra_column': None,
        }
    ),
])
async def test_parse_columns_order(
        tap, input_csv, fieldnames, obj_count, first_obj):
    with tap.plan(3, 'Проверяем упорядочивание колонок в CSV'):
        result, errors = parse(
            input_csv,
            parsing_class=MultipleAttrs,
            fieldnames=fieldnames
        )
        tap.eq(len(result), obj_count, 'Нужное кол-во объектов')
        tap.eq(len(errors), 0, 'Нет ошибок')
        tap.eq(
            result[0].pure_python(),
            first_obj,
            'Первый объект совпадает'
        )


@pytest.mark.parametrize('input_csv', [
    # с заголовком
    (
        'something\tcolumn_two\trenamed\trenamed_miss\tcolumn_one\n'
        'random_here\t222\trenamed_value\tmiss_value\t111\n'
        'random_here\t222\trenamed_value\tmiss_value\t111\n'
    ),
    # без заголовка
    (
        '111\t222\trandom_here\trenamed_value\tmiss_value\n'
        '111\t222\trandom_here\trenamed_value\tmiss_value\n'
    )
])
async def test_parse_redundant_fields(tap, input_csv):
    with tap.plan(3, 'Обработка полей, которых нет в модели'):
        # В парсинге указаны дополнительные поля, которых нет в классе

        result, errors = parse(
            input_csv,
            parsing_class=MultipleAttrs,
            fieldnames=['column_one', 'column_two', 'something', 'renamed'],
            renames={
                'renamed': 'extra_column',
                'renamed_miss': 'extra_another',
            },
        )
        tap.eq(len(result), 2, 'Два объекта')
        tap.eq(len(errors), 0, 'Нет ошибок')
        tap.eq(
            result[0].pure_python(),
            {
                'column_one': '111',
                'column_two': '222',
                'extra_column': 'renamed_value'
            },
            'Первый объект правильно собрали'
        )
