# coding: utf-8

import numpy as np
import pandas as pd
import pytest
from business_models.util import change_index, get_period_list, change_coding, monitor_difference_frames,\
    to_start, shift_date, SCALES_ORDER
from business_models.convert import HierarchyConverter, ScaleConverter, Converter, BadConvertRegions
from .common import read_data, check_df, write_data

ADDITIVE_VALUES = ['trips', 'discounts', 'gmv', 'gross_revenue', 'drivers', 'users', 'subsidies', 'coupons']


@pytest.mark.greenplum
def converter_tests():
    data = pd.DataFrame({
        'city': ['msc', 'msc', 'spb', 'spb'],
        'month': pd.to_datetime(['2018-01-01', '2018-02-01', '2018-02-01', '2018-03-01']),
        'trips': [1000, 1500, 50, 60],
        'users': [300, 350, 10, 15],
        'some_value': [0, 0, 1, 1],
        'some_str': ['ru1', 'ru1', 'ru2', 'ru2']
    })
    data['activity'] = data.eval('trips / users')
    data['some_value_activity'] = data.eval('some_value / users * 100')

    value_types = {
        'additive': ['trips', 'users'],
        'non-additive': 'activity',
        'calculated': {'new_activity': 'trips / users', 'some_value_activity': 'some_value / users * 100'}
    }

    week_periods = get_period_list(from_period='2018-01-01', to_period='2018-01-29', scale='week') + \
                   get_period_list(from_period='2018-01-29', to_period='2018-02-26', scale='week')
    month_periods = ['2018-01-01'] * 5 + ['2018-02-01'] * 10 + ['2018-03-01'] * 5
    coefs = [0.16, 0.25, 0.27, 0.29, 0.03] + [0.12, 0.2, 0.23, 0.24, 0.21]
    user_coefs = [0.12, 0.27, 0.29, 0.32, 0.0] + [0.2, 0.2, 0.2, 0.2, 0.2]

    proportions = pd.DataFrame({
        'city': ['msc'] * 10 + ['spb'] * 10,
        'month': pd.to_datetime(month_periods),
        'week': week_periods + week_periods,
        'trips': coefs + coefs,
        'users': user_coefs + user_coefs,
        'some_value': np.linspace(0, 1, num=20),
        'activity': 0.2
    })
    proportions = proportions.set_index('week')

    squeeze_index = get_period_list('2018-01-01', '2018-02-26', 'week')
    squeeze_proportions = pd.DataFrame({
        'city': ['msc'] * len(squeeze_index) + ['spb'] * len(squeeze_index),
        'week': squeeze_index + squeeze_index,
        'some_value': np.linspace(0, 1, num=2 * len(squeeze_index)),
        'activity': 0.9
    })
    new_data = Converter.convert_iteration(data, value_types, proportions,
                                           index=['city', 'month'], stable_index='city',
                                           additional_index='week', squeeze_proportions=squeeze_proportions,
                                           squeeze_kwargs={'non-additive': {
                                               'agg_function': 'sum'}},
                                           with_squeeze=True)
    golden = read_data(__file__, 'converted_values.pkl')
    write_data(golden, __file__, 'converted_values.pkl')
    golden = change_index(golden, new_data.index.names).sort_index()
    new_data = new_data.sort_index()
    pd.testing.assert_frame_equal(new_data, golden, check_like=True)


@pytest.mark.greenplum
def converter_non_additive_tests():
    '''
    Проверка squeeze неаддитивных метрик
    '''
    date_range = pd.to_datetime(['2019-01-01', '2019-02-02'])
    weeks = get_period_list(from_period=date_range[0], to_period=shift_date(date_range[-1], 1, 'month'), scale='week', include_right=False)
    data = pd.DataFrame({
        'week': weeks,
        'some_value': np.linspace(0, 1, num=len(weeks)),
        'other_value': [2 ** i for i in range(len(weeks))],
        'city': ['a'] * len(weeks)
    })

    proportions = pd.DataFrame({
        'month': to_start(weeks, 'month'),
        'week': weeks,
        'city': ['a'] * len(weeks),
        'some_value': 1,
        'other_value': 1
    })
    proportions = proportions.set_index('month')

    value_types = {
        'non-additive': ['some_value', 'other_value']
    }
    new_data = Converter.convert_iteration(change_index(data, None), value_types, proportions=None,
                                           index=['city', 'week'],
                                           stable_index='city',
                                           additional_index='month',
                                           squeeze_kwargs={'non-additive': {'agg_function': {'some_value': 'max', 'other_value': 'mean'}},
                                                           'common_index': ['city', 'week'],
                                                            'additional_index': 'month'
                                                           },
                                           with_squeeze=True,
                                           with_expand=False,
                                           squeeze_index=['city', 'month'],
                                           squeeze_proportions=proportions)

    expected = pd.DataFrame({
        'month': pd.to_datetime(['2019-01-01', '2019-02-01']),
        'some_value': [0.428571, 1.],
        'other_value': [3.75, 60.0],
        'city': ['a'] * len(date_range)
    })
    index = ['city', 'month']

    pd.testing.assert_frame_equal(change_index(new_data, index), change_index(expected, index), check_like=True)


@pytest.mark.greenplum
def hierarchy_converter_tests():
    data = read_data(__file__, 'hierarchy_converter_data.pickle')
    value_types = {
        'additive': ADDITIVE_VALUES,
        'calculated': {
            'net_inflow': 'gross_revenue - subsidies - discounts - coupons',
        }
    }
    columns = value_types['additive'] + list(value_types['calculated'].keys())
    new_regions = ['op_center', 'fi_spb_region', 'fi_spb_and_spbr', 'fi_far_moscow_region',
                   'op_far_moscow_region', 'op_privolzhie']

    converter = HierarchyConverter()
    proportions = converter.get_proportions(data['region_id'].unique(),
                                            region_name='city', fact_interval='2 Week')
    proportions = proportions.groupby(['region_id', 'city']).sum()
    errors = proportions[~np.isclose(proportions[value_types['additive']], 1.0).any(axis=1)]
    if len(errors) != 0:
        raise ValueError('Some proportion sums not equals to 1.0\n{}'.format(errors))

    data_hc = converter.convert(data,
                                value_types,
                                index='month',
                                fact_interval='2 Week',
                                new_regions=new_regions,
                                region_name='city')

    data_hc = change_index(data_hc[columns], None)
    assert np.allclose(data_hc['net_inflow'], data_hc.eval("gross_revenue - subsidies - discounts - coupons")), \
        "Calculated value in HierarchyConverter not equals to calculation"
    print("HierarchyConverter test for calculated fields PASSED")

    assert len(new_regions) == data_hc[data_hc.region_id.isin(new_regions)].region_id.nunique(), \
        "Not all new_regions were added to data in HierarchyConverter"

    assert sorted(columns) == sorted(filter(lambda x: x not in ['region_id', 'city', 'month'], data_hc.columns)), \
        "Not all values were calculated by HierarchyConverter"

    data_hc_base = data_hc[~data_hc.region_id.isin(new_regions)]
    group = lambda df: df.groupby('month')[columns].sum().sort_index()
    data_hc_base, data = group(data_hc_base), group(data)
    data.columns.name = None
    pd.testing.assert_frame_equal(data_hc_base, data)  # Total sums test


@pytest.mark.greenplum
def scale_converter_tests(save_golden=False):
    data = read_data(__file__, 'scale_converter_data.pkl')
    value_types = {
        'additive': ['trips', 'gmv', 'drivers'],
        'non-additive': ['active_drivers'],
        'calculated': {
            'avg_check': 'gmv / trips',
        }
    }
    seasonality_values = {
        'trips_cnt': ['trips']
    }
    kwargs = dict(data=data, value_types=value_types, scale='month',
                  to_scale='week', index='city',
                  seasonality_values=seasonality_values,
                  squeeze_kwargs={'non-additive': {
                      'agg_function': 'sum'}},
                  )
    converter = ScaleConverter()
    data_weeks = converter.convert(use_seasonality=False, **kwargs)
    data_weeks = data_weeks.sort_index()

    def group(df):
        return df.groupby('city')[value_types['additive']].sum().sort_index()

    def get(df):
        return df.set_index(['city', 'week']).sort_index()

    def compare_to_golden(data, golden_path, obj):
        golden = read_data(__file__, golden_path)
        golden = change_index(golden.sort_values(['city', 'week']), None)
        data = change_index(data, None)[golden.columns]
        check_df(get(change_coding(data)), get(change_coding(golden)), obj=obj)

    if save_golden:
        write_data(change_index(data_weeks, None), __file__, 'scale_converter_golden.pkl')
    else:
        check_df(group(change_coding(data_weeks)), group(change_coding(data)),
                 check_names=False, obj='Total sums')
        compare_to_golden(data_weeks, 'scale_converter_golden.pkl', 'Test with golden ')

    converter = ScaleConverter(seasonality_data=read_data(__file__, 'holidays_fact.pkl'),
                               holidays_data=read_data(__file__, 'holidays_all.pkl'))
    data_weeks = converter.convert(use_seasonality=True, **kwargs)
    data_weeks = data_weeks.sort_index()

    if save_golden:
        write_data(change_index(data_weeks, None), __file__, 'scale_converter_golden_season.pkl')
    else:
        compare_to_golden(data_weeks, 'scale_converter_golden_season.pkl', 'golden with use_seasonality=True ')


# TODO: надо переехать на taxi_rep_amr.dm_amr_geo_tariff_msk
# @pytest.mark.greenplum
# @pytest.mark.parametrize(
#     "scale,to_scale",
#     [
#         ['month', 'week'],
#         ['week', 'month']
#     ])
# def amr_scale_converter_tests(scale, to_scale):
#     df = pd.DataFrame([['br_kazan', '2020-02-01', 4., 5.], ['br_kazan', '2020-03-01', 7., 6.],
#                        ['br_moscow', '2019-02-01', 9., 1.], ['br_moscow', '2019-01-01', 90., 13.]],
#                       columns=['region_id', 'some_scale', 'trips', 'active_drivers'])
#     value_types = {'additive': ['trips'], 'non-additive': ['active_drivers']}
#     this_df = df.copy()
#     this_df[scale] = to_start(df['some_scale'], scale)
#     sc = ScaleConverter()
#     additive = sc.get_columns(value_types, include_type='additive')
#     converted = sc.convert(this_df, value_types, scale=scale, to_scale=to_scale,
#                                index=['region_id'], proportions_mode='amr')
#     # аддитивные колонки должны сходится
#     pd.testing.assert_frame_equal(this_df.groupby('region_id')[additive].sum(),
#                                       converted.groupby('region_id')[additive].sum())
#     is_squueze = SCALES_ORDER.index(scale) < SCALES_ORDER.index(to_scale)
#     # из физического смысла active_drivers
#     assert ((this_df.groupby('region_id')['active_drivers'].max() > converted.groupby('region_id')[
#         'active_drivers'].max()) ^ is_squueze).all()


@pytest.mark.greenplum
def hierarchy_skipping_in_converter_tests():
    hc = HierarchyConverter()
    test = change_index(pd.DataFrame([[u'Москва', 'br_moscow', '2020-04-01', 100.],
                         [u'Москва и МО', 'fi_moscow_and_mr','2020-04-01', 40.]], columns=['city', 'region_id', 'month', 'trips']),
                        ['region_id', 'month'])
    def run(**extra):
        return hc.convert(test, {'additive': 'trips'}, with_base_regions=False,
                          new_regions=['fi_moscow_and_mr'], **extra)

    with pytest.raises(ValueError):
        run()

    def check(golden_index, **extra):
        converted = change_index(run(**extra), ['region_id', 'month'])
        pd.testing.assert_series_equal(test.loc[golden_index]['trips'], converted.loc[u'fi_moscow_and_mr']['trips'])

    check(u'fi_moscow_and_mr', if_exists='skip')
    check(u'br_moscow', if_exists='replace')


def generate_hierarchy_dummy_suites():
    '''
    Генерирует набор мини тестов на комбинации параметров запуска
    '''
    runs = []
    index = ['region_id', 'city']
    columns = index + ['trips']
    base = [[u'br_suzdal', u'Суздаль', 100.], [u'br_agryz', u'Агрыз', 200.]]
    # четсная сумма от base
    direct_sum = base + [[u'fi_ru_50km', u'RU_50K-', 300.0]]
    # какое-то рандомное число вместо суммы
    some_value = base + [[u'fi_ru_50km', u'RU_50K-', 600.0]]
    val = {'additive': ['trips']}
    pskov_basic = [[u'br_velikie_luki', u'Великие Луки', 100.], [u'br_pskov', u'Псков', 10.],
                   [u'br_novosokolniky', u'Новосокольники', 0.], [u'br_pskov_region', u'Псковский регион', 0.]]
    pskov_plus_one = [[u'br_pskovskaja_obl', u'Псковская область', 110.]]
    pskov_plus_two = [[u'br_severo_zapadnyj_fo', u'Северо-Западный ФО', 110.]]

    # дефолтный дефолт
    runs.append({'data': pd.DataFrame(pskov_plus_one, columns=columns),
                 'index': index,
                 'cols': [],
                 'convert': {'value_types': val},
                 'expected': pd.DataFrame(pskov_basic, columns=columns)})
    # конвертация в популяцию, которой нет в данных
    runs.append({'data': pd.DataFrame(base, columns=columns),
                 'index': index,
                 'cols': ['trips'],
                 'convert': {'value_types': val, 'new_regions': [u'fi_ru_50km']},
                 'expected': pd.DataFrame(direct_sum, columns=columns),
                 'compare': {'obj': 'Simple to population convert'}})
    # конвертация в популяцию, которая есть в данных не перезаписывая
    runs.append({'data': pd.DataFrame(some_value, columns=columns),
                 'index': index,
                 'cols': ['trips'],
                 'convert': {'value_types': val, 'new_regions': [u'fi_ru_50km'], 'if_exists': 'skip'},
                 'expected': pd.DataFrame(some_value, columns=columns),
                 'compare': {'obj': 'Population convert with skip'}})
    # конвертация в популяцию, которая есть в данных c перезаписью
    runs.append({'data': pd.DataFrame(some_value, columns=columns),
                 'index': index,
                 'cols': ['trips'],
                 'convert': {'value_types': val, 'new_regions': [u'fi_ru_50km'], 'if_exists': 'replace'},
                 'expected': pd.DataFrame(direct_sum, columns=columns),
                 'compare': {'obj': 'Population convert with replace'}})


    # смешанная конвертация, когда добавляем и популяции и новые регионы
    runs.append({'data': pd.DataFrame(some_value + pskov_basic, columns=columns),
                 'index': index,
                 'cols': ['trips'],
                 'convert': {'value_types': val, 'new_regions': [u'fi_ru_50km', u'br_severo_zapadnyj_fo'], 'if_exists': 'replace'},
                 'expected': pd.DataFrame(direct_sum + pskov_basic + pskov_plus_two, columns=columns),
                 'compare': {'obj': 'Mixed convert'}})
    return runs

@pytest.mark.parametrize(
    "run",
    generate_hierarchy_dummy_suites()
)
@pytest.mark.greenplum
def hierarchy_dummy_tests(run):
    hc = HierarchyConverter()
    conv = hc.convert(run['data'], **run['convert'])
    assert monitor_difference_frames(conv, run['expected'], columns=run['cols'], index=run['index']) is None


@pytest.mark.greenplum
def hierarchy_proportion_tests():
    hc = HierarchyConverter()
    props = hc.get_proportions(custom_regions=['br_dolgoprudny'])
    assert props.empty, props
    props = hc.get_proportions(custom_regions=['br_moscow'])
    assert len(props) == 1, props
    props = hc.get_proportions(custom_regions=['fi_moscow_and_mr'])
    assert (len(props['trips'].unique()) - len(props)) * 1. / len(props) < 0.2, "Proportions should be different"
    props_sum = props.groupby(['region_id'])[ADDITIVE_VALUES].sum()
    bugs = props_sum[~np.isclose(props_sum, 1).any(axis=1)]
    assert bugs.empty, "Proportions do not sum up to 1:\n {}".format(bugs)


@pytest.mark.greenplum
def hierarchy_param_check_tests():
    evil = pd.DataFrame([['br_russia', u'Россия', 100500.],
                         ['br_dolgoprudny', u'Долгопрудный', 121.],
                         ['br_moscow', u'Москва', 1100.],
                         ['crazzzy', u'Фейк', 122.]
                         ],
                        columns=['region_id', 'city', 'trips'])
    hc = HierarchyConverter()
    value = {'additive': ['trips']}
    # это должно отработать
    hc.convert(evil, value, exclude_regions=['br_dolgoprudny', 'br_moscow', 'crazzzy'])
    # это должно развалиться из-за региона ниже аггломерации, фейкового региона и дублирования базовых регионов
    with pytest.raises(BadConvertRegions):
        hc.convert(evil, value)
    # долгопрудный ниже аггломерации, в него нельзя конвертить
    with pytest.raises(BadConvertRegions):
        hc.convert(evil, value, exclude_regions=['br_russia', 'br_moscow'])
    # crazzzy  невалидный айдишник региона
    with pytest.raises(BadConvertRegions):
        hc.convert(evil, value, exclude_regions=['br_dolgoprudny', 'br_moscow'])
    # нельзя скипать базовый регион, неконсистеные данные будут
    with pytest.raises(BadConvertRegions):
        hc.convert(evil, value, exclude_regions=['br_dolgoprudny', 'crazzzy'], new_regions='br_moscow', if_exists='skip')
    # а реплейсить можно
    hc.convert(evil, value, exclude_regions=['br_dolgoprudny', 'crazzzy'], new_regions='br_moscow', if_exists='replace')







