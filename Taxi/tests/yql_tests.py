# Неактуально пока не работают прогнозы

# # coding: utf-8
#
# import datetime
# import pandas as pd
# import pytest
#
# from business_models.queries import runner, queries_config
# from business_models.util import shift_date
#
#
# SCALES = ['month', 'week']
# BINARY = [True, False]
# FACT_FORECAST = ["fact", "forecast"]
#
# @pytest.mark.parametrize(
#     "scale, sub_path, with_scale_free, driver_sessions_incremental, hierarchy_table",
#     [['week', '', True, True, None],  # продакшен
#      ['month', '', False, True, None],  # продакшен
#      ['week', 'test_sub_path_really_empty', True, False, None],  # в пустой sub_path (порядок запросов),
#      # То же самое, но на иерархии со всеми аггломерациями
#      ['week', '', True, True, '$hierarchy_with_all_agglomerations'],
#      ['month', '', False, True, '$hierarchy_with_all_agglomerations'],
#      ['week', 'test_sub_path_really_empty', True, False, '$hierarchy_with_all_agglomerations'],
#      ]
# )
# def recount_all_tests(scale, sub_path, with_scale_free, driver_sessions_incremental, hierarchy_table):
#     runner.recount_all(with_scale_free=with_scale_free,
#                        driver_sessions_incremental=driver_sessions_incremental,
#                        sub_path=sub_path, scale=scale, hierarchy_table=hierarchy_table,
#                        hahn_kwargs={"validation_mode": True})
#
#
#
#
# @pytest.mark.parametrize(
#     "scale, sub_path, hierarchy_table",
#     [['month', '', None],  # все существующие запросы (во всех скейлах будет одно и то же)
#      ['week', 'first_city', None],  # пересчет в sub_path (first_city из прода),
#      # То же самое, но на иерархии со всеми аггломерациями
#      ['month', '', '$hierarchy_with_all_agglomerations'],
#      ['week', 'first_city', '$hierarchy_with_all_agglomerations'],
#      ]
# )
# def recount_metrics_tests(scale, sub_path, hierarchy_table):
#     runner.recount_all_metric(scale=scale,
#                               sub_path=sub_path,
#                               parallel_mode=False,  # validate быстро работает
#                               hahn_kwargs={"validation_mode": True},
#                               hierarchy_table=hierarchy_table,
#                               )
#
#
# @pytest.mark.parametrize(
#     "scale, sub_path",
#     [['month', ''],  # все существующие запросы (во всех скейлах будет одно и то же)
#      ]
# )
# def recount_capacity_tests(scale, sub_path):
#     runner.recount_all_capacity(scale=scale,
#                             sub_path=sub_path,
#                             hahn_kwargs={"validation_mode": True},
#                             folder="test_folder",
#                             crypta_mapping_path="//home/taxi-analytics/business_models/tests/crypta_mapping_sample",
#                             )
#
#
# @pytest.mark.parametrize(
#     "scale, sub_path",
#     # нужно тестировать во всех скейлах, потому что набор метрик от него зависит
#     [['hour', ''],  # часовые точки
#      ['month', ''],  # все-все метрики
#      ['week', 'first_city'],  # все-все метрики в sub_path
#      ]
# )
# def upload_all_fact_tests(scale, sub_path):
#     runner.upload_all_fact(scale=scale, sub_path=sub_path,
#                            hahn_kwargs={"validation_mode": True})
#
#
# @pytest.mark.parametrize(
#     "fact_or_forecast",
#     ['fact',
#      'forecast'
#      ]
# )
# def upload_forecast_tests(fact_or_forecast):
#     parameter = 'trips'
#     scale = 'week'
#     forecast_date = shift_date(pd.datetime.now().date(), 52, 'week')
#     fact_date = shift_date(pd.datetime.now().date(), -52, 'week')
#     fake_df = pd.DataFrame([['BR0', 'Moscow', fact_date, 100, 0.01],
#                             ['BR0', 'Moscow', forecast_date, 500, 0.01]],
#                                columns=['region_id', 'city', scale, parameter, 'confidence_interval'])
#     runner.write_forecast(fake_df, parameter, scale=scale, fact_or_forecast=fact_or_forecast,
#                           validation_mode=True)
#
#
# @pytest.mark.parametrize(
#     "table_name, validation_mode",
#     [['fact_data', True],  # просто проверяем, что таблица по формату подходит
#      ['forecast_data', True]
#      ]
# )
# def restore_last_flag_tests(table_name, validation_mode):
#     load_date_threshold = (datetime.datetime.today() - datetime.timedelta(days=3)).strftime("%Y-%m-%d")
#     runner.restore_last_flag(table_name, load_date_threshold, params="mph", scales="week", validate=True,
#                              validation_mode=validation_mode)
#
#
# @pytest.mark.parametrize(
#     "method, parameters",
#     [['run_group_cohorts', {}],  # дефолтные параметры должны работать
#      ['run_group_cohorts', {'prefix_subquery': 'select 1;'}],
#      ['run_group_cohorts', {'group_checker': '($group_from, $smth) -> {RETURN True;}',
#                             'group_parameters': '"some value"'}],
#      ['run_group_cohorts', {'first_ride_checker': '($smth) -> {RETURN True;}',
#                             'first_ride_parameters': '"some value"'}],
#      ['run_group_cohorts', {'row_filter': ''}],
#      ['run_group_cohorts', {'metrics': [], 'grouped_metrics': []}],
#
#      ['run_simple_cohorts', {}],  # дефолтные параметры должны работать
#      ['run_simple_cohorts', {'row_filter': ''}],
#      ['run_simple_cohorts', {'metrics': [], 'grouped_metrics': []}],
#      ['run_group_cohorts', {'first_ride_checker': '($smth) -> {RETURN True;}',
#                             'first_ride_parameters': '"some value"'}],
#      # То же самое, но на иерархии со всеми аггломерациями
#      ['run_group_cohorts', {'hierarchy_table': '$hierarchy_with_all_agglomerations'}],  # дефолтные параметры должны работать
#      ['run_group_cohorts', {'prefix_subquery': 'select 1;', 'hierarchy_table': '$hierarchy_with_all_agglomerations'}],
#      ['run_group_cohorts', {'group_checker': '($group_from, $smth) -> {RETURN True;}',
#                             'group_parameters': '"some value"',
#                             'hierarchy_table': '$hierarchy_with_all_agglomerations'}],
#      ['run_group_cohorts', {'first_ride_checker': '($smth) -> {RETURN True;}',
#                             'first_ride_parameters': '"some value"',
#                             'hierarchy_table': '$hierarchy_with_all_agglomerations'}],
#      ['run_group_cohorts', {'row_filter': '',
#                             'hierarchy_table': '$hierarchy_with_all_agglomerations'}],
#      ['run_group_cohorts', {'metrics': [], 'grouped_metrics': [],
#                             'hierarchy_table': '$hierarchy_with_all_agglomerations'}],
#      ['run_simple_cohorts', {'hierarchy_table': '$hierarchy_with_all_agglomerations'}],  # дефолтные параметры должны работать
#      ['run_simple_cohorts', {'row_filter': '', 'hierarchy_table': '$hierarchy_with_all_agglomerations'}],
#      ['run_simple_cohorts', {'metrics': [], 'grouped_metrics': [],
#                              'hierarchy_table': '$hierarchy_with_all_agglomerations'}],
#      ['run_group_cohorts', {'first_ride_checker': '($smth) -> {RETURN True;}',
#                             'first_ride_parameters': '"some value"',
#                             'hierarchy_table': '$hierarchy_with_all_agglomerations'}],
#      ]
# )
# def simple_cohorts_validate_tests(method, parameters):
#     # Тест падает из-за user_phone
#     return
#
#     getattr(runner, method)(hahn_kwargs={'validation_mode': True, 'syntax_version': 1},
#                             **parameters)
#
#
# @pytest.mark.parametrize(
#     "regions",
#     [
#         None,
#         ['Ашдод', 'Ололоевск']
#      ]
# )
# def runner_drop_regions_tests(regions):
#     runner.drop_unknown_regions(regions=regions, validation_mode=True)
