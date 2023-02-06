import json
from contextlib import contextmanager
from datetime import datetime

import operator
import pytest
import random

from typing import Callable
from yt import wrapper as ytw

from context.settings import settings
from core.connection import create_postgresql_connection, PostgreSQLConnection
from core.utils import get_yt_schema
from gptransfer_client import GPTransferClient, GPTransferException, Status
from .cli_tools.generate_data import random_str
from .helpers import (
    with_tmp_gp_table,
    prepare_yt_table,
    prepare_yt_table_with_infinities,
    generate_gp_tmp_table_name,
    GP_TABLE_CREATE_STATEMENT_WITH_FLOAT,
    grant_all_on_gp,
    revoke_all_on_gp,
    prepare_yt_table_with_errors_in_data,
    prepare_generic_yt_table, Column,
    prepare_generic_gp_table
)

WAIT_TILL_FINISH_TIMEOUT = 5 * 60
REPEAT_EVERY_SEC = 5


@pytest.fixture
def yt_client():
    return ytw.YtClient(
        proxy=settings('YT.PROXY'),
        token=settings('tests.YT_TOKEN'),
        config={'backend': 'rpc'},
    )


@pytest.fixture
def client():
    return GPTransferClient(
        token=settings('tests.YT_TOKEN'),
        gp_user=settings('tests.GP_USER'),
        gp_password=settings('tests.GP_PASSWORD'),
        host=settings('tests.GPTRANSFER_HOST'),
        verify_https=False
    )


@pytest.fixture
def gp_conn():
    with create_postgresql_connection(
            host=settings('tests.GP_HOST'),
            port=settings('tests.GP_PORT'),
            database=settings('GP.DATABASE'),
            user=settings('tests.GP_TEST_SUIT_USER'),
            password=settings('tests.GP_TEST_SUIT_PASSWORD'),
    ) as gp_conn:
        yield gp_conn


@pytest.fixture
def gp_robot_conn():
    with create_postgresql_connection(
            host=settings('tests.GP_HOST'),
            port=settings('tests.GP_PORT'),
            database=settings('GP.DATABASE'),
            user=settings('tests.GP_USER'),
            password=settings('tests.GP_PASSWORD'),
    ) as gp_conn:
        yield gp_conn


@pytest.mark.slow
def test_ping(client):
    # type: (GPTransferClient) -> None
    assert client.ping()


@pytest.mark.slow
def test_yt_to_gp(client, yt_client, gp_conn):
    # type: (GPTransferClient, ytw.YtClient, PostgreSQLConnection) -> None

    yt_table = prepare_yt_table(yt_client, 1000, True)

    with with_tmp_gp_table('stg', 'gp_transfer_test', gp_conn) as tmp_table:
        grant_all_on_gp(gp_conn, tmp_table, 'ALL', settings('GP.USER'))
        process_uuid = client.yt_to_gp(
            yt_table_path=yt_table,
            gp_table_name=tmp_table,
            column_list=['col1', 'col2'],
            table_type='prepared-tsv'
        )

        assert process_uuid

        status = client.check_status(process_uuid)

        assert status
        assert not status.error


def gen_data_by_columns(columns, rows_count=2):
    data = [{c.name: c.gen_func() for c in columns} for _ in range(rows_count)]
    sort_keys = [c.name for c in columns if c.is_key]
    if sort_keys:
        data.sort(key=operator.itemgetter(*sort_keys))
    return data


@contextmanager
def prepare_gp_table_by_columns(gp_conn, columns, data=None, add_grants=('SELECT',)):
    # dict to list of values
    data = list(data or [])
    for i in range(len(data)):
        row_data = []
        for col in columns:
            val = data[i][col.name]
            if col.gp_type == 'json':
                val = json.dumps(val, ensure_ascii=False)
            elif col.gp_type == 'point':
                val = '({lon},{lat})'.format(**val) if val else None

            row_data.append(val)
        data[i] = row_data

    with prepare_generic_gp_table('stg', 'gp_transfer_test', gp_conn, columns, data) as tmp_table:
        gptransfer_user = settings('GP.USER')
        for grant in add_grants:
            grant_all_on_gp(gp_conn, tmp_table, grant, gptransfer_user)
        yield tmp_table


def prepare_yt_table_by_columns(yt_client, columns, data=None, dynamic=False, sorted=False):
    sorted = sorted or dynamic
    yt_attrs = {
        "schema": [
            {
                'name': col.name,
                'type': col.yt_type,
                'sort_order': 'ascending' if col.is_key and sorted else None,
                'required': col.required,
            }
            for col in columns
        ],
        "unique_keys": bool([col.name for col in columns if col.is_key]) if sorted else None,
        "dynamic": dynamic,
    }
    return prepare_generic_yt_table(yt_client, 'gp_transfer_test', yt_attrs, data)


def get_gp_update_mode_params(**kwargs):
    params = {
        "mode": "merge",
        "match_columns": ["distr"],
        "update_columns": ["txt"],
        "UPDATE_CONDITION": "distr::int < 10",
    }
    params.update(**kwargs)
    return params


@pytest.mark.parametrize('params', (
    get_gp_update_mode_params(mode='wrong_mode'),
    get_gp_update_mode_params(match_columns=['distr - ']),
    get_gp_update_mode_params(match_columns='distr'),
    get_gp_update_mode_params(UPDATE_CONDITION='distr::int < 10; select 1'),
    get_gp_update_mode_params(UPDATE_CONDITION='\n  - 123'),
    get_gp_update_mode_params(UPDATE_CONDITION='1' * 71),
))
@pytest.mark.slow
def test_yt_to_gp_update_mode_validations(client, params):
    pytest.raises(GPTransferException, client.yt_to_gp,
                  yt_table_path='//not_use',
                  gp_table_name='not_use',
                  column_list=['not_use'],
                  gp_table_truncate=False,
                  gp_update_mode=params
                  )


@pytest.mark.skip(reason='TAXIDWH-9714 - необходимо обновить gpload')
@pytest.mark.slow
def test_yt_to_gp_gp_update_mode(client, yt_client, gp_conn):
    """
    проверяем не очищается таблица на ГП, и данные корректно обновляются
    """
    columns = (
        Column('distr', 'string', 'varchar', random_str, 'its_key_field'),
        Column('txt', 'string', 'text', random_str),
        Column('other', 'string', 'text', random_str),
    )
    column_names = [c.name for c in columns]
    gp_data = [
        {'distr': '1', 'txt': 'значение уже есть на GP', 'other': '1'},
        {'distr': '2', 'txt': 'значение обновляется из Ытя', 'other': '2'},
        {'distr': '33', 'txt': 'строка неподходящая под условие обновления', 'other': '3'},
    ]
    yt_data = [
        {'distr': '2', 'txt': 'значение обновляется из Ытя (новое)', 'other': '22'},
        {'distr': '3', 'txt': 'новая строка', 'other': '33'},
        {'distr': '33', 'txt': 'строка неподходящая под условие обновления (новая)', 'other': '33'},
    ]
    expected = [
        {'distr': '1', 'txt': 'значение уже есть на GP', 'other': '1'},
        {'distr': '2', 'txt': 'значение обновляется из Ытя (новое)', 'other': '2'},
        {'distr': '3', 'txt': 'новая строка', 'other': '33'},
        {'distr': '33', 'txt': 'строка неподходящая под условие обновления', 'other': '3'},
    ]
    yt_table = prepare_yt_table_by_columns(yt_client, columns, data=yt_data, dynamic=False)
    with prepare_gp_table_by_columns(gp_conn, columns, data=gp_data, add_grants=['ALL']) as gp_table:
        process_uuid = client.yt_to_gp(
            yt_table_path=yt_table,
            gp_table_name=gp_table,
            column_list=column_names,
            gp_table_truncate=False,
            gp_update_mode={
                "mode": "merge",
                "match_columns": ["distr"],
                "update_columns": ["txt"],
                "UPDATE_CONDITION": "distr::int < 10",
            }
        )

        assert process_uuid
        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert status
        assert not status.error
        column_names = column_names
        sql = "select {columns} from {tab} order by distr".format(columns=', '.join(column_names), tab=gp_table)
        gp_data = [dict(zip(column_names, row)) for row in gp_conn.execute_and_get_result(sql)]
        assert gp_data == expected


@pytest.mark.slow
@pytest.mark.parametrize('dynamic_yt_table', (True, False))
def test_gp_to_yt(client, yt_client, gp_conn, dynamic_yt_table):
    """
    проверяем что сгенерированные записи выгружаются корректно и данные на YT равны данным на GP
    + существующие записи в YT не пропали
    """
    columns = (
        Column('distr', 'string', 'varchar', random_str, 'its_key_field'),
        Column('i4', 'int32', 'int4', lambda: 2147483647),
        Column('i8', 'int64', 'int8', lambda: 9223372036854775806),
        Column('vch', 'string', 'varchar', random_str),
        Column('txt', 'string', 'text', random_str),
        Column('bl', 'boolean', 'boolean', lambda: bool(random.randint(0, 1))),
        Column('flt', 'double', 'float', lambda: round(random.random(), 5)),
        Column('flt_inf', 'double', 'float', lambda: float('inf')),
        Column('dt', 'string', 'date', lambda: '2020-03-20'),
        Column('dttm', 'string', 'timestamp', lambda: '2020-03-20 23:59:00'),
        Column('array_of_str', 'any', 'varchar[]', lambda: ['1', '2', '3\n \t, s', '1, 2', '{1,2,3}', None]),
        Column('array_of_str_1', 'any', 'varchar[]', lambda: ['1']),
        Column('array_of_int', 'any', 'int4[]', lambda: [1, 2, 3, None]),
        Column('array_of_float', 'any', 'float[]', lambda: [1.0, 1.2, None]),
        Column('array_empty', 'any', 'varchar[]', lambda: None),
        Column('json_field', 'any', 'json', lambda: {'a': 1.0, 'b': ['txt', 1], 'c': None}),
        Column('uuid_field', 'string', 'uuid', lambda: '2e39a5fa-8590-41e3-b2b9-cbeda0585413'),
        Column('geo_point', 'any', 'point', lambda: {"lat": 2.22, "lon": 1.11}),
    )
    data = gen_data_by_columns(columns, 5)
    yt_table = prepare_yt_table_by_columns(yt_client, columns, data=data[:1], dynamic=dynamic_yt_table)
    with prepare_gp_table_by_columns(gp_conn, columns, data=data[1:]) as gp_table:
        grant_all_on_gp(gp_conn, gp_table, 'SELECT', settings('tests.GP_USER'))
        process_uuid = client.gp_to_yt(
            yt_table_path=yt_table,
            gp_table_name=gp_table,
        )

        assert process_uuid
        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert status
        assert not status.error
        if dynamic_yt_table:
            yt_client.freeze_table(yt_table, sync=True)  # дожидаемся фиксации записей в таблице
            yt_client.unfreeze_table(yt_table, sync=True)
        gp_data = sorted(data, key=lambda i: i['distr'])
        yt_data = sorted(yt_client.read_table(yt_table), key=lambda i: i['distr'])
        assert yt_data == gp_data


@pytest.mark.slow
def test_gp_to_yt_with_etl_updated(client, yt_client, gp_conn):
    """
    проверяем что выгружается дата и время таска в поле etl_updated_column
    """
    columns = (
        Column('distr', 'string', 'varchar', random_str, 'its_key_field'),
    )
    yt_columns = columns + (
        Column('etl_updated', 'string', 'varchar', lambda: None),
    )
    data = gen_data_by_columns(columns, 1)
    yt_table = prepare_yt_table_by_columns(yt_client, yt_columns)

    with prepare_gp_table_by_columns(gp_conn, columns, data=data) as gp_table:
        grant_all_on_gp(gp_conn, gp_table, 'SELECT', settings('tests.GP_USER'))
        process_uuid = client.gp_to_yt(
            yt_table_path=yt_table,
            gp_table_name=gp_table,
            column_list=['distr'],
            etl_updated_column='etl_updated'
        )
        assert process_uuid
        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert status
        assert not status.error

        yt_data = yt_client.read_table(yt_table)
        etl_updated = datetime.strptime(next(yt_data)['etl_updated'], '%Y-%m-%d %H:%M:%S')
        max_diff_sec = 60 * 20  # 20 minutes
        assert (datetime.utcnow() - etl_updated).total_seconds() < max_diff_sec


@pytest.mark.slow
def test_gp_to_yt_with_nulls(client, yt_client, gp_conn):
    """
    проверяем что сгенерированные записи выгружаются корректно и данные на YT равны данным на GP
    + существующие записи в YT не пропали
    """
    columns = (
        Column('distr', 'string', 'varchar', random_str, 'its_key_field'),
        Column('vch_none', 'string', 'varchar', lambda: None),
        Column('escaped', 'string', 'varchar', lambda: 'a \n b \t c \' d " e \\ f \\'),
        Column('vch_empty', 'string', 'varchar', lambda: ''),
        Column('bl_none', 'boolean', 'boolean', lambda: None),
        Column('bl_false', 'boolean', 'boolean', lambda: False),
        Column('flt_none', 'double', 'float', lambda: None),
        Column('flt_0', 'double', 'float', lambda: 0.0),
        Column('array_of_str_none', 'any', 'varchar[]', lambda: [None]),
        Column('array_of_str_empty', 'any', 'varchar[]', lambda: []),
    )
    data = gen_data_by_columns(columns, 1)
    yt_table = prepare_yt_table_by_columns(yt_client, columns, dynamic=False)
    with prepare_gp_table_by_columns(gp_conn, columns, data=data) as gp_table:
        grant_all_on_gp(gp_conn, gp_table, 'SELECT', settings('tests.GP_USER'))
        process_uuid = client.gp_to_yt(
            yt_table_path=yt_table,
            gp_table_name=gp_table,
        )
        assert process_uuid
        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert status
        assert not status.error
        gp_data = sorted(data, key=lambda i: i['distr'])
        yt_data = sorted(yt_client.read_table(yt_table), key=lambda i: i['distr'])
        assert yt_data == gp_data


@pytest.mark.slow
def test_gp_to_yt_gp_has_more_columns(client, yt_client, gp_conn):
    """
    проверяем что выгружаются только поля, переданные в column_list
    """
    columns = (
        Column('distr', 'string', 'varchar', lambda: 'val1'),
        Column('col2', 'string', 'varchar', lambda: 'val2'),
    )
    data = gen_data_by_columns(columns, 1)
    yt_table = prepare_yt_table_by_columns(yt_client, columns)
    with prepare_gp_table_by_columns(gp_conn, columns, data) as gp_table:
        grant_all_on_gp(gp_conn, gp_table, 'SELECT', settings('tests.GP_USER'))
        process_uuid = client.gp_to_yt(
            yt_table_path=yt_table,
            gp_table_name=gp_table,
            column_list=['distr']
        )
        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert status
        assert not status.error
        yt_data = list(yt_client.read_table(yt_table))
        expected_data = [{'distr': i['distr'], 'col2': None} for i in data]
        assert yt_data == expected_data


@pytest.mark.slow
def test_gp_to_yt_with_required_columns(client, yt_client, gp_conn):
    """
    Проверяем что если у таблички на YT есть required поля,
    то они без проблем переливаются.
    """
    columns = (
        Column('distr', 'string', 'varchar', lambda: 'val1', is_key=False, required=True),
        Column('col2', 'string', 'varchar', lambda: 'val2'),
    )
    data = gen_data_by_columns(columns, 1)
    yt_table = prepare_yt_table_by_columns(yt_client, columns)

    # Убедимся, что в схеме на YT у колонки есть признак required
    schema = get_yt_schema(yt_client, yt_table)
    fields = schema['schema']
    for field in fields:
        if field['name'] == 'distr':
            assert field['required']
        else:
            assert not field['required']

    with prepare_gp_table_by_columns(gp_conn, columns, data) as gp_table:
        grant_all_on_gp(gp_conn, gp_table, 'SELECT', settings('tests.GP_USER'))
        process_uuid = client.gp_to_yt(
            yt_table_path=yt_table,
            gp_table_name=gp_table,
            column_list=['distr']
        )
        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert status
        assert not status.error
        yt_data = list(yt_client.read_table(yt_table))
        expected_data = [{'distr': i['distr'], 'col2': None} for i in data]
        assert yt_data == expected_data


@pytest.mark.slow
@pytest.mark.parametrize('set_timezone, expected_data', [
    (False, [{'ts_to_date': 18341, # 2020-03-20
              'ts_to_datetime': 1584666000,
              'ts_to_timestamp': 1584666000000042,
              'date_to_date': 18341,
              'text_to_date': 18341,
              'distr': '2020-03-20 01:00:00.000042'}]),
    (True, [{'ts_to_date': 18340, # 2020-03-19
             'ts_to_datetime': 1584655200,
             'ts_to_timestamp': 1584655200000042,
             # Из date и text в date мы всегда периливаем
             # как есть, без учёта таймзоны, так как у этих типов
             # нет временной составляющей и невозможно правильно сделать сдвиг.
             # Поэтому эти значения отличаются от того, что приходит в ts_to_date
             'date_to_date': 18341, # 2020-03-20
             'text_to_date': 18341,
             'distr': '2020-03-20 01:00:00.000042'}]),
])
def test_gp_to_yt_with_datetime_columns(client, yt_client, gp_conn, set_timezone, expected_data):
    """
    Проверяем что GPTransfer правильно перекодирует поля хранящие дату и время.

    По умолчанию, GTP считает, что дата в UTC, поэтому в одном из наборов данных
    мы проверяем, что ему можно передать таймзону, в которой GP хранит даты.
    """
    time_as_string = '2020-03-20 01:00:00.000042'
    date_as_string = '2020-03-20'
    columns = (
        Column('distr', 'string', 'timestamp without time zone', lambda: time_as_string),
        # Колонки для преобразования из timestamp
        # для этих случаев может применяться преобразование из одной таймзоны в другую
        Column('ts_to_datetime', 'datetime', 'timestamp without time zone', lambda: time_as_string),
        Column('ts_to_date', 'date', 'timestamp without time zone', lambda: time_as_string),
        Column('ts_to_timestamp', 'timestamp', 'timestamp without time zone', lambda: time_as_string),
        # Колонки для преобразования из разных типов в date
        Column('date_to_date', 'date', 'date', lambda: date_as_string),
        Column('text_to_date', 'date', 'text', lambda: date_as_string),
    )
    data = gen_data_by_columns(columns, 1)
    yt_table = prepare_yt_table_by_columns(yt_client, columns)

    if set_timezone:
        timezone = 'Europe/Moscow'
        column_settings = {
            'ts_to_datetime': {'default_timezone': timezone},
            'ts_to_date': {'default_timezone': timezone},
            'ts_to_timestamp': {'default_timezone': timezone},
        }
    else:
        column_settings = None

    column_names = [c.name for c in columns]

    with prepare_gp_table_by_columns(gp_conn, columns, data) as gp_table:
        grant_all_on_gp(gp_conn, gp_table, 'SELECT', settings('tests.GP_USER'))
        process_uuid = client.gp_to_yt(
            yt_table_path=yt_table,
            gp_table_name=gp_table,
            column_list=column_names,
            column_settings=column_settings,
        )
        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert status
        assert not status.error
        yt_data = list(yt_client.read_table(yt_table))
        assert yt_data == expected_data


@pytest.mark.slow
@pytest.mark.parametrize('column_list, part_of_err_msg', [
    (['distr', 'not_exists_col'], 'not_exists_col'),  # в column_list передана колонка которой нет в yt
    (['distr', 'different_types'], 'different_types'),  # колонки с разными типами
    (['distr', 'not_exists_in_gp'], 'not_exists_in_gp'),  # в gp нет нужной колонки
])
def test_gp_to_yt_fails_wrong_columns(client, yt_client, gp_conn, column_list, part_of_err_msg):
    """
    проверяем что срабатывает проверка
    """
    gp_columns = (
        Column('distr', 'string', 'varchar', lambda: 'val1'),
        Column('col2', 'string', 'varchar', lambda: 'val2'),
        Column('different_types', 'double', 'varchar', lambda: 'val2'),
    )
    yt_columns = gp_columns + (
        Column('not_exists_in_gp', 'string', 'varchar', lambda: 'val2'),
    )
    gp_data = gen_data_by_columns(gp_columns, 5)
    yt_table = prepare_yt_table_by_columns(yt_client, yt_columns)
    with prepare_gp_table_by_columns(gp_conn, gp_columns, gp_data) as gp_table:
        grant_all_on_gp(gp_conn, gp_table, 'SELECT', settings('tests.GP_USER'))
        process_uuid = client.gp_to_yt(
            yt_table_path=yt_table,
            gp_table_name=gp_table,
            column_list=column_list
        )
        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert status
        assert status.error
        assert part_of_err_msg in status.message


@pytest.mark.slow
def test_gp_to_yt_fails_wrong_tail(client, yt_client, gp_conn):
    """
    В GP нет колонки по которой сортируется таблица в ЫТе, поэтому должна сработать проверка
    """
    columns = (Column('yt_sorted_by', 'string', 'varchar', random_str, True),
               Column('distr', 'string', 'varchar', random_str))
    gp_data = gen_data_by_columns(columns, 5)
    yt_table = prepare_yt_table_by_columns(yt_client, columns, sorted=True)
    with prepare_gp_table_by_columns(gp_conn, columns, gp_data) as gp_table:
        process_uuid = client.gp_to_yt(
            yt_table_path=yt_table,
            gp_table_name=gp_table,
            column_list=[c.name for c in columns]
        )
        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert status
        assert status.error
        assert 'not supported' in status.message


@pytest.mark.slow
@pytest.mark.parametrize('conn, desc', [
    (gp_conn, ' Тестирует что срабатывают проверки отсутствия прав у робота на gp таблицу'),
    # (gp_robot_conn, 'Создает таблицу от робота и проверяет, что срабатывает проверка на отсутствие прав у пользователя') # todo временно отлючил, робот не может создать таблицу
])
def test_gp_to_yt_fails_wrong_has_not_privileges(client, yt_client, conn, desc):
    gp_conn = next(conn())
    columns = (Column('distr', 'string', 'varchar', random_str),)
    gp_data = gen_data_by_columns(columns, 1)
    yt_table = prepare_yt_table_by_columns(yt_client, columns, sorted=True)
    with prepare_gp_table_by_columns(gp_conn, columns, gp_data, add_grants=[]) as gp_table:
        process_uuid = client.gp_to_yt(
            yt_table_path=yt_table,
            gp_table_name=gp_table,
            column_list=[c.name for c in columns]
        )
        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert status
        assert status.error
        assert 'Permission denied' in status.message


@pytest.mark.slow
def test_gp_to_yt_empty_table(client, yt_client, gp_conn):
    """
    поверим что при пустой таблице выгрузка не падает
    """
    columns = (
        Column('distr', 'string', 'varchar', random_str, 'its_key_field'),
    )
    data = gen_data_by_columns(columns, 0)
    yt_table = prepare_yt_table_by_columns(yt_client, columns, dynamic=False)
    with prepare_gp_table_by_columns(gp_conn, columns, data=data) as gp_table:
        grant_all_on_gp(gp_conn, gp_table, 'SELECT', settings('tests.GP_USER'))
        process_uuid = client.gp_to_yt(
            yt_table_path=yt_table,
            gp_table_name=gp_table,
        )
        assert process_uuid
        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert status
        assert not status.error
        yt_data = yt_client.read_table(yt_table)
        assert not list(yt_data)


@pytest.mark.slow
def test_wait_till_finish(
    client: GPTransferClient,
    yt_client: ytw.YtClient
) -> None:

    yt_table = prepare_yt_table(yt_client, 1000, True)

    with create_postgresql_connection(
            host=settings('tests.GP_HOST'),
            port=settings('GP.PORT'),
            database=settings('GP.DATABASE'),
            user=settings('tests.GP_TEST_SUIT_USER'),
            password=settings('tests.GP_TEST_SUIT_PASSWORD'),
    ) as gp_conn:
        with with_tmp_gp_table('stg', 'gp_transfer_test', gp_conn) as tmp_table:
            grant_all_on_gp(gp_conn, tmp_table, 'ALL', settings('GP.USER'))
            grant_all_on_gp(gp_conn, tmp_table, 'ALL', settings('tests.GP_USER'))

            process_uuid = client.yt_to_gp(
                yt_table_path=yt_table,
                gp_table_name=tmp_table,
                column_list=['col1', 'col2'],
                table_type='prepared-tsv'
            )

            status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                             seconds_to_sleep=REPEAT_EVERY_SEC)

            assert status
            assert not status.error
            assert status.finished


def _assert_gp_table(yt_table, tmp_table, client):
    process_uuid = client.yt_to_gp(
        yt_table_path=yt_table,
        gp_table_name=tmp_table,
        column_list=['col1', 'col2']
    )

    status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                     seconds_to_sleep=REPEAT_EVERY_SEC)

    assert status
    assert not status.error
    assert status.finished


@pytest.mark.slow
def test_simple_schema_table(client, yt_client):
    yt_table = prepare_yt_table(yt_client, 1000, False)

    with create_postgresql_connection(
            host=settings('tests.GP_HOST'),
            port=settings('GP.PORT'),
            database=settings('GP.DATABASE'),
            user=settings('tests.GP_TEST_SUIT_USER'),
            password=settings('tests.GP_TEST_SUIT_PASSWORD'),
    ) as gp_conn:
        with with_tmp_gp_table('stg', 'gp_transfer_test', gp_conn) as tmp_table:
            grant_all_on_gp(gp_conn, tmp_table, 'ALL', settings('GP.USER'))
            grant_all_on_gp(gp_conn, tmp_table, 'ALL', settings('tests.GP_USER'))
            _assert_gp_table(yt_table, tmp_table, client)


@pytest.mark.slow
def test_schema_table_with_infinities(client, yt_client):
    yt_table = prepare_yt_table_with_infinities(yt_client)

    with create_postgresql_connection(
            host=settings('tests.GP_HOST'),
            port=settings('GP.PORT'),
            database=settings('GP.DATABASE'),
            user=settings('tests.GP_TEST_SUIT_USER'),
            password=settings('tests.GP_TEST_SUIT_PASSWORD'),
    ) as gp_conn:
        with with_tmp_gp_table(
                'stg', 'gp_transfer_test', gp_conn,
                create_statement=GP_TABLE_CREATE_STATEMENT_WITH_FLOAT
        ) as tmp_table:
            grant_all_on_gp(gp_conn, tmp_table, 'ALL', settings('GP.USER'))
            grant_all_on_gp(gp_conn, tmp_table, 'ALL', settings('tests.GP_USER'))
            _assert_gp_table(yt_table, tmp_table, client)


@pytest.mark.slow
def test_gp_table_creation(client, yt_client):
    yt_table = prepare_yt_table(yt_client, 1000, False)

    with create_postgresql_connection(
            host=settings('tests.GP_HOST'),
            port=settings('GP.PORT'),
            database=settings('GP.DATABASE'),
            user=settings('tests.GP_TEST_SUIT_USER'),
            password=settings('tests.GP_TEST_SUIT_PASSWORD'),
    ) as gp_conn:
        tmp_table = generate_gp_tmp_table_name('stg', 'gp_transfer_test')
        try:
            _assert_gp_table(yt_table, tmp_table, client)
        finally:
            gp_conn.execute('drop table if exists {}'.format(tmp_table))


@pytest.mark.slow
def test_gpload_fail(
    client: GPTransferClient,
    yt_client: ytw.YtClient
) -> None:

    yt_table = prepare_yt_table_with_errors_in_data(yt_client)

    with create_postgresql_connection(
            host=settings('tests.GP_HOST'),
            port=settings('GP.PORT'),
            database=settings('GP.DATABASE'),
            user=settings('tests.GP_TEST_SUIT_USER'),
            password=settings('tests.GP_TEST_SUIT_PASSWORD'),
    ) as gp_conn:
        with with_tmp_gp_table('stg', 'gp_transfer_test', gp_conn) as tmp_table:
            grant_all_on_gp(gp_conn, tmp_table, 'ALL', settings('GP.USER'))

            process_uuid = client.yt_to_gp(
                yt_table_path=yt_table,
                gp_table_name=tmp_table,
                column_list=['col1', 'col2'],
                table_type='prepared-tsv'
            )

            status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                             seconds_to_sleep=REPEAT_EVERY_SEC)

            assert status
            assert status.error
            assert status.finished


def test_column_name_validation():
    assert GPTransferClient._is_column_name_valid('col1')
    assert GPTransferClient._is_column_name_valid('col1_11')
    assert not GPTransferClient._is_column_name_valid('table.col1')
    assert not GPTransferClient._is_column_name_valid('1col')


def test_gp_table_name_validation():
    assert GPTransferClient._is_gp_table_names_valid('d.b')
    assert GPTransferClient._is_gp_table_names_valid('d1.b1')
    assert not GPTransferClient._is_gp_table_names_valid('1s.b1')
    assert not GPTransferClient._is_gp_table_names_valid('s.b.c')


def test_yt_path_validation():
    assert GPTransferClient._is_yt_path_valid('//home/taxi-dwh')
    assert GPTransferClient._is_yt_path_valid('//home/2016-04-29')
    assert not GPTransferClient._is_yt_path_valid('/home')
    assert not GPTransferClient._is_yt_path_valid('home')


def gp_test_suit_password_getter():
    return settings('tests.GP_TEST_SUIT_PASSWORD')


def gp_password_getter():
    return settings('tests.GP_PASSWORD')


def gpt_fake_pass_getter():
    return 'fake-pass'


def assert_success(status: Status):
    assert status
    assert not status.error
    assert status.finished


def assert_token_is_not_valid(status: Status):
    assert status
    assert status.error
    assert status.finished
    assert 'is not valid' in status.message


def assert_permission_denied(status: Status):
    assert status
    assert status.error
    assert status.finished
    assert 'Permission denied for table' in status.message


def assert_token_does_not_match(status: Status):
    assert status
    assert status.error
    assert status.finished
    assert 'token does not match' in status.message


@pytest.mark.slow
@pytest.mark.parametrize(
    'grant_on_gp_key, grant_role, gpt_user_key, gpt_pass_getter, assert_func, revoke',
    [
        (  # Everything id OK. All creds and all permissions are OK
            'tests.GP_USER',
            'ALL',
            'tests.GP_TEST_SUIT_USER',
            gp_test_suit_password_getter,
            assert_success,
            False,
        ),
        (  # Fake token in gpt client
            'tests.GP_USER',
            'ALL',
            'tests.GP_TEST_SUIT_USER',
            gpt_fake_pass_getter,
            assert_token_is_not_valid,
            False,
        ),
        (  # Wrong token in gpt client
            'tests.GP_USER',
            'ALL',
            'tests.GP_TEST_SUIT_USER',
            gp_password_getter,
            assert_token_does_not_match,
            False,
        ),
        (  # GPT User has no wights on table
            'tests.GP_USER',
            'ALL',
            'tests.GP_TEST_SUIT_USER',
            gp_test_suit_password_getter,
            assert_permission_denied,
            True,
        ),
    ]
)
def test_yt_tp_gp_privileges(
    yt_client: ytw.YtClient,
    gp_conn: PostgreSQLConnection,
    grant_on_gp_key: str,
    grant_role: str,
    gpt_user_key: str,
    gpt_pass_getter: Callable[[], str],
    assert_func: Callable[[Status], None],
    revoke: bool,
) -> None:
    """
    Check if robot or user has not enough privileges to write to GP table
    """

    yt_table = prepare_yt_table(yt_client, 10, True)

    client = GPTransferClient(
        token=settings('tests.YT_TOKEN'),
        gp_user=settings(gpt_user_key),
        gp_password=gpt_pass_getter(),
        host=settings('tests.GPTRANSFER_HOST'),
        verify_https=False
    )

    with with_tmp_gp_table('stg', 'gp_transfer_test', gp_conn) as tmp_table:
        grant_all_on_gp(gp_conn, tmp_table, grant_role, settings(grant_on_gp_key))
        if revoke:
            revoke_all_on_gp(gp_conn, tmp_table, 'UPDATE', settings('tests.GP_TEST_SUIT_USER'))

        process_uuid = client.yt_to_gp(
            yt_table_path=yt_table,
            gp_table_name=tmp_table,
            column_list=['col1', 'col2'],
            table_type='prepared-tsv'
        )

        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert_func(status)


@pytest.mark.slow
@pytest.mark.parametrize(
    'grant_on_gp_key, grant_role, gpt_user_key, gpt_pass_getter, assert_func, revoke',
    [
        (  # Everything id OK. All creds and all permissions are OK
            'tests.GP_USER',
            'SELECT',
            'tests.GP_TEST_SUIT_USER',
            gp_test_suit_password_getter,
            assert_success,
            False,
        ),
        (  # Fake token in gpt client
            'tests.GP_USER',
            'SELECT',
            'tests.GP_TEST_SUIT_USER',
            gpt_fake_pass_getter,
            assert_token_is_not_valid,
            False,
        ),
        (  # Wrong token in gpt client
            'tests.GP_USER',
            'SELECT',
            'tests.GP_TEST_SUIT_USER',
            gp_password_getter,
            assert_token_does_not_match,
            False,
        ),
        (  # GPT User has no wights on table
            'tests.GP_USER',
            'SELECT',
            'tests.GP_TEST_SUIT_USER',
            gp_test_suit_password_getter,
            assert_permission_denied,
            True,
        ),
    ]
)
def test_gp_to_yt_privileges(
    yt_client: ytw.YtClient,
    gp_conn: PostgreSQLConnection,
    grant_on_gp_key: str,
    grant_role: str,
    gpt_user_key: str,
    gpt_pass_getter: Callable[[], str],
    assert_func: Callable[[Status], None],
    revoke: bool,
) -> None:
    """
    Check if robot or user has not enough privileges to read from GP table
    """
    columns = (
        Column('distr', 'string', 'varchar', random_str, 'its_key_field'),
    )
    data = gen_data_by_columns(columns)
    yt_table = prepare_yt_table_by_columns(yt_client, columns, data=data[:1], dynamic=False)

    client = GPTransferClient(
        token=settings('tests.YT_TOKEN'),
        gp_user=settings(gpt_user_key),
        gp_password=gpt_pass_getter(),
        host=settings('tests.GPTRANSFER_HOST'),
        verify_https=False
    )

    with prepare_gp_table_by_columns(gp_conn, columns, data=data[1:], add_grants=[]) as gp_table:
        grant_all_on_gp(gp_conn, gp_table, grant_role, settings(grant_on_gp_key))
        if revoke:
            revoke_all_on_gp(gp_conn, gp_table, 'SELECT', settings('tests.GP_TEST_SUIT_USER'))

        process_uuid = client.gp_to_yt(
            yt_table_path=yt_table,
            gp_table_name=gp_table,
        )

        assert process_uuid
        status = client.wait_till_finish(process_uuid, timeout=WAIT_TILL_FINISH_TIMEOUT,
                                         seconds_to_sleep=REPEAT_EVERY_SEC)
        assert_func(status)
