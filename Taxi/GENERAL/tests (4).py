# coding: utf-8

from __future__ import print_function
import warnings

import numpy as np
import pandas as pd
import os

from business_models.util import get_list, change_index, monitor_difference, change_coding, \
    test_series, data_from_file, data_to_file, test_dataframe
from .read_inputs import get_previous_plan, get_previous_file_from_ticket


def plan_trips_test(plan, trips_name='trips'):
    plan_data = change_index(plan.plan, [plan.dimension, plan.scale])
    final_trips = plan_data[trips_name]
    demand_trips = plan.get_channels('real_' + trips_name, plan.demand_keys)
    supply_trips = plan.get_channels('real_' + trips_name, plan.supply_keys)

    monitor_difference(final_trips, demand_trips, message='Demand trips not equals total trips')
    print('plan_trips_test with demand PASSED')
    monitor_difference(final_trips, supply_trips, message='Supply trips not equals total trips')
    print('plan_trips_test with supply PASSED')


def test_plan(plan, plan_settings,
              elasticity_bounds=(-10, 10),
              balance_bounds=(0.5, 20),
              gmv_bounds = (1e+05, None),
              conversion_bounds=(0.001, 0.8),
              avg_check_bounds=(30, 1100),
              surge_bounds=(0.95, 2), trips_name='trips'):
    plan_trips_test(plan, trips_name=trips_name)

    tested_cols = set()
    plan_df = plan.plan
    def test(df, colname, bounds=(None, None), **kwargs):
        extra_tests = {}
        extra_tests["small"] = lambda s: s < (bounds[0] if bounds[0] is not None else -np.inf)
        extra_tests["big"] = lambda s: s > (bounds[1] if bounds[1] is not None else np.inf)
        test_series(df[colname], keep_index=True, name=colname, extra_tests=extra_tests, **kwargs)
        tested_cols.add(colname)

    def check_heads(df, heads_col, prefix):
        full_heads_name = heads_col if not prefix else prefix + "_" + heads_col
        test(df, full_heads_name, exclude_tests='zero')
        min_col_name = 'min_' + heads_col if not prefix else prefix + "_min_" + heads_col
        max_col_name = 'max_' + heads_col if not prefix else prefix + "_max_" + heads_col
        test(df, min_col_name, exclude_tests='zero')
        test(df, max_col_name, exclude_tests='zero')
        outliers = df[(df[full_heads_name] > df[max_col_name]) |
                      (df[full_heads_name] < df[min_col_name])][[full_heads_name, min_col_name, max_col_name]]
        if not outliers.empty:
            raise ValueError('newbies out of bound for {} {}\n{}'.format(heads_col, prefix,
                                                                         change_coding(outliers, False)))

    big_cities = plan_df[plan_df['trips'] > 100000]
    for source in ['supply', 'demand']:
        for channel in plan_settings.settings[source + '_keys']:
            heads_name = plan.properties[channel].key_name
            value = plan.properties[channel].value_name
            check_heads(big_cities, heads_name, channel)
            test(big_cities, channel + '_' + value)
            test(plan_df, channel + '_trend_' + value)
            test(plan_df, channel + '_trips')
            test(plan_df, channel + '_trend_trips')
            test(plan_df, channel + '_real_trips')
            test(plan_df, value + '_trend_trips')
            if source == "supply":
                test(plan_df, channel + '_demand_trips')
        test(big_cities, source + '_elasticity', bounds=elasticity_bounds, exclude_tests=['negative', 'zero'])
        test(plan_df, source + '_trips')
        test(plan_df, value)
        test(plan_df, 'trend_' + value)
        # check_heads(plan_df, heads_name, '')  # не проверяем, потому что водители специально в коде портятся
                                                # TODO: считать сумму водителей через каннибализацию
        test(plan_df, 'trips')

    test(big_cities, 'balance', bounds=balance_bounds)
    test(big_cities, 'gmv', bounds=gmv_bounds)
    test(big_cities, 'conversion', bounds=conversion_bounds)
    test(big_cities, 'avg_check', bounds=avg_check_bounds)
    test(plan_df, 'surge', bounds=surge_bounds)

    unchecked_columns = [col for col in plan_df.columns if col not in tested_cols]
    if unchecked_columns:
        warnings.warn("Some columns in plan have no check rules {}".format(unchecked_columns))


def comapare_plans(plan, prev_plan, plan_settings, columns=('trips', 'gmv'), rtol=1e-04):
    if not isinstance(plan, pd.DataFrame):
        plan = plan.plan

    if plan_settings.scale in change_index(plan, None).columns:
        index = [plan_settings.dimension, plan_settings.scale]
    else:
        # это большой план с мультииндексом
        index = plan.index.names

    columns = columns or plan.columns
    plan = change_index(plan, index)
    prev_plan = change_index(prev_plan, index)
    for column in get_list(columns):
        monitor_difference(plan[column], prev_plan[column],
                           all_close_kwargs={"rtol": rtol})


def compare_and_report(new_df, old_df, plan_settings, columns=('trips', 'gmv')):
    diff = ""
    equal = True
    try:
        comapare_plans(new_df, old_df, plan_settings, columns=columns)
    except ValueError as e:
        diff = str(e)
        equal = False
    return "Reperformed plan status {} {}".format(equal, diff)


def test_df_with_reperform(new_df, file_path, plan_settings, from_file_kwargs=None,
                           save_path='.', check_equals=False, columns=('trips', 'gmv')):
    prev_result = get_previous_file_from_ticket(file_path, plan_settings, check_equals=check_equals)
    prev_result = data_from_file(prev_result, **(from_file_kwargs or {}))
    save_name = "Reperformed_" + file_path
    message = compare_and_report(new_df, prev_result, plan_settings, columns=columns)
    saved = data_to_file(new_df, os.path.join(save_path, save_name))
    plan_settings.send_to_ticket(files=[saved], message=message, with_clear=True)



def test_reperform(plan, plan_settings, budget_metrics):
    prev_plan_df, prev_plan_name = get_previous_plan(plan_settings)
    reperformed_plan_save_name = "Reperformed " + prev_plan_name
    message = compare_and_report(prev_plan_df, plan, plan_settings)
    plan_settings.save_plan(plan, budget_metrics, save_name=reperformed_plan_save_name)
    plan_settings.send_to_ticket(files=[reperformed_plan_save_name], message=message, with_clear=True)


def test_plan_changes(old_plan, new_plan):
    print('TEST fix_anomaly changes starts')
    # сравнение независимых логов
    evaluate_columns = list(filter(lambda x: 'evaluate' in x, new_plan.changes_in_scale.columns))
    has_changes = (new_plan.changes_in_scale[evaluate_columns] != 0).any(axis=1)

    errors = new_plan.anomaly_log['has_changes_flg'] & ~has_changes
    if len(errors[errors]) != 0:
        errors = new_plan.anomaly_log.loc[errors]
        raise ValueError('anomaly_log not equals to changes_in_scale: {}'.format(errors))

    # Сравнение changes_in_scale и реального расхождения в данных
    changes = new_plan.changes_in_scale
    prefix = 'evaluate_'
    columns = list(filter(lambda x: prefix in x, changes.columns))

    dimension = old_plan.dimension
    scale = old_plan.scale
    index = [dimension, scale]
    old_plan = change_index(old_plan.plan, index)
    new_plan = change_index(new_plan.plan, index)

    for column in columns:
        value_name = column[len(prefix):]
        monitor_difference(old_plan[value_name] + changes[column],
                           new_plan[value_name],
                           index=dimension,
                           grouper={scale: 'count', value_name: 'mean'},
                           message='Old plan + diff not equals to new plan in {}'.format(value_name))

    print('TEST fix_anomaly changes PASSED')


def validate_total_plan(plan, plan_settings, metrics, not_only_positive_metrics=None):
    """Проверяет, что в итоговом плане есть все города и значения метрик не содержат
    грубых ошибок
    :param not_only_positive_metrics: list - список метрик, которые могут становиться отрицатльными
    """
    def get_dimension_values(df):
        df = change_index(df, None)
        return df[plan_settings.dimension].unique()

    test_dataframe(plan, keep_index=True, name='total_plan', tests=['inf', 'nan'])
    non_negative = [x for x in metrics
                    if x not in get_list(not_only_positive_metrics, none_as_empty=True)]
    test_dataframe(plan[non_negative],
                   keep_index=True, name='total_plan', tests=['negative'])

    target_cities = get_dimension_values(plan_settings.business_targets_full)
    plan_cities = get_dimension_values(plan)
    plan_cities = list(filter(lambda x: x in target_cities, plan_cities))  # Фильтруем Москву с Питером

    index = [plan_settings.dimension, plan_settings.scale]
    if 'tariff' in plan:
        index.append('tariff')

    errors_ni = change_index(plan, index)[['net_inflow', 'gross_revenue', 'subsidies',
                                           'discounts', 'fee_branding_chargebacks', 'coupons']]
    errors_ni['ni_calc'] = errors_ni.eval('gross_revenue - subsidies - discounts - fee_branding_chargebacks - coupons')
    errors_ni = errors_ni[~np.isclose(errors_ni['ni_calc'], plan['net_inflow'])]
    if len(errors_ni) != 0:
        raise ValueError("Inconsistent Net Inflow in {} rows!\nAll data: {}".format(
            len(errors_ni), errors_ni[['ni_calc', 'net_inflow']]
        ))

    if len(plan_cities) != len(target_cities):
        missed = list(filter(lambda x: x not in plan_cities, target_cities))
        warnings.warn('Some cities missed in total plan: {}'.format(
            ', '.join(map(lambda x: change_coding(x, False), missed))
        ))
