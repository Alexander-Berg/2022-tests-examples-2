# coding: utf-8
import json
import os

import pandas as pd
#НЕ УБИРАТЬ! numpy и statsmodels тащатся ради lambda функций, заданных в конфиге.
import numpy as np
import statsmodels.api as sm
# Модели импортятся все, чтобы фабрику из строчек было легко запускать. Не убирать!
from business_models.models import *
from business_models.util.dates import shift_date
from business_models.util.basic import is_string, Factory, data_to_file, data_from_file, deep_compare, get_list
from business_models.util.dataframes import change_coding, change_index, monitor_difference_frames
from .common import make_path, read_data, check_df, write_data, get_filename
import pytest

from business_models.models.curves import LinearCurve
from business_models.models.curves.curve_fitter import CurveFitter



def make_prediction(df, newbie, cfg):
    model = CohortModel(
        newbie=newbie,
        **cfg['model']
    )
    model.fit(
        df,
        **cfg['common']
    )
    cfg['forecast'].update(cfg['common'])
    result = model.forecast(
        df,
        **cfg['forecast']
    )
    return result


def rectangle_cohort_model_tests():
    # Проверяем, что на одинаковых данных прямоугольные матрицы делают то же, что и полные
    cfg = json.load(open(make_path("rectangle_cohort_prediction_test.config")))
    df = data_from_file(make_path(cfg['source_data']), determine_type=True)

    scale = cfg['common']['scale']
    ndots_fit = cfg['model']['ndots_fit']
    date_to = cfg['common']['date_to']
    newbie = df[df.cohort_date == df[scale]]
    golden_result = make_prediction(df, newbie, cfg)
    df = df[df[scale] >= shift_date(date_to, -ndots_fit - 1, scale)]
    result = make_prediction(df, newbie, cfg)
    dimensions = list(cfg['common']["dimensions"].keys())
    result = result[result[scale] >= date_to]
    golden_result = golden_result[golden_result[scale] >= date_to]
    result, golden_result = change_index([result, golden_result], dimensions + [cfg['common']['scale'], 'cohort_date'])
    pd.testing.assert_frame_equal(result.sort_index(), golden_result.sort_index(), check_like=True)


def cohort_model_tests(save_golden=False):
    cfg = json.load(open(make_path("cohort_prediction_test.config")))
    df = data_from_file(make_path(cfg['source_data']), determine_type=True)

    scale = cfg['common']['scale']
    key_name = cfg['common']["key_name"]
    newbies_constant = 1
    newbie = df[df.cohort_date == df[scale]]
    result = make_prediction(df, newbie, cfg)

    if save_golden:
        data_to_file(change_index(result, None), make_path(cfg['golden_result']), determine_type=True)

    golden_result = data_from_file(make_path(cfg['golden_result']), determine_type=True)
    result = result[golden_result.columns]
    dimensions = list(cfg['common']["dimensions"].keys())
    result, golden_result = change_index([result, golden_result], dimensions + [cfg['common']['scale']])
    pd.testing.assert_frame_equal(result.sort_index(), golden_result.sort_index(), check_like=True)

    #check newbiews as constant against handcrafted constant newbies
    constant_newbies_prediction = make_prediction(df, newbies_constant, cfg)
    constant_newbies_emulated = df[(df.cohort_date == df.month)].copy()
    constant_newbies_emulated[key_name] = newbies_constant
    emulated_constant_newbies_prediction = make_prediction(df, constant_newbies_emulated, cfg)

    pd.testing.assert_frame_equal(emulated_constant_newbies_prediction, constant_newbies_prediction, check_like=True)

    #check with no dimensions and no date_to
    from_period = cfg['common']['date_to']
    to_period = shift_date(from_period, cfg['forecast']['ndots_predict'], scale)
    del cfg['common']['date_to']
    del cfg['common']['dimensions']
    limited_df = df[df[scale] < from_period]

    constant_newbies_prediction = make_prediction(limited_df, newbies_constant, cfg)
    constant_newbies_emulated = df[(df.cohort_date == df[scale]) &
                                           (df[scale] <= to_period)].copy()
    constant_newbies_emulated[key_name] = newbies_constant
    emulated_constant_newbies_prediction = make_prediction(limited_df, constant_newbies_emulated, cfg)

    pd.testing.assert_frame_equal(emulated_constant_newbies_prediction, constant_newbies_prediction, check_like=True)


def glm_model_tests():
    cfg = {
        "source_data": "glm_test_input_20190625.pkl",
        "date_to": 45,
        "dimensions": {"city": None},
        "preprocess_kwargs": {"date_columns": []},
        "add_constant": True,
        "with_seasonality": True,
        "glm_parameters": {
            "family": sm.families.Gaussian(link=sm.genmod.families.links.log)
        },
        "value_name": "organic_new_users",
        "norming": "population",
        "features":
        [
            "yandex_cost",
            "paid_new_users"
        ],
        "features_norming":
        [
            None,
            "population"
        ],
        "discrete_features":
        [
            "city",
            {
                "from_column": "week",
                "feature_function": lambda z: int(2019 == pd.to_datetime(z).year)
            }
        ],
        "prediction_column": "prediction",
        "features_transform": lambda x: np.log(x + 1),
        "golden_train": "glm_test_train_result_20190625.pkl",
        "golden_test": "glm_test_forecast_result_20190625.pkl",
    }

    df = change_coding(data_from_file(make_path(cfg['source_data']), determine_type=True), to_unicode=True)
    date_to = cfg['date_to']
    train = df[df.week_number <= date_to]
    test = df[df.week_number > date_to]
    model = GLMModel(
        add_constant=cfg['add_constant'],
        with_seasonality=cfg['with_seasonality'],
        glm_parameters=cfg['glm_parameters'],
        dimensions=cfg['dimensions']
    )

    train_df = model.fit(train, cfg['value_name'], features=cfg['features'],
                    value_norming=cfg['norming'], features_norming=cfg['features_norming'],
                    discrete_features=cfg['discrete_features'],
                    features_transform=cfg['features_transform'],
                    return_train_df=True,
                    preprocess_kwargs=cfg['preprocess_kwargs']
                    )
    golden_train_df = data_from_file(make_path(cfg['golden_train']), determine_type=True)

    check_df(golden_train_df, train_df, index=['city', 'week'])

    forecast = model.forecast(test, 'prediction', preprocess_kwargs=cfg['preprocess_kwargs'])
    golden_test_df = data_from_file(make_path(cfg['golden_test']), determine_type=True)
    check_df(golden_test_df, forecast, index=['city', 'week'], check_like=True, check_less_precise=2)


def truncated_cohort_config():
    cfg = json.load(open(make_path("truncated_cohort_test.config")))
    return cfg


@pytest.mark.parametrize(
    "kernel_model",
    truncated_cohort_config()["kernel_models"]
)
def truncated_cohort_model_tests(kernel_model, save_golden=False):
    cfg = truncated_cohort_config()
    data = data_from_file(make_path(cfg['source_data']), determine_type=True)
    value_name = cfg["value_name"]
    scale = cfg["scale"]
    dimensions = cfg["dimensions"]
    date_to = cfg["date_to"]
    kernel_age_threshold = cfg["kernel_age_threshold"]
    ndots_predict = cfg["ndots_predict"]

    newbie = data[data.cohort_date == data.month]
    cohort_model_params = cfg.get("cohort_model_params", {})
    cohort_fit_kwargs = cfg.get("cohort_fit_kwargs")
    cohort_forecast_kwargs = cfg.get("cohort_forecast_kwargs")
    key_name = cfg["key_name"]

    kernel_model_name = kernel_model["kernel_model"]
    truncated_cohort_model = TruncatedCohortModel(kernel_age_threshold=kernel_age_threshold,
                                                  cohort_model=(cfg["cohort_model"], cohort_model_params),
                                                  kernel_model=(kernel_model_name,
                                                                kernel_model.get("kernel_forecast_model_init_param")))
    truncated_cohort_model.fit(data,
                               value_name,
                               key_name=key_name,
                               scale=scale,
                               dimensions=dimensions,
                               date_to=date_to,
                               cohort_fit_kwargs=cohort_fit_kwargs)

    result = truncated_cohort_model.forecast(data,
                                             value_name,
                                             ndots_predict=ndots_predict,
                                             key_name=key_name,
                                             scale=scale,
                                             date_to=date_to,
                                             dimensions=dimensions,
                                             cohort_forecast_kwargs=cohort_forecast_kwargs,
                                             kernel_forecast_kwargs=kernel_model["kernel_forecast_kwargs"],
                                             return_all_forecasts=True,
                                             newbie=newbie
                                             )
    if save_golden:
        data_to_file(change_index(result.parts_dict["cohort_forecast"].main_result, None),
                     make_path(kernel_model['golden_cohort_forecast']), determine_type=True)
        data_to_file(change_index(result.parts_dict["kernel_forecast"].main_result, None),
                     make_path(kernel_model['golden_kernel_forecast']), determine_type=True)
        data_to_file(change_index(result.main_result, None),
                     make_path(kernel_model['golden_combined_forecast']), determine_type=True)

    golden_kernel = data_from_file(make_path(kernel_model['golden_kernel_forecast']), determine_type=True)
    golden_cohort = data_from_file(make_path(kernel_model['golden_cohort_forecast']), determine_type=True)
    golden_combined_forecast = data_from_file(make_path(kernel_model['golden_combined_forecast']), determine_type=True)

    def validate_result(result, golden, key=None, **kwargs):
        if key is not None:
            result = result.parts_dict[key].main_result
        else:
            result = result.main_result
        result = result[golden.columns]
        monitor_difference_frames(result, golden, **kwargs)

    index = [scale] + truncated_cohort_model.get_dimensions(dimensions, as_list=True)
    validate_result(result, golden_cohort, "cohort_forecast", index=index + ['cohort_date'])
    validate_result(result, golden_combined_forecast, index=index + ['cohort_date'])
    validate_result(result, golden_kernel, "kernel_forecast", index=index)

@pytest.mark.parametrize(
    "golden_file,value_name,with_date_to,kwargs",
    [
        ['cluster_forecast_data_no_date_to.pkl', 'trips', False, {}],
        ['cluster_forecast_data.pkl', 'trips', True, {}],
        ['cluster_night_calculated.pkl', 'trips', True, {'calculate_clusters': 'night'}],
        ['cluster_many_calculated.pkl', 'trips', True, {'calculate_clusters': ['night', 'morning']}],
        ['cluster_night_exclude.pkl', 'trips', True, {'exclude_clusters': 'night'}],
        ['cluster_supply_change.pkl', 'supply_change', True, {'exclude_clusters': 'night',
         'multiply_before_agg': 'supply'}]
    ]
)
def cluster_model_tests(golden_file, value_name, with_date_to, kwargs, save_golden=False):
    clusters = ['night', 'morning', 'day', 'evening', 'late_evening']
    rules_kwargs = {'night': {'scale': dict(attribute='hour', values=list(range(1,7)))},
                    'morning': {'scale': dict(attribute='hour', values=list(range(7,10)))},
                    'day': {'scale': dict(attribute='hour', values=list(range(10,16)))},
                    'evening': {'scale': dict(attribute='hour', values=list(range(16,21)))},
                    'late_evening': {'scale': dict(attribute='hour', values=list(range(21,24)) + [0])}}

    model = ClusterModel(cluster_kwargs=dict(clusters=clusters, rules='include_attribute',
                                             cluster_kwargs=rules_kwargs))
    fit_data = read_data(__file__, 'cluster_fit_data.pkl')
    scale = 'week'
    model.fit(fit_data, 'trips', fit_scale='hour', model_kwargs= {'ndots_fit': 30},
              other_values=['demand', 'supply'], scale=scale)

    # Test sum of ratio_data
    ratio_data = change_index(model.main_parameters['ratio_data'], None)
    ratio_data = ratio_data.groupby(['city', 'region_id', scale])[['supply', 'demand', 'trips']].sum()
    ratio_data = ratio_data[~np.isclose(ratio_data.sum(axis=1), 3)]
    assert len(ratio_data) == 0, 'TEST cluster_model ratios FAILED: sum of ratio for all clusters ' \
                                 'not equals to 1, %d errors' % len(ratio_data)

    data = read_data(__file__, 'cluster_data.pkl')
    date_to = shift_date(data.week.max(), -26, scale) if with_date_to else None

    prediction = change_index(model.forecast(data, value_name, 26, scale=scale, date_to=date_to, **kwargs),
                              ['region_id', 'city', scale]).sort_index()

    if save_golden:
        write_data(change_index(prediction, None), __file__, golden_file)

    dimensions = list(model['dimensions'].keys())
    index = dimensions + [scale]
    golden = change_index(read_data(__file__, golden_file), index).sort_index()
    monitor_difference_frames(prediction, golden, check_less_precise=2)

    ndots_fact = 30
    prediction = model.fact(fit_data, 'supply_change', ndots_fact, forecast_scale='hour',
                            exclude_clusters='night', multiply_before_agg='supply',
                            forecast_ratio=False, cluster_name='MY_NEW_NAME', scale=scale)
    if save_golden:
        write_data(change_index(prediction, None), __file__, 'cluster_fact_prediction.pkl')

    golden = read_data(__file__, 'cluster_fact_prediction.pkl')

    check_length = prediction.groupby(dimensions)['supply_change'].count()
    if not (check_length == ndots_fact).all():
        raise ValueError('TEST cluster_model fact FAILED: fact returned not ndots_predict periods\n{}'.format(
            check_length[check_length != ndots_fact]
        ))
    monitor_difference_frames(prediction, golden, index=index, check_less_precise=2)


@pytest.mark.parametrize(
    "minimize_parameters,results",
    [
        ({
            'x0': 'lambda x, y: np.array([(np.max(y) - np.min(y))/(np.max(x) - np.min(x)), 0.0])',
        }, [0.9577414, 0.14341011]),
        ({
            'x0': lambda x, y: np.array([(np.max(y) - np.min(y))/(np.max(x) - np.min(x)), 0.0]),
            'bounds': 'lambda x, y: [[(np.max(y) - np.min(y))/(np.max(x) - np.min(x))*0.2, (np.max(y) - np.min(y))/(np.max(x) - np.min(x))*2.0], [None, None]]'
        }, [0.957741, 0.14341])
    ]
)
def curve_fitter_tests(minimize_parameters, results):

    def compare_double_lists(x, y):
        x_y = list(zip(x, y))
        x_y = list(map(lambda x: x[0] == x[1], x_y))
        return all(x_y)

    x_sample = np.linspace(0, 5, 10)
    y_sample = [0.32210110439619843,
                0.7104668484024907,
                0.6916989166221517,
                1.6934135472323544,
                2.0150067062384975,
                3.450203870836894,
                3.622731968640393,
                3.857766719076819,
                4.2582837241228795,
                4.755962629689841]

    cf = CurveFitter()
    formula = minimize_parameters['x0']
    formula_bounds = minimize_parameters.get('bounds')

    aim = eval(formula)(x_sample, y_sample) if is_string(formula) else formula(x_sample, y_sample)
    got = cf.form_minimize_parameters(LinearCurve(), minimize_parameters=minimize_parameters,
                                      x_sample=x_sample, y_sample=y_sample)['x0']

    assert compare_double_lists(aim, got), \
        'TEST curve_fitter_tests FAILED for x0 = {} and bound = {}. form_minimize_parameters returned incorrect results'.format(
            formula, formula_bounds) + '\n' + \
        'We needed {} and got {}'.format(aim, got)

    if formula_bounds is not None:
        aim = eval(formula_bounds)(x_sample, y_sample) if is_string(formula_bounds) else formula_bounds(x_sample, y_sample)
        got = cf.form_minimize_parameters(LinearCurve(), minimize_parameters=minimize_parameters,
                                          x_sample=x_sample, y_sample=y_sample)['bounds']

        assert compare_double_lists(aim, got), \
            'TEST curve_fitter_tests FAILED for x0 = {} and bound = {}. form_minimize_parameters returned incorrect results'.format(
                formula, formula_bounds) + '\n' + \
            'We needed {} and got {}'.format(aim, got)

    opm = OneParameterModel(curve='LinearCurve',
                            curve_fitter_parameters={'minimize_parameters': minimize_parameters},
                            verbose=False)

    opm.fit(pd.DataFrame({'y_raw': y_sample, 'x': x_sample
                             , 'week': pd.to_datetime(['2019-01-01'] * len(x_sample))
                             , 'city': [u'Москва'] * len(x_sample)
                             , 'region_id': [u'BR00001'] * len(x_sample)}),
            'y_raw', parameter_name='x')

    aim = np.round(opm.main_parameters['fitted_parameters'][(u'Москва', u'BR00001')], 6)
    got = np.round(results, 6)

    assert compare_double_lists(aim, got), \
        'TEST curve_fitter_tests FAILED for x0 = {} and bound = {}. Fitted parameters differ.'.format(
            formula,  formula_bounds) + '\n' + \
        'We needed {} and got {}'.format(aim, got)


def curve_fitter_test_within_one_parameter_model_tests():
    df = read_data(__file__, 'df_h_points_for_curve_fitter.pkl')
    minimize_parameters = {
        'x0': lambda x, y: [np.percentile(x, 10),
                            (np.percentile(x, 90) - np.percentile(x, 10)) / 2.0,
                            (np.percentile(y, 95) - np.percentile(y, 1)) * np.sqrt(2 * np.pi) * (
                                        np.percentile(x, 90) - np.percentile(x, 10)) / 2.0,
                            np.percentile(y, 1)],
        'bounds': lambda x, y: [[np.min(x), np.max(x)],
                                [None, None],
                                [None, None],
                                [0.0, np.percentile(y, 50)]]
    }

    outliers_parameters = dict(
        outliers_methods=["QuantileOutliers"],
        outliers_methods_parameters=[{
            "x_axis": True, "x_how": "both", "x_quantile": 0.98,
            "y_axis": True, "y_how": "both", "y_quantile": 0.98,
            "w_axis": True, "w_how": "left", "w_quantile": 0.9}]
    )

    opm = OneParameterModel(curve='NormalDistributionUpperCurve',
                            curve_fitter_parameters={'minimize_parameters': minimize_parameters},
                            verbose=False,
                            outliers="MultipleOutliers",
                            outliers_parameters=outliers_parameters
                            )

    opm.fit(df, 'y_raw', fit_scale='hour', parameter_name='x', weights_name='demand')


@pytest.mark.parametrize(
    "golden_file,value_name,dimensions",
    [
        ['elasticity_value_name_demand_elasticity_dimensions_city.pkl', 'demand_elasticity', ['city']],
        ['elasticity_value_name_demand_elasticity_dimensions_city_region_id.pkl', 'demand_elasticity', ['city', 'region_id']],
        ['elasticity_value_name_supply_change_dimensions_city.pkl', 'supply_change', ['city']],
        ['elasticity_value_name_supply_change_dimensions_city_region_id.pkl', 'supply_change', ['city', 'region_id']]
    ]
)
def elasticity_tests(golden_file, value_name, dimensions, save_golden=False):
    init = {
        "conversion_model": "NormalDistributionUpperCurve",
        "demand_elasticity_bounds": [0.49, 0.51],
        "outliers": "BestScoreOutliers",
        "outliers_parameters": {"drop_part": 0.01},
        "use_agg_dots": True,
        "use_separate_splitting": True
    }

    fit_data = read_data(__file__, 'elasticity_fit_data.pkl')
    data = read_data(__file__, 'elasticity_forecast_data.pkl')

    model = ElasticityModel(**init)
    model.fit(fit_data, fit_scale='hour', ndots_fit=6, dimensions=dimensions)
    prediction = model.forecast(data, ndots_predict=26, value_name=value_name, dimensions=dimensions)

    if save_golden:
        write_data(change_index(prediction, None), __file__,  golden_file)

    golden = read_data(__file__, golden_file)
    monitor_difference_frames(prediction, golden, index=dimensions + ['week'])


@pytest.mark.parametrize(
    "model_name,model_inits,save_params,expected_files_count",
    [
        ["CohortModel", {"newbie": 1}, {"recursive": True, "name": "cohort"}, 1],
        ["ActivityCohortModel", {"newbie": 1, "heads_model": 'TruncatedCohortModel'},
         {"recursive": False, "name": "activity"}, 1],
        ["ActivityCohortModel", {"newbie": 1, "heads_model": 'TruncatedCohortModel'},
         {"recursive": True, "name": "activity"}, 4],
        ["ActivityCohortModel", {"newbie": 1, "heads_model": 'TruncatedCohortModel', },
         {"recursive": True, "name": "activity"}, 4],
        ["ElasticityModel", {}, {"recursive": True, "name": "elasticity"}, 2],
        ["ClusterModel", {"cluster_kwargs": {"clusters": ["one", "two", "three"]}},
         {"recursive": True, "name": "cluster"}, 10],
        ["MultipleConfigs", {"model_name": "CohortModel", "newbie": 1, "configs_path":
            make_path('model_tests', 'multiple_configs')}, {"recursive": True, "name": "multiple"}, 4]
    ]
)
def save_model_tests(tmpdir, model_name, model_inits, save_params, expected_files_count):
        model = Factory.get(Model, model_name, **model_inits)
        files = model.save(models_path=str(tmpdir), **save_params)
        assert len(files) == expected_files_count
        for file in files:
            file_path = os.path.join(str(tmpdir), file)
            assert os.path.isfile(file_path)
            source = model
            for p in file.split('.')[1:]:
                if p.isdigit():
                    p = int(p)
                source = source[p]
            type(source).load(file, models_path=str(tmpdir))


def get_elasticity_methods(save_golden=False):
    result = [
        ['get_conversion', 2],
        ['get_conversion_by_elasticity', 1],
        ['get_demand_change', 2],
        ['get_demand_elasticity', 2],
        ['get_elasticity', 2],
        ['get_fitted_dimensions', 0],
        ['get_supply', 2],
        ['get_supply_change', 2],
        ['get_supply_elasticity', 2],
        ['get_trips', 2],
    ]
    if save_golden:
        [res.append(save_golden) for res in result]
    return result

elasticity_subdir = 'elasticity/'


def get_elasticity_model():
    data = read_data(__file__, elasticity_subdir + 'fit_data')
    model = ElasticityModel(conversion_model='NormalDistributionUpperCurve')
    model.fit(data, 'trips', fit_scale='hour', ndots_fit=4, dimensions='city')
    return model


class TestsElasticity(object):
    model = get_elasticity_model()

    def _method_call(self, method, args, kwargs, target_type, save_golden=False, suffix=''):
        if self.model['balance_bounds'] is None:
            self.model['balance_bounds'] = self.model.get_balance_bounds()

        if method == 'get_supply':
            args = list(args)
            args[0], args[1] = args[1], args[0]  # чтобы нормальные числа получились

        result = getattr(self.model, method)(*args, **kwargs)
        if len(args) != 0 and method not in ['get_elasticity', 'get_conversion_by_elasticity']:
            assert isinstance(result, target_type)

        golden_file = elasticity_subdir + method + suffix
        if save_golden:
            write_data(result, __file__, golden_file)
        else:
            golden = read_data(__file__, golden_file)
            if isinstance(result, pd.Series):
                pd.testing.assert_series_equal(result, golden)
            else:
                result = get_list(result)
                if isinstance(golden, pd.Series):
                    golden = golden.values
                elif isinstance(golden, (tuple, list)) and isinstance(golden[0], pd.Series) \
                        and not isinstance(result[0], pd.Series):
                    golden = [g.values for g in golden]
                else:
                    golden = get_list(golden)
                ordered = True if method != 'get_fitted_dimensions' else False
                deep_compare(result, golden, ordered=ordered)

    @pytest.mark.parametrize(
        "method, args_cnt",
        get_elasticity_methods()
    )
    def method_float_tests(self, method, args_cnt, save_golden=False):
        args = {
            0: [],
            1: [0.6],
            2: [22.8, 7]
        }[args_cnt]
        self._method_call(method, args, {'dimensions_values': u'Москва'},
                          target_type=np.float, save_golden=save_golden, suffix='_float')

    @pytest.mark.parametrize(
        "method, args_cnt",
        get_elasticity_methods()
    )
    def method_array_tests(self, method, args_cnt, save_golden=False):
        if method in ['get_conversion_by_elasticity']:
            return # для них не актуален этот тест

        if args_cnt != 0:
            args = {
                1: [np.array([0.6, 1.2])],
                2: [np.array([22.8, 9]), np.array([7, 3])]
            }[args_cnt]
            self._method_call(method, args, {'dimensions_values': u'Москва'},
                          target_type=np.ndarray, save_golden=save_golden, suffix='_array')
        else:
            args = []
        self._method_call(method, args, {'dimensions_values': [(u'Москва', ), (u'Чита', )]},
                          target_type=np.ndarray, save_golden=save_golden, suffix='_array_list_dim')

    @pytest.mark.parametrize(
        "method, args_cnt",
        get_elasticity_methods()
    )
    def method_series_tests(self, method, args_cnt, save_golden=False):
        if args_cnt == 0 or method in ['get_conversion_by_elasticity']:
            return  # для них не актуален этот тест

        args = {
            1: [pd.Series([0.6, 1.2])],
            2: [pd.Series([22.8, 9]), pd.Series([7, 3])]
        }[args_cnt]
        self._method_call(method, args, {'dimensions_values': u'Москва'},
                          target_type=pd.Series, save_golden=save_golden, suffix='_series')
        dimensions_values = [u'Москва', u'Чита']
        self._method_call(method, args, {'dimensions_values': dimensions_values},
                          target_type=pd.Series, save_golden=save_golden, suffix='_series_list_dim')
        args = [pd.Series(s.values, index=dimensions_values) for s in args]
        self._method_call(method, args, {},
                          target_type=pd.Series, save_golden=save_golden, suffix='_series_index_dim')

    def consistency_tests(self):
        demand = [1, 2, 3.600608979820667]
        supply = [5, 5, 1]
        conversion = self.model.get_conversion(demand, supply, u'Москва')
        trips = self.model.get_trips(demand, supply, u'Москва')
        assert all(trips == conversion * demand)
