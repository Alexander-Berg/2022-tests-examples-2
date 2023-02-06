# coding: utf-8
from __future__ import print_function

import copy
import os
import random
from datetime import datetime

import pandas as pd
import pytest

from business_models.databases.hahn import hahn
from business_models.queries import runner, Reader, queries_config, get_current_prefix, set_yt_path,reader
from business_models.queries.queries_config import QueriesConfig
from business_models.util import deep_compare, data_from_file, change_coding, change_index, shift_date, to_start
from business_models.util import left_first_join, Handler
from .common import check_df
from .common import get_filename, read_data, make_path, write_data


def queries_config_prefix_tests():
    for database in ['yt', 'greenplum']:
        old_prefix = queries_config.get_prefix(database=database)
        new_prefix = 'some/new/base/path'
        queries_config.set_prefix(new_prefix, database=database)
        assert queries_config.get_prefix(database=database) == new_prefix, \
            'queries_config: Prefix was not correctly set for database {}'.format(database)

        assert queries_config.is_prefix_changed(database=database), \
            'queries_config: Prefix was changed, but is_prefix_changed returned False'

        if database == 'yt':
            assert get_current_prefix() == new_prefix, \
                'queries_config: Prefix was not correctly set for method ' \
                'get_current_prefix in DB {}'.format(database)
            set_yt_path(old_prefix)
        else:
            queries_config.set_prefix(old_prefix, database=database)
        assert queries_config.get_prefix(database=database) == old_prefix, \
            'queries_config: Prefix was not correctly revert for database {}'.format(database)

        assert not queries_config.is_prefix_changed(database=database), \
            'queries_config: Prefix was not changed, but is_prefix_changed returned True'


# ------- Тесты QueriesConfig -------
CONFIG_PATH = get_filename('test_config.json', __file__)
SCRIPT_PATH = get_filename('yql_src', __file__)


def get_database_path_yt_args():
    tables = {
        'info': u'home/taxi-analytics/business_models/main_query/week/info',
        'hierarchy': u'home/taxi-analytics/business_models/main_query/hierarchy',
        'dm_order': u'home/taxi-dwh/summary/dm_order'
    }
    sub_path = 'foo'
    sub_tables = {
        'info': u'home/taxi-analytics/business_models/main_query/foo/week/info',
        'hierarchy': u'home/taxi-analytics/business_models/main_query/foo/hierarchy',
        'dm_order': u'home/taxi-dwh/summary/dm_order'
    }

    for query_name in ['main_query', None, 'other_query']:
        for table_dict, sp in zip([tables, sub_tables], ['', sub_path]):
            yield query_name, 'info', table_dict['info'], sp, 'week'
            for table_name in ['hierarchy', 'dm_order']:
                for scale in ['', 'week', 'month']:
                    yield query_name, table_name, table_dict[table_name], sp, scale


def get_scripts_args():
    queries = {
        "empty": ["script"],
        "main_query": ["hierarchy", "aaaaa", "info"],
        "other_query": ["some_script"]
    }
    not_scale_free = {
        "empty": ["script"],
        "main_query": ["info"],
        "other_query": ["some_script"]
    }
    scale_free = {
        "empty": [],
        "main_query": ["hierarchy", "aaaaa"],
        "other_query": []
    }
    for tables, scale_free, only_scale_free in zip([queries, not_scale_free, scale_free],
                                                   [True, False, True],
                                                   [False, True, True]):
        for query in tables:
            yield query, scale_free, only_scale_free, tables[query]


def get_script_golden_parameters():
    common = {"common_mutable": 123, "common_parameter": False, "common_table": "home/taxi-dwh/summary/dm_order",
              "common_list": ["value", "another_value"], "common_str_list": ["str_val", "another_str"],
              "format_parameter": "{common_parameter} for {common_table}", "list_parameters": ["common_list"],
              "list_str_parameters": ["common_str_list"], "formatting_parameters": ["format_parameter"],
              "value_dependent_parameters": {}, "start_part": "start_part.yql"
              }
    main_query = copy.deepcopy(common)
    main_query.update({"mutable": "bbb", "some_parameter": True, "table_parameter": "@dwh_hierarchy",
                       "list_parameters": ["metrics", "common_list"], "some_name": "other_name",
                       "value_dependent_parameters": {"some_name": {"name": {"metrics": ["a", "b", "c"]},
                                                                    "other_name": {"metrics": ["a", "a", "a"]}}}

                       })
    hierarchy = copy.deepcopy(main_query)
    hierarchy.update({"some_name": "name", "unique_value": "unique", "unique_value_list": ["unique"],
                      "list_parameters": ["unique_value_list", "metrics", "common_list", "list_metrics"],
                      "value_dependent_parameters": {"some_name": {"name": {"metrics": ["a", "b", "c"]},
                                                                   "other_name": {"metrics": ["a", "a", "a"]}},
                                                     "unique_value": {"unique": {"list_metrics": ["cc", "bb"],
                                                                                 "my_table": {"week": "@dm_order",
                                                                                              "month": "@hierarchy"}},
                                                                      "non_unique": {"list_metrics": ["ff", "ss"]}}}
                      })
    info = copy.deepcopy(main_query)
    info.update({"some_name": "other_name"})
    other_query = copy.deepcopy(common)
    other_query.update({"table": "@my_info"})
    return {"common": common, "hierarchy": hierarchy, "info": info, "main_query": main_query,
            "other_query": other_query}


def get_script_raw_parameters_args():
    golden = get_script_golden_parameters()
    script_parameters = {
        ("empty", "script"): golden['common'],
        ("main_query", "hierarchy"): golden['hierarchy'],
        ("main_query", "info"): golden['info'],
        ("main_query", "aaaaa"): golden['main_query'],
        ("other_query", "some_script"): golden['other_query']
    }
    for query_name, script in script_parameters:
        yield query_name, script, script_parameters[(query_name, script)]


def get_script_parameters_args():
    # Проверяем что итоговые параметры правильно собираются
    common = {"common_mutable": 123, "common_parameter": False, "common_table": "home/taxi-dwh/summary/dm_order",
              "common_list": "value, another_value", "common_str_list": '"str_val", "another_str"',
              "format_parameter": "False for home/taxi-dwh/summary/dm_order",
              "sub_path": '', "scale": 'week', "prefix": "home/taxi-analytics/business_models",
              "dm_order": "home/taxi-dwh/summary/dm_order", "start_part": "start_part.yql"}
    main_query = copy.deepcopy(common)
    main_query.update({"mutable": "bbb", "some_parameter": True,
                       "table_parameter": "home/taxi-dwh/dds/v_dim_full_geo_hierarchy/v_dim_full_geo_hierarchy",
                       "info": "home/taxi-analytics/business_models/main_query/week/info",
                       "hierarchy": "home/taxi-analytics/business_models/main_query/hierarchy",
                       "dm_order": "home/taxi-dwh/summary/dm_order",
                       "dwh_hierarchy": "home/taxi-dwh/dds/v_dim_full_geo_hierarchy/v_dim_full_geo_hierarchy",
                       "metrics": "a, a, a", "some_name": "other_name"
                       })
    hierarchy = copy.deepcopy(main_query)
    hierarchy.update({"some_name": "name", "unique_value": "unique", "metrics": "a, b, c",
                      "unique_value_list": "unique", "list_metrics": "cc, bb",
                      "my_table": "home/taxi-dwh/summary/dm_order"})
    info = copy.deepcopy(main_query)
    info.update({"some_name": "other_name", "metrics": "a, a, a"})
    other_query = copy.deepcopy(common)
    other_query.update({"info": "home/taxi-analytics/business_models/main_query/week/info",
                        "my_info": "home/taxi-analytics/business_models/main_query/week/info",
                        "hierarchy": "home/taxi-analytics/business_models/main_query/hierarchy",
                        "dm_order": "home/taxi-dwh/summary/dm_order",
                        "table": "home/taxi-analytics/business_models/main_query/week/info",
                        "other_related": "home/taxi-analytics/business_models/other_query/week/info"
                        })

    script_parameters = {
        ("empty", "script"): common,
        ("main_query", "hierarchy"): hierarchy,
        ("main_query", "info"): info,
        ("main_query", "aaaaa"): main_query,
        ("other_query", "some_script"): other_query
    }
    for query_name, script in script_parameters:
        yield query_name, script, script_parameters[(query_name, script)]


def run_script_args():
    my_info = "home/taxi-analytics/business_models/main_query/week/info"
    return [[pd.DataFrame([123], columns=['value']),
             {'script': 'script', 'query_name': 'empty', 'has_start': False}],
            [pd.DataFrame([[123, my_info]], columns=['value', 'my_info']),
             {'script': 'some_script', 'query_name': 'other_query', 'has_start': True,
              'parameters': {'scale': 'week'}}],
            [pd.DataFrame([[321, 'my_info']], columns=['value', 'my_info']),
             {'script': 'some_script', 'query_name': 'other_query', 'has_start': True,
              'parameters': {'scale': 'week', 'common_mutable': 321, 'sub_path': 'some_path',
                             'my_info': 'my_info'}}],
            [pd.DataFrame([[1, 123]], columns=['value', 'common_gp']),
             {'script': 'script', 'query_name': 'gp_query', 'has_start': False,
              'parameters': {'scale': 'week'}}],
            [pd.DataFrame([[1, 900]], columns=['value', 'common_gp']),
             {'script': 'script', 'query_name': 'gp_query', 'has_start': False,
              'parameters': {'scale': 'week', 'common_parameter': 900, 'sub_path': 'aaa'}}]]


class TestsQueriesConfig(object):
    config = QueriesConfig(CONFIG_PATH, SCRIPT_PATH)
    hierarchy = get_script_golden_parameters()['hierarchy']

    def get_empty_query_settings_tests(self):
        empty_parameters = self.config.get_query_settings('empty')
        golden = {u'scripts': {u'script': u'my_best_script.yql'}}
        assert golden == empty_parameters

    def get_database_path_info_no_scale_tests(self):
        with pytest.raises(ValueError):
            self.config.get_database_path('info', 'main_query')

    def get_database_path_info_hour_tests(self):
        with pytest.raises(ValueError):
            self.config.get_database_path('info', 'main_query', scale='hour')

    @pytest.mark.parametrize(
        "query_name, table_name, table_path, sub_path, scale",
        list(get_database_path_yt_args()))
    def get_database_path_yt_tests(self, query_name, table_name, table_path, sub_path, scale):
        # Корректность построения путей таблиц на YT
        assert table_path == self.config.get_database_path(table_name, query_name, scale, sub_path)

    @pytest.mark.parametrize(
        "golden, kwargs",
        [['snb_taxi.business_models_gp_query_week_my_great_table', {'query_name': 'gp_query'}],
         ['snb_taxi.business_models_gp_query_week_my_great_table', {}],
         ['snb_taxi.business_models_gp_query_subpath_week_my_great_table', {'sub_path': 'subpath'}]])
    def get_database_path_gp_tests(self, golden, kwargs):
        # Корректность построения путей таблиц на GP
        assert golden == self.config.get_database_path('my_great_table', scale='week',
                                                       database='greenplum', **kwargs), \
            "FAILED get_database_path('my_great_table', scale='week', database='greenplum', **{})".format(kwargs)

    @pytest.mark.parametrize(
        "query, tables",
        [["empty", {"dm_order": "home/taxi-dwh/summary/dm_order"}],
         ["main_query", {"info": "home/taxi-analytics/business_models/main_query/week/info",
                         "dm_order": "home/taxi-dwh/summary/dm_order",
                         "dwh_hierarchy": "home/taxi-dwh/dds/v_dim_full_geo_hierarchy/v_dim_full_geo_hierarchy",
                         "hierarchy": "home/taxi-analytics/business_models/main_query/hierarchy"}],
         ["other_query", {"info": "home/taxi-analytics/business_models/main_query/week/info",
                          "my_info": "home/taxi-analytics/business_models/main_query/week/info",
                          "dm_order": "home/taxi-dwh/summary/dm_order",
                          "hierarchy": "home/taxi-analytics/business_models/main_query/hierarchy",
                          "other_related": "home/taxi-analytics/business_models/other_query/week/info"}]]
    )
    def get_tables_tests(self, query, tables):
        # Корректность получения таблиц для скрипта
        deep_compare(self.config.get_tables(scale='week', queries=query, config_paths=True), tables,
                     message='Test test_queries_config FAILED: for method '
                             'get_tables(scale="week", queries="{}", config_paths=True)'.format(query))

    def get_script_file_name_tests(self):
        assert 'aaa.yql' == self.config.get_script_file_name('aaaaa', 'main_query')

    @pytest.mark.parametrize(
        "query, scale_free, only_scale_free, golden",
        list(get_scripts_args())
    )
    def get_scripts_tests(self, query, scale_free, only_scale_free, golden):
        result = self.config.get_scripts(query, only_names=True, scale_free=scale_free,
                                         only_scale_free=only_scale_free)
        assert sorted(golden) == sorted(result), \
            'Test test_queries_config FAILED: get_scripts("%s", scale_free=%s, only_scale_free=%s) ' \
            'wrong values' % (query, scale_free, only_scale_free)
        assert golden == result, \
            'Test test_queries_config FAILED: get_scripts(%s, %s, %s) ' \
            'wrong order' % (query, scale_free, only_scale_free)

    @pytest.mark.parametrize(
        "query_name, script, golden",
        list(get_script_raw_parameters_args())
    )
    def get_script_raw_parameters_tests(self, query_name, script, golden):
        deep_compare(self.config.get_script_raw_parameters(script, query_name), golden,
                     message='Test test_queries_config FAILED: for method '
                             'get_script_raw_parameters("{}", "{}")'.format(script, query_name))

    def check_sub_path_error_tests(self):
        with pytest.raises(AttributeError):
            self.config._validate_sub_path('', self.hierarchy, {'some_name': 'new_name'})

    def check_sub_path_changed_sub_path_tests(self):
        # Тесты на валидность защиты от изменений параметроов
        # Есть sub_path
        self.config._validate_sub_path('some', self.hierarchy, {'some_name': 'new_name'})

    def check_sub_path_changed_prefix_tests(self):
        # Заменили префикс
        old_prefix = self.config.get_prefix('yt')
        self.config.set_prefix(old_prefix + 'some_new', database='yt')
        self.config._validate_sub_path('', self.hierarchy, {'some_name': 'new_name'})
        self.config.set_prefix(old_prefix, database='yt')

    def check_sub_path_validation_mode_tests(self):
        # Включен validation_mode
        self.config._validate_sub_path('', self.hierarchy, {'some_name': 'new_name'},
                                       validation_mode=True)

    def check_sub_path_equal_changes_tests(self):
        # В кваргах меняется все на значение из конфига (что не ошибка)
        self.config._validate_sub_path('', self.hierarchy, {'some_name': 'name'})

    def check_sub_path_global_mutable_tests(self):
        # Изменение глобальной mutable переменной
        self.config._validate_sub_path('', self.hierarchy, {'common_mutable': 's'})

    def check_sub_path_local_mutable_tests(self):
        # Изменение локальной mutable переменной
        self.config._validate_sub_path('', self.hierarchy, {'mutable': 's'})

    def check_sub_path_not_config_param_tests(self):
        # Изменение переменной, отсутствующей в конфиге
        self.config._validate_sub_path('', self.hierarchy, {'not_exists': 's'})

    @pytest.mark.parametrize(
        "query_name, script, golden",
        list(get_script_parameters_args())
    )
    def get_script_parameters_tests(self, query_name, script, golden):
        # Проверяем что итоговые параметры правильно собираются
        deep_compare(self.config.get_script_parameters(script, query_name, scale='week'), golden,
                     message='Test test_queries_config FAILED: for method '
                             'get_script_parameters("{}", "{}")'.format(script, query_name))

    def read_script_tests(self):
        assert self.config.read_script('script', 'empty') == "SELECT {common_mutable} as value -- MY BEST SCRIPT", \
            "read_script('script', 'empty')"

    @pytest.mark.parametrize(
        "golden, kwargs",
        run_script_args()
    )
    @pytest.mark.greenplum
    def run_script_tests(self, golden, kwargs):
        pd.testing.assert_frame_equal(self.config.run_script(**kwargs), golden)

    @pytest.mark.parametrize(
        "golden, kwargs",
        [['full_main_query.yql', {'scripts': None}],
         ['two_scripts_of_main.yql', {'scripts': ['hierarchy', 'aaaaa'],
                                      'mutable': 'new_mutable'}]]
    )
    def get_query_tests(self, golden, kwargs):
        golden_text = read_data(__file__, golden)
        assert self.config._get_query('main_query', scale='week',
                                      has_start=True, **kwargs) == golden_text, \
            '_get_query("main_query", scale="week", has_start="True", **{}) ' \
            'FAILED'.format(kwargs)


def reader_tests(tmpdir):
    cache_directory = os.path.join(str(tmpdir), 'cache')
    reader = Reader(config=queries_config, cache_directory=cache_directory)
    info_path = queries_config.get_database_path('info', scale='month')
    info_by_path = reader.read_table_by_path(info_path, cache=True, hard_cache=True)

    # проверяем кэши
    cache = reader.get_cache()
    info_cache_name = reader._get_name(info_path)
    golden = {'cache': [info_cache_name], 'hard_cache': [info_cache_name],
              'hard_cache_old': []}
    deep_compare(cache, golden, message='Cache was not set')

    reader.clear_cache()
    cache = reader.get_cache()
    golden = {'cache': [], 'hard_cache': [info_cache_name], 'hard_cache_old': []}
    deep_compare(cache, golden, message='Cache was not cleared')

    reader.clear_cache(hard=True)
    cache = reader.get_cache()
    golden = {'cache': [], 'hard_cache': [], 'hard_cache_old': []}
    deep_compare(cache, golden, message='Cache was not cleared with hard=True')

    reader.clear_cache(hard=True)
    cache = reader.get_cache()
    golden = {'cache': [], 'hard_cache': [], 'hard_cache_old': []}
    deep_compare(cache, golden, message='Clear empty cache error.')

    info_by_name = reader.read_table('info', scale='month')
    # проверка что кэш не появился
    cache = reader.get_cache()
    golden = {'cache': [], 'hard_cache': [], 'hard_cache_old': []}
    deep_compare(cache, golden, message='Cache saved without need')

    pd.testing.assert_frame_equal(info_by_path, info_by_name)

    # тест запуска
    for table in ['fact_data', 'forecast_data', 'plan_data']:
        try:
            reader.read_versions(table, run_kwargs={'validation_mode': True})
        except ValueError:
            pass


@pytest.mark.parametrize(
    "database,tmp_table",
    [
        ["yt", "//tmp/bm_read_parameter_tests"],
        ["greenplum", "snb_taxi.bm_read_parameter_tests"]
    ]
)
@pytest.mark.greenplum
def read_parameter_tests(database, tmp_table):

    conf = read_data(__file__, 'read_parameter_tests.json')
    test_df = read_data(__file__, conf["input"])
    reader = Reader()
    db = queries_config.get_database(database)
    db.remove(tmp_table)
    t = test_df.copy()
    if database == 'yt':
        t['version'] = t['version'].astype('float')
    db.write(dataframe=t, table_name=tmp_table)
    with Handler(raise_exceptions=True, finally_call=lambda: db.remove(tmp_table)):
        for test in conf['configurations']:
            result = reader.read_parameter(table_name=tmp_table, database=database, **change_coding(test['params'],
                                                                                                  to_unicode=False))
            golden = read_data(__file__, test['golden'])
            pd.testing.assert_frame_equal(result, golden, obj='Database {} with params {}'.format(database, test['params']))


# неактуально пока прогнозы не работают
# @pytest.mark.greenplum
# @pytest.mark.parametrize(
#     "database,scale, from_date,periods_from_today,filter_scale",
#     [
#         ["yt", 'week', '2020-01-01', None, None],
#         ["yt", 'week', None, 5, None],
#         ["yt", 'week', None, 5, 'month'],
#         ["yt", 'month', '2020-01-01', None, None],
#         ["yt", 'month', None, 5, None],
#         ["yt", 'month', None, 5, 'month'],
#         ["greenplum", 'week', '2020-01-01', None, None],
#         ["greenplum", 'week', None, 5, None],
#         ["greenplum", 'week', None, 5, 'month'],
#         ["greenplum", 'month', '2020-01-01', None, None],
#         ["greenplum", 'month', None, 5, None],
#         ["greenplum", 'month', None, 5, 'month']
#     ]
# )
# def read_parameter_n_periods_tests(database, scale, from_date, periods_from_today, filter_scale):
#     reader = Reader()
#     src_table = 'fact_data'
#     if database == 'greenplum':
#         src_table = 'dwh_fact_data'
#     result_data = reader.read_parameter('supply', src_table, database=database, scale=scale, from_date=from_date,
#                                         periods_from_today=periods_from_today,
#                                         filter_scale=filter_scale)
#     compare_filter_scale = filter_scale or scale
#     start_date = pd.to_datetime(from_date)
#     if start_date is None:
#         start_date = to_start(shift_date(datetime.today(), -periods_from_today, compare_filter_scale),
#                               compare_filter_scale)
#     if start_date != to_start(start_date, scale):
#         start_date = shift_date(to_start(start_date, scale), 1, scale)
#     assert result_data[scale].min() == start_date


def run_yql_tests():
    runner.run_yql('select 1')


@pytest.mark.greenplum
def greenplum_patch_tests():
    main = 'snb_taxi.bm_test_main'
    patch = 'snb_taxi.bm_test_patch'
    gp = queries_config.get_database('greenplum')
    index_cols = ['id', 'name']
    df = pd.DataFrame([['1', 'a', 2.], ['2', 'a', 4.], ['3', 'b', 6.]], columns=['id', 'name', 'val'])
    gp.write(df, patch, if_exists='replace')
    runner.update_table_gp(table=main, patch=patch, index=index_cols)
    check_df(df, gp.read(main), index=index_cols, check_like=True)
    df_patch = pd.DataFrame([['15', 'c', 2.], ['2', 'a', 9.], ['3', 'a', 0.]], columns=['id', 'name', 'val'])
    gp.write(df_patch, patch, if_exists='replace')
    runner.update_table_gp(table=main, patch=patch, index=index_cols)
    result = gp.read(main)
    gp.remove(main)
    gp.remove(patch)
    check_df(left_first_join(df_patch, df, left_on=index_cols), result, index=index_cols, check_like=True)


# def simple_cohorts_tests():
#     df = pd.DataFrame({
#         'city': ['Москва', 'Москва', 'Москва', 'Москва', 'Москва', 'Москва', ],
#         'tariff_zone': [None, None, None, None, None, None, ],
#         'user_phone': ['a', 'a', 'a', 'a', 'a', 'a', ],
#         'utc_date': ['2018-03-04 00:00:00', '2018-03-10 00:00:00', '2018-04-04 00:00:00', '2018-04-06 00:00:00',
#                      '2018-04-08 00:00:00', '2018-05-01 00:00:00', ],
#         'app': ['mac', 'mac', 'mac', 'snedi', 'snedi', 'snedi'],
#         'order_id': ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
#     })
#     tmp_table = os.path.join("//tmp", 'simple_cohorts_test' + str(random.random()))
#
#     hahn.write(df, tmp_table)
#
#     test_tariff_cohorts_table = os.path.join("//tmp", 'test_tariff_cohorts_table' + str(random.random()))
#     test_tariff_cohorts_nf_table = os.path.join("//tmp", 'test_tariff_cohorts_nf_table' + str(random.random()))
#     # Как назвать таблицу для сохранения?
#     cohort_path = {
#         False: (test_tariff_cohorts_nf_table, 'test_tariff_cohorts_nf'),
#         True: (test_tariff_cohorts_table, 'test_tariff_cohorts')
#     }
#
#     # задаем параметры запроса
#     # основная таблица с данными
#     main_table_query = """
#     SELECT
#         *
#     FROM `{}`
#     """.format(tmp_table)
#
#     # как ее надо фильтровать
#     row_filter = ""
#
#     unique = 'user_phone'  # по кому считаем когорты?
#     time_field = 'utc_date'  # какое поле отвечает за дату?
#     scale = 'month'
#     group_by_columns = ['app']
#     custom_regions = "''"  # список вершин геоиерархии, по которым надо посчитать когорты
#     # (это значит, что по базовым регионам)
#
#     # нам подходят все поездки в качестве первых, но для примера сделаем фейковую проверку
#     first_ride_checker = "() -> {RETURN TRUE;}"
#     first_ride_parameters = []
#
#     # Теперь про расчет необходимых метрик
#     metrics = ["order_id"]
#
#     grouped_metrics = [
#         "COUNT(DISTINCT {unique}) AS users",
#         "COUNT(order_id) AS orders"
#     ]
#
#     # Запуск расчета
#     for use_first_city in cohort_path:
#         runner.run_simple_cohorts(
#             main_table_query=main_table_query,
#             row_filter=row_filter,
#             unique=unique,
#             time_field=time_field,
#             scale=scale,
#             group_by_columns=group_by_columns,
#             first_ride_checker=first_ride_checker,
#             first_ride_parameters=first_ride_parameters,
#             metrics=metrics,
#             grouped_metrics=grouped_metrics,
#             cohort_path=cohort_path[use_first_city][0],
#             custom_regions=custom_regions,
#             use_first_city=use_first_city
#         )
#     # Сверка
#     for use_first_city in cohort_path:
#         golden_data_path = make_path("%s.pkl" % cohort_path[use_first_city][1])
#         golden_data = data_from_file(golden_data_path, determine_type=True)
#         table = hahn.load_result(full_path=cohort_path[use_first_city][0])
#         pd.testing.assert_frame_equal(change_index(change_coding(golden_data), ['city', 'cohort_date', 'month']),
#                                       change_index(change_coding(table), ['city', 'cohort_date', 'month']),
#                                       check_like=True)



# @pytest.mark.greenplum
# @pytest.mark.parametrize(
#     "source_table, by_geo_node_flg, cohort_flg, source_geo_column, source_dttm_column, source_columns, filter, periods_from_today",
#     [
#         ["demand_week_poly_cohorts", True, True, None, None,
#          ['demand_session_cnt', 'trip_cnt', 'unit_active_life_period_cnt'],
#          None, None],
#         ["demand_session_lcl_hourly", False, False, None, None,
#          ['demand_session_cnt'], None, None],
#         ["agg_management_reporting", True, False, 'geo_node_id', 'moscow_order_dttm',
#          ['completion_rate', 'gmv_trips_rub', 'trips_cnt'],
#          "scale_name='weekly' and moscow_order_dttm < date_trunc('week', now())", None],
#         ["demand_week_poly_cohorts", True, True, None, None,
#          ['demand_session_cnt', 'trip_cnt', 'unit_active_life_period_cnt'],
#          None, 52],
#         ["demand_session_lcl_hourly", False, False, None, None,
#          ['demand_session_cnt'], None, 1],
#         ["agg_management_reporting", True, False, 'geo_node_id', 'moscow_order_dttm',
#          ['completion_rate', 'gmv_trips_rub', 'trips_cnt'],
#          "scale_name='weekly' and moscow_order_dttm < date_trunc('week', now())", 52],
#     ]
# )
# def read_dwh_object_tests(source_table, by_geo_node_flg, cohort_flg, source_geo_column, source_dttm_column,
#                           source_columns, filter, periods_from_today):
#     reader.read_dwh_object(source_table=source_table, by_geo_node_flg=by_geo_node_flg,
#                            cohort_flg=cohort_flg, source_geo_column=source_geo_column,
#                            source_dttm_column=source_dttm_column, source_columns=source_columns,
#                            filter=filter, periods_from_today=periods_from_today)
#
