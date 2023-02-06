# coding: utf-8

from past.builtins import basestring
import os

import numpy as np
import pandas as pd
import pytest
import psycopg2
import yt.wrapper as yt
from business_models.util import Factory, Handler, change_coding, Timer, generate_random_string
from business_models.databases.database import Database
from business_models.config_holder import  ConfigHolder
from business_models.databases import hahn, HahnDataLoader, GreenplumManager, greenplum, gdocs
from business_models.databases import get_mongo_df, ClickHouseClient
from sqlalchemy.types import String
import getpass

from .common import make_path


USER = getpass.getuser().replace('-', '_')


# Монга не работает
# def mongo_tests():
#     """
#     Пример использования функции. Гонять тест можно только там, где есть дырки до монги
#     """
#     df = get_mongo_df(query={'date_to': None}, collection='tariffs')
#     assert not df.empty, "Empty dataframe from mongo"


def is_clickhouse_unavailable():
    return os.system("which clickhouse-client") != 0 or\
           not ConfigHolder().get_any_attribute('taxi_clickhouse_password', validate=True)


@pytest.mark.skipif(is_clickhouse_unavailable, reason="clickhouse-client not installed!")
def clickhouse_tests():
    """
    В mylib_config.json должны быть настройки taxi_clickhouse_user и taxi_clickhouse_password
    """
    click = ClickHouseClient()
    df = click.run_query(query="show tables from taxi")
    assert not df.empty, "Empty dataframe from clickhouse"

    # test empty dataframe write no fail
    empty_frame = pd.DataFrame(columns=["name", "value", "result"])
    click.write_table(table_name="bm_tiny_test", dataframe=empty_frame)
    # test run query. table name with database. no parse answer
    click.run_query("drop table taxi.bm_tiny_test", parsed=False)


@pytest.mark.parametrize(
    "worker, colname, check_result_array, call_kwargs",
    [
        [HahnDataLoader(), "column0", True, {'syntax_version': 1}],
        [GreenplumManager(), "?column?", False, {}]
    ]
)
def sql_queries_tests(worker, colname, check_result_array, call_kwargs):
    test_query_path = make_path("test_hahn_query.yql")
    test_query_second_path = make_path("test_hahn_second_query.yql")

    num = 100500
    result = worker("""
    Select 1;
    """, query_file_paths=test_query_path, query_format_kwargs={"number": 100500}, **call_kwargs)
    golden_one = pd.DataFrame([[1]], columns=[colname])
    golden_two = pd.DataFrame([[num]], columns=[colname])
    if check_result_array:
        assert len(result) == 2
        assert result[0].equals(golden_one)
        assert result[1].equals(golden_two)
    else:
        assert result.equals(golden_two)
    worker("""
    Select 1
    """, query_file_paths=[test_query_path, test_query_second_path], query_format_kwargs={"number": 100500}, **call_kwargs)
    worker("""
    Select 1
    """, query_file_paths=[test_query_second_path, test_query_path], query_format_kwargs={"number": 100500}, **call_kwargs)


def hahn_share_url_tests():
    single = hahn("select 1", return_shared_url=True, syntax_version=1)
    assert len(single) == 2
    assert isinstance(single[0], pd.DataFrame)
    assert isinstance(single[1], basestring)

    many = hahn("select 1; select 2", return_shared_url=True, syntax_version=1)
    assert len(many) == 2
    assert isinstance(many[0], list)
    assert isinstance(many[1], basestring)


def hahn_public_link_tests():
    test_query, query_url = hahn("select 1", return_shared_url=True)
    query_id = query_url.split('/')[-1]
    pd.testing.assert_frame_equal(test_query, hahn(operation_url=query_url))
    pd.testing.assert_frame_equal(test_query, hahn(operation_url=query_id))
    hahn(query="select 1", operation_url=query_url)


def hahn_write_read_tests():
    sample_df = pd.DataFrame([["a", 3, "2019-08-01", np.nan],
                              ["v", 4, "2019-07-01", 0.4],
                              ["c", None, "2019-06-01", 0.3],
                              ["d", 3, "2020-04-05", -np.nan]],
                             columns=["str", "int", "date", "float"]).sort_index(axis=1)
    sample_df_export = sample_df.copy()
    sample_df_export["date"] = pd.to_datetime(sample_df_export["date"])
    with yt.TempTable(prefix="hahn_test") as tmp:
        hahn.write_table(tmp, sample_df_export)
        read_df = hahn.load_result(tmp, chunksize=2).sort_index(axis=1)
        pd.testing.assert_frame_equal(sample_df, read_df)


@pytest.mark.greenplum
def greenplum_write_read_tests():
    sample_df = pd.DataFrame([["a", 3, "2019-08-01", np.nan],
                              ["v", 4, "2019-07-01", 0.4],
                              ["c", None, "2019-06-01", 0.3],
                              ["d", 3, "2020-04-05", -np.nan]],
                             columns=["str", "int", "date", "float"]).sort_index(axis=1)
    tmp = 'snb_taxi.bm_test_write_read'
    greenplum.remove(tmp)
    greenplum.write_table(tmp, sample_df)
    read_df = greenplum.load_result(tmp)
    pd.testing.assert_frame_equal(sample_df.set_index('date').sort_index(),
                                  read_df.set_index('date').sort_index())
    greenplum.remove(tmp, with_truncate=True)
    assert greenplum.check_table_exists(tmp)
    df = greenplum.load_result(tmp)
    assert df.empty
    greenplum.remove(tmp)
    assert not greenplum.check_table_exists(tmp)


@pytest.mark.greenplum
def greenplum_write_columns_order_tests():
    sample_df = pd.DataFrame([["a", 3],
                              ["v", 4],
                              ["d", 100500],
                              ["y", -10]],
                             columns=["name", "value"])

    tmp = 'snb_taxi.bm_test_columns_order'
    greenplum.remove(tmp)
    greenplum.write(sample_df[["name", "value"]], tmp)
    # # проверяем, что невыровненные колонки не зальются
    # with pytest.raises(psycopg2.errors.InvalidTextRepresentation):
    #     greenplum.write(sample_df[["value", "name"]], tmp, if_exists="append", columns_order=None)
    # проверяем auto выравнивание
    greenplum.write(sample_df[["value", "name"]], tmp, if_exists="append", columns_order='auto')
    # проверяем явное выравнивание
    greenplum.write(sample_df[["value", "name"]], tmp, if_exists="append", columns_order=["name", "value"])
    # проверяем auto выравнивание на пустой таблице
    greenplum.write(sample_df[["value", "name"]], tmp, with_truncate=True, columns_order='auto')
    # проверяем корректность
    df = greenplum.read(tmp)

    def compare(df, other):
        # чтение может поменять исходный порядок строчек
        sorting = df.columns.values.tolist()
        pd.testing.assert_frame_equal(df.sort_values(sorting).reset_index(drop=True),
                                      other.sort_values(sorting).reset_index(drop=True))

    compare(sample_df, df)
    # проверяем работу auto в отсутствии таблицы
    greenplum.remove(tmp)
    greenplum.write(sample_df[["value", "name"]], tmp, with_truncate=True, columns_order='auto')
    df = greenplum.read(tmp)
    compare(sample_df[["value", "name"]], df)
    greenplum.remove(tmp)


@pytest.mark.parametrize(
    "database, base_path, table_name, decode_result",
    [
        ['HahnDataLoader', "//tmp/{}/databases_tests".format(USER), "bm_test", True],
        ['GreenplumManager', "snb_taxi", 'bm_test_base_{}'.format(USER), False],
        ['GoogleDocs', "1x7N_XICco3iXP_WA0JZrOog_fVbCNprIEexBi3QTAVk", 'test', False]
    ]
)
@pytest.mark.greenplum
def databases_tests(database, base_path, table_name, decode_result):
    data = pd.DataFrame({
        'str_field': ['a', 'b', 'c', 'd', 'e', u'привет-привет', u'а вот так?'],
        'int': [1, 2, 3, 4, 5, 6, 7],
        'some_other': [2, 21, 32, 35, 106, 100500, -9]
    })[['str_field', 'int', 'some_other']]  # задаем порядок колонок явно для gdocs
    data['int'] = data['int'].astype(float)
    data['some_other'] = data['some_other'].astype(float)

    db = Factory.get(Database, database, base_path=base_path)
    reindex = lambda df: df.sort_values('int').reset_index(drop=True)

    def test(golden_df):
        written = db.read(table_name)
        if decode_result:
            written = change_coding(written)
        if database == 'GoogleDocs':
            written['int'] = written['int'].apply(lambda x: float(x) if x else np.nan)
            written['some_other'] = written['some_other'].apply(lambda x: float(x) if x else np.nan)

        pd.testing.assert_frame_equal(reindex(golden_df), reindex(written), check_like=True)

    db.remove(table_name)
    # записали и считали
    db.write(data, table_name, if_exists='replace')
    test(data)

    # дописываем туда же
    kwg = {}
    if database == 'GoogleDocs':
        kwg = dict(columns=False)  # чтобы GoogleDocs не записывал еще раз колонки
    db.write(data, table_name, if_exists='append', **kwg)
    golden = data.append(data, ignore_index=True)
    test(golden)

    # дописываем туда же, но частично те же данные
    with Handler():
        db.write(data[['str_field', 'int']], table_name,
                 if_exists='append', **kwg)
        golden = golden.append(data[['str_field', 'int']], ignore_index=True)
    test(golden)

    # проверяем replace
    db.write(data, table_name, if_exists='replace')
    test(data)

    # удаляем
    db.remove(table_name)


@pytest.mark.parametrize(
    "database, base_path",
    [
        ['HahnDataLoader', "//home/taxi-analytics/bm_test"],
        ['GreenplumManager', "snb_taxi"],
        ['GoogleDocs', "1x7N_XICco3iXP_WA0JZrOog_fVbCNprIEexBi3QTAVk"]
    ]
)
@pytest.mark.greenplum
def databases_properties_tests(database, base_path):
    db = Factory.get(Database, database, base_path=base_path)
    db.base_path
    db.base_path = base_path

    token = db.token
    db.token = token

    db.authorized


def gdocs_get_all_sheet_titles_tests():
    sheets = ['test', 'read_test', u'Лист3']
    readed_sheets = gdocs.get_all_sheet_titles("1x7N_XICco3iXP_WA0JZrOog_fVbCNprIEexBi3QTAVk")
    # на случай распараллеливания с тестом gdocs_add_table_with_create_tests
    readed_sheets = [x for x in readed_sheets if x not in ['MyTable! With WOW', 'MyOtherTable! With WOW', 'Мега Шит', u'Мега Шит']]
    assert readed_sheets == sheets


@pytest.mark.parametrize(
    "table_name, golden",
    [
       ["Sheet", "Sheet"],
       ["Sheet!A", "Sheet"],
       ["Sheet!AA", "Sheet"],
       ["Sheet!A1", "Sheet"],
       ["Sheet!a1", "Sheet"],
       ["Sheet!a73524", "Sheet"],
       ["Sheet!A12:B", "Sheet"],
       ["Sheet!A12:B30", "Sheet"],
       ["Sheet! MySheet", "Sheet! MySheet"],
       ["Sheet! MySheet!A435:C", "Sheet! MySheet"],
       ["TypoSheet!:A46", "TypoSheet!:A46"],
       ["TypoSheet!46Abc", "TypoSheet!46Abc"],
       ["TypoSheet!4", "TypoSheet!4"],
       ["СуперСписок!F4", u"СуперСписок"]
    ]
)
def gdocs_get_table_name_tests(table_name, golden):
    assert gdocs.get_table_name(table_name) == golden


@pytest.mark.parametrize(
    "table_name",
    [
       'MyTable! With WOW',
       'MyOtherTable! With WOW!A1',
       'Мега Шит'
    ]
)
def gdocs_add_table_with_create_tests(table_name):
    """Тест на правильную работу с обращениями к ячейкам"""
    sheet_id = '1x7N_XICco3iXP_WA0JZrOog_fVbCNprIEexBi3QTAVk'
    data = pd.DataFrame({'col': ['a', 'b', 'c']})
    assert not gdocs.contains(table_name, sheet_id=sheet_id)

    gdocs.write(data, table_name, sheet_id=sheet_id)  # тест проверки существования листа
    assert gdocs.contains(table_name, sheet_id=sheet_id)
    gdocs.write(data, table_name, sheet_id=sheet_id)
    data.columns = ['col1']

    table_name = gdocs.get_table_name(table_name)  # должен был пропасть A1
    gdocs.write(data, table_name + '!B1',  # тест на парсинг !
                force_drop=False, sheet_id=sheet_id)
    written_data = gdocs.read(table_name, sheet_id=sheet_id)
    assert (written_data.columns == ['col', 'col1']).all()
    for col in written_data.columns:
        assert (written_data[col] == data['col1']).all(), col
    gdocs.delete_table(table_name, sheet_id=sheet_id)
    assert not gdocs.contains(table_name, sheet_id=sheet_id)


@pytest.mark.parametrize(
    "base_path, yt_path",
    [
        ["home/taxi-analytics/business_models/{}",
            "//home/taxi-analytics/business_models/capacity/population_by_devices"],
        ["home/taxi-analytics/business_models/{}",
            "home/taxi-analytics/business_models/capacity/population_by_devices"],
        ["", "//home/taxi-analytics/business_models/capacity/population_by_devices"],
        ["", "home/taxi-analytics/business_models/capacity/population_by_devices"],
    ]
)
@pytest.mark.greenplum
def replicate_path_tests(base_path, yt_path):
    gp_path = generate_random_string('snb_taxi.bm_tests_replicate', int_suffix=True)
    hahn.base_path = base_path
    def restore_base_path(): hahn.base_path = ''
    with Handler(finally_call=restore_base_path):
        greenplum.replicate(yt_path=yt_path,
                            table_name=gp_path,
                            with_truncate=False)
    greenplum.remove(gp_path)

@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {'dtype': {'population': String}}
    ]
)
@pytest.mark.greenplum
def replicate_dtype_tests(kwargs):
    gp_path = generate_random_string('snb_taxi.bm_tests_replicate', int_suffix=True)
    greenplum.replicate(yt_path="//home/taxi-analytics/business_models/capacity/population_by_devices",
                        table_name=gp_path, **kwargs)
    greenplum.remove(gp_path)
