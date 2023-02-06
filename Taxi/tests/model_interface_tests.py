# coding: utf-8
# import matplotlib
# matplotlib.use('Agg')

from business_models.models import *
import pandas as pd
from business_models.util.basic import  Factory, data_to_file, data_from_file, deep_compare, get_list, \
    dict_recursive_update
from business_models.cross_platform import PYTHON_VERSION
from business_models.util.dates import shift_date, periods_in_year
from business_models.util.dataframes import change_coding, get_missing_dates, change_index, \
    monitor_difference_frames, test_dataframe
from tests.common import get_filename, read_data, make_path, write_data
import copy
import pytest
import os
from business_models.models.model import ModelParametersWarning, ModelParametersError, \
    ModelDateForecastTypes


DEFAULT_COHORT_MODEL_CONFIG = 'default_test_parameters_cohort.json'
DEFAULT_MODEL_CONFIG = 'default_test_parameters_ordinary.json'


def validate_scale_difference(result, golden, dimensions, scale):
    """Если в result и golden для каких-то измерений различается  количество и значения скейлов,  то
    кинет исключение с этими расхождениями
    Основан на util.dataframes.get_missing_dates
    """
    test_cases = [
        [result, golden, '_golden', 'Missing values in result'],
        [golden, result, '_result', 'Extra values in result'],
    ]
    messages = []
    for cur_result, cur_golden, suffix, message in test_cases:
        difference = get_missing_dates(cur_result, cur_golden, dimensions, scale, golden_suffix=suffix)
        if len(difference) != 0:
            messages.append('{}:\n{}'.format(message, difference))

    if len(messages) != 0:
        raise ValueError('\n'.join(messages))


class TestSuite(object):
    """
    Структура, в которой лежит проинциализированная модель и конфиги ее запуска
    """
    def __init__(self, testing_model_type, value_name, fit_data, forecast_data,
                 month_data, init_parameters=None, fit_parameters=None, forecast_parameters=None,
                 same_fit_forecast_data=False, scale='week'):
        """
        :param testing_model_type: type - Модель, которую тестируем
        :param value_name: str
        :param fit_data: pd.DataFrame - данные для обучения модели
        :param forecast_data: pd.DataFrame - данные для предсказания модели
        :param month_data: pd.DataFrame - данные в меячном скейле для тестирования корректноти работы с
            не дефолтным скейлом
        :param init_parameters: dict - параметры для init
        :param fit_parameters: dict - параметры для fit
        :param forecast_parameters: dict - параметры для forecast
        :param same_fit_forecast_data: bool. - Одинаковая ли дата для обучения и прогноза.
                                        Если true, в случе смены scale на тестах, заменится и fit_data, и forecast data.
                                        Если False - только forecast_data
        """
        self.testing_model_type = testing_model_type
        self.init_parameters = init_parameters or {}
        self.model = self.testing_model_type(**self.init_parameters)
        self.fit_parameters = fit_parameters or {}
        self.forecast_parameters = forecast_parameters or {}
        self.value_name = value_name
        self.fit_data = fit_data
        self.forecast_data = forecast_data
        self.month_data = month_data
        self.same_fit_forecast_data = same_fit_forecast_data
        self.scale = scale

    @property
    def ndots_predict(self):
        return periods_in_year[self.scale]

    @property
    def dimensions(self):
        return self.model.get_dimensions(self.model['dimensions'], as_list=True)

    def change_dimensions_to(self, exact_one_name):
        """Если у модели в main_parameters есть init_parameters, то ее надо переинициализировать
        при изменении списка измерений
        Прямо сейчас это переделка измерений из [city, region_id] в city
        Переинициализации модели при этом не происходит
        """
        if 'dimensions_lst' in self.init_parameters:
            dimensions_lst = self.init_parameters['dimensions_lst']
            if isinstance(dimensions_lst[0], dict):
                dimensions_lst = [{exact_one_name: x[exact_one_name]} for x in dimensions_lst]
            else:
                dimensions_lst = [x[0] for x in dimensions_lst]
            self.init_parameters['dimensions_lst'] = dimensions_lst

    def run_method(self, method, **kwargs):
        """
        :param method: str - название метода, который будет дергаться у self.model
        :param kwargs: дополнительные аргументы для вызова метода (кроме self."{method}_parameters")
        :return: результат высова метода
        """
        if method == 'fit_forecast':
            for m in ['fit', 'forecast']:
                kwargs['%s_kwargs' % m] = copy.deepcopy(getattr(self, m + '_parameters', {}))
        else:
            kwargs.update(copy.deepcopy(getattr(self, method + '_parameters', {})))

        self.scale = kwargs.get('scale', self.scale)
        if method == 'init':
            self.model.__init__(**kwargs)
            return

        data_attribute = method if method != 'fit_forecast' else 'forecast'
        data = getattr(self, data_attribute + '_data')
        args = [data, self.value_name]  # проверяем корректность позиционной передачи аргументов
        if method in ['forecast', 'fact', 'fit_forecast']:
            args.append(self.ndots_predict)

        return getattr(self.model, method)(*args, **kwargs)

    def __str__(self):
        if isinstance(self.model, SeriesModelWrapper):
            return type(self.model).__name__ + "-" + type(self.model["series_model"]).__name__
        return type(self.model).__name__

    def copy(self):
        parameters = copy.deepcopy({k: v for k, v in self.__dict__.items()
                                    if k != 'model'  # точно не аффектим метод copy
                                    })
        return TestSuite(**parameters)

    def _get_filtered(self, data, forecast=None, type='future'):
        """Фильтрует данные относительно последней фактовой точки в прогнозе (forecast),
        если forecast не передан, то считается, что прогноз - это data"""
        data = change_index(data, None)
        if forecast is None:
            forecast = data
        else:
            forecast = change_index(forecast, None)

        last_fact_date = shift_date(forecast[self.scale].max(), -self.ndots_predict, self.scale)
        mask = {
            'future': data[self.scale] > last_fact_date,
            'past': data[self.scale] <= last_fact_date
        }[type]
        return data[mask]

    def get_future(self, data, forecast=None):
        """Возвращает по прогнозу только кусок с будущим, из колонок остается только
        value_name, scale и dimensions. Результат сгруппирован по scale+dimensions
        Также сортирует данныые и сбрасывает индекс, чтобы они дальше точно правильно сравнивались

        :param data: DataFrame
        :param forecast: DataFrame - по нему определяется граница факта и прогноза, если forecast
            не передан, то считается, что прогноз - это data
        :return: DataFrame
        """
        data = self._get_filtered(data, type='future', forecast=forecast)
        data = data.groupby(self.dimensions + [self.scale], sort=True)[self.value_name].sum()
        return data.reset_index()

    def get_past(self, data, forecast=None):
        """Возвращает по прогнозу только кусок с прошлым, колонки при этом
        обрезаются по колонкам из self.forecast_data
        Также сортирует данныые и сбрасывает индекс, чтобы они дальше точно правильно сравнивались

        :param data: DataFrame
        :param forecast: DataFrame - по нему определяется граница факта и прогноза, если forecast
            не передан, то считается, что прогноз - это data
        :return: DataFrame
        """
        data = self._get_filtered(data, type='past', forecast=forecast)
        data = data[[col for col in data.columns if col in self.forecast_data]]
        return data.sort_values(self.dimensions + [self.scale]).reset_index(drop=True)


def get_model_config(model_name, path=None):
    """По названию модели возвращает название ее персонального конфига с параметрами
    Если model_name не передано, но передан path, то вернет его (совместимость для
    чтения и записи дефолтных конфигов)

    :param model_name: Union(str, None)
    :param path: Union(str, None)
    :return: str
    """
    if model_name is None and path is None:
        raise ValueError('Pass model_name or path')
    if model_name is not None:
        path = '{}_test.json'.format(model_name)
    return path


def get_default_model_config(model_type):
    """По типу модели получает название дефолтного конфига для всех моделей
    похожих на нее (например, когортных)

    :param model_type: type(Model) или объект Model
    :return: str
    """
    if model_type.is_cohort:
        return DEFAULT_COHORT_MODEL_CONFIG
    return DEFAULT_MODEL_CONFIG


def read_config(model_name=None, path=None):
    """Прочитать параметры из конфига модели по пути или названиню модели

    :param model_name: str
    :param path: str
    :return: dict
    """
    path = get_model_config(model_name, path)
    parameters = read_data(__file__, path)
    return parameters or {}


def write_config(parameters, model_name=None, path=None):
    """Аналогично read_config, но запись параметров

    :param parameters: dict
    :param model_name: str
    :param path: str
    :return: str - путь к конфигу
    """
    path = get_model_config(model_name, path)
    return write_data(parameters, __file__, path)


def get_model_parameters(model_type, parameters=None):
    """Читает дефолтный конфиг с параметрами, подходящий для модели, обновляет его по
    данным из конфига конкретной модели (если он существует). В конце обновляет
    параметрами переданными через parameters.
    Все обновления делаются через dict_recursive_update
    Название конфига модели и дефолтного конфига можно получить через get_model_config
    и get_default_model_config
    Данные в параметры не подставляются (тут остаются относительные пути к ним)

    :param model_type: type(Model) или объект Model
    param parameters: dict - дополнительные параметры модели (например, SeriesModel для
        SeriesModelWrapper)
    :return: dict
    """
    model_parameters = read_config(path=get_default_model_config(model_type))
    dict_recursive_update(model_parameters, read_config(model_type.__name__))
    dict_recursive_update(model_parameters, parameters or {})
    return model_parameters


def get_test_suite(model_name, parameters=None):
    """Читает параметры модели через get_model_parameters, читает fit_data/forecast_data
    и создает объект TestSuite для модели

    param model_name: str - название модели, для которой нужно собрать TestSuite
    param parameters: dict - дополнительные параметры модели (например, SeriesModel для
        SeriesModelWrapper)
    return TestSuite - структура, содержащая все данные для тестирования модели
    """
    model_type = Factory.get_type(Model, model_name)
    model_parameters = get_model_parameters(model_type, parameters)
    default_data_path = model_parameters.pop('data')
    paths = []
    for data_parameter in ['fit_data', 'forecast_data', 'month_data']:
        data_path = model_parameters.get(data_parameter, default_data_path)
        paths.append(data_path)
        model_parameters[data_parameter] = change_coding(read_data(__file__, data_path))
    same_fit_forecast_data = paths[0] == paths[1]

    test_suite = TestSuite(model_type,
                           same_fit_forecast_data=same_fit_forecast_data,
                           **model_parameters)
    return test_suite


def get_all_test_suites():
    """
    Собирает все конфиги моделей
    return dict(). params - список с самими конфигами для тестирования.
    ids - имена для них, чтобы было SeriesModelWrapper:PaddingModel , а не SeriesModelWrapper:SeriesModel2
    """
    test_suites = []
    for model_name in Factory.summon_all_children(Model, as_names=True):
        if model_name != "Model":
            # Для SeriesModelWrapper нужно собрать все SeriesModels
            if model_name == 'SeriesModelWrapper':
                for series_model in Factory.summon_all_children(SeriesModels, as_names=True):
                    if series_model != 'SeriesModels':
                        parameters = {'init_parameters': {u'series_model': series_model}}
                        test_suites.append(get_test_suite(model_name, parameters=parameters))
            else:
                test_suites.append(get_test_suite(model_name))
    return test_suites


ALL_TEST_SUITES = get_all_test_suites()
# ALL_TEST_SUITES = []
DATE_TO_VALUES = [None, '2019-01-07']


@pytest.fixture(params=ALL_TEST_SUITES,  # значения из списка будут попадать в request.param
                ids=[str(suite) for suite in ALL_TEST_SUITES]  # в тесте будут отображаться названия отсюда
                )
def test_suite(request):
    """Фикстура: вызывается перед выполнением каждой функии из тестов
    и возвращает значение в аргумент функции test_suite"""
    test_suite_instance = request.param
    return test_suite_instance.copy()  # чтобы тесты не аффектили друг друга


class TestsModelInterface:

    def default_run_tests(self, test_suite, save_golden=False):
        """Проверка, что при полностью дефолтных параметрах фит+форкаст не падают"""
        test_suite.run_method('fit')
        forecast = test_suite.run_method('forecast')

        golden_filename = 'default_run_{}_golden'.format(str(test_suite))
        golden = read_data(__file__, golden_filename)
        if save_golden or golden is None:
            write_data(forecast, __file__, golden_filename)
        else:
            monitor_difference_frames(forecast, golden, index=test_suite.dimensions + [test_suite.scale])

    @pytest.mark.parametrize(
        "date_to",
        DATE_TO_VALUES
    )
    def not_changes_past_tests(self, test_suite, date_to):
        """Проверка, что фит+форкаст не меняет прошлое в данных"""
        test_suite.run_method('fit', date_to=date_to)
        result = test_suite.run_method('forecast', date_to=date_to)
        past = test_suite.get_past(result)
        golden = test_suite.get_past(test_suite.forecast_data, forecast=result)  # чтобы не думать про тип модели

        deep_compare(past.columns, golden.columns, message='Some columns was dropped after forecast')
        validate_scale_difference(past, golden, test_suite.dimensions, test_suite.scale)
        monitor_difference_frames(past, golden, index=test_suite.dimensions + [test_suite.scale],
                                  message='Some past values was changed while predicting "{}"'.format(
                                      test_suite.value_name))
        pd.testing.assert_frame_equal(past, golden, check_like=True, check_column_type=False, check_dtype=False)

    @pytest.mark.parametrize(
            "dimensions, scale, pass_to_init, pass_to_fit",
            # проверяем только не дефолтные значения + используем знание о незаисимости dimensions от scale
            [
                 ('city', 'month', True, True),
                 ('city', 'month', True, False),
                 ('city', 'month', False, True),
             ]
        )
    def params_consistency_tests(self, test_suite, dimensions, scale, pass_to_init, pass_to_fit):
        """
        Проверка корректности передачи dimensions, date_to, scale в init и/или fit
        """
        kwargs = {'dimensions': dimensions, 'scale': scale}
        init_extra = kwargs if pass_to_init else {}
        fit_extra = kwargs if pass_to_fit else {}
        if scale == 'month':
            test_suite.fit_data = test_suite.forecast_data = test_suite.month_data

        test_suite.change_dimensions_to(dimensions)
        test_suite.run_method('init', **init_extra)
        test_suite.run_method('fit', **fit_extra)

        assert test_suite.model['scale'] == scale, 'Main parameters scale is wrong'
        deep_compare(test_suite.dimensions, get_list(dimensions), message='Dimensions was saved incorrectly')

        if dimensions == 'city':
            test_suite.forecast_data = test_suite.forecast_data.drop('region_id', axis=1)
        test_suite.run_method('forecast')

    @pytest.mark.parametrize(
        "parameter_name, fit_value, forecast_value",
        [('dimensions', 'city', ['city', 'region_id']),
         ('scale', 'week', 'month'),
         ('date_to', '2019-06-01', '2019-01-01')]
    )
    def params_consistency_fail_tests(self, test_suite, parameter_name, fit_value, forecast_value):
        """
        Проверка ошибок/ворнингов при несовпадении dimensions, scale, date_to в fit и forecast
        """
        test_suite.run_method('fit', **{parameter_name: fit_value})

        if (parameter_name == 'dimensions') or (parameter_name == 'scale'
                                                and test_suite.model.restrict_forecast_scale):
            with pytest.raises(ModelParametersError):
                test_suite.run_method('forecast', **{parameter_name: forecast_value})

        elif parameter_name == 'date_to':
            with pytest.warns(ModelParametersWarning):
                test_suite.run_method('forecast', **{parameter_name: forecast_value})

    def fit_return_tests(self, test_suite):
        """
        Проверка того, что fit возвращает тренировочные данные
        """
        fit_result = test_suite.run_method('fit', return_train_df=True)
        assert fit_result is not None

    @pytest.mark.parametrize(
        "date_to",
        DATE_TO_VALUES
    )
    def prediction_length_tests(self, test_suite, date_to):
        """
        Проверка соответсвия длины предсказания ndots_predict
        """
        test_suite.run_method('fit', date_to=date_to)
        result = test_suite.run_method('forecast', date_to=date_to)
        future = test_suite.get_future(result)
        test_dataframe(future, dimension=test_suite.dimensions, name='future_data',
                       tests=['nan', 'inf'])
        future = future.groupby(test_suite.dimensions)[test_suite.scale].count()
        incorrect_length = future[future != test_suite.ndots_predict]
        if len(incorrect_length) != 0:
            raise ValueError('Some dimensions was predicted incorrectly '
                             '(ndots_predict={}), but found:{}'.format(
                test_suite.ndots_predict, incorrect_length
            ))

    def return_all_forecasts_tests(self, test_suite):
        """
        Проверка того, что при флаге return_all_forecasts модель возвращает объект ModelResultHolder
        """
        test_suite.run_method('fit')
        result = test_suite.run_method('forecast', return_all_forecasts=True)
        assert isinstance(result, ModelResultHolder)

        if test_suite.model.future_forecast_type == ModelDateForecastTypes.model_composition:
            # TODO тест на то, что все правильно складывается + учет того, что вложенности сами
            # могут быть композитными моделями
            assert len(result.parts_dict) != 0, 'No parts provided for composite model'

    def wrong_scale_tests(self, test_suite):
        """
        Проверка того, что если scale не содержится в данных, то модель упадет
        """
        with pytest.raises((ValueError, KeyError)):
            test_suite.run_method('fit', scale='infinity')

        test_suite.run_method('init')
        test_suite.run_method('fit')
        with pytest.raises((ValueError, KeyError)):
            test_suite.run_method('forecast', scale='infinity')

    def _validate_pickled(self, test_suite):
        filename = str(test_suite)
        data_to_file(test_suite.model, filename, determine_type=True)
        loaded_model = data_from_file(filename, determine_type=True)
        deep_compare(loaded_model, test_suite.model, ordered=True)
        os.remove(filename)

    def _validate_copied(self, test_suite):
        copy_model = test_suite.model.copy()
        deep_compare(copy_model, test_suite.model, validate_copy=True, ordered=True)

    @pytest.mark.parametrize(
        "validate_method",
        ['_validate_pickled',
         '_validate_copied']
    )
    def pickle_copy_tests(self, test_suite, validate_method):
        """
        Проверка сохранения содержимого модели при ее загрузке в файл и выгрузке из него
        """
        getattr(self, validate_method)(test_suite)
        test_suite.run_method('fit')
        getattr(self, validate_method)(test_suite)
        test_suite.run_method('forecast')
        getattr(self, validate_method)(test_suite)

    @pytest.mark.skipif(PYTHON_VERSION < 3, reason='Tests skipped because of unicode errors in plot titles')
    def verbose_tests(self, test_suite):
        """
        Проверка работы отрисовки моделей (проверяем с date_to, чтобы не думать про
        разные типы моделей)
        """
        def validate_plot(skip_fig_validate=False):
            fig = test_suite.model.plot([u'Казань', 'BR00231'])
            if not skip_fig_validate:
                assert fig is not None

        date_to = DATE_TO_VALUES[1]
        test_suite.run_method('init', verbose=True)
        validate_plot(skip_fig_validate=True)
        test_suite.run_method('fit', verbose=True, date_to=date_to)
        validate_plot(skip_fig_validate=True)
        test_suite.run_method('forecast', verbose=True, date_to=date_to)
        validate_plot()  # тут все должны отрисовать хотя бы сам прогноз

    def fit_forecast_tests(self, test_suite):
        test_suite.fit_data = test_suite.forecast_data = test_suite.month_data
        test_suite.run_method('fit_forecast', scale='month')


def run_model_test(model_name, test_name, get_test_suite_kwargs=None, args=None, **kwargs):
    """Запускает конкретный тест на модель

    :param model_name: str
    :param test_name: str - название метода TestsModelInterface
    :param kwargs: аргументы, которые будут передаваться в тест
    """
    test_suite = get_test_suite(model_name, **(get_test_suite_kwargs or {}))
    getattr(TestsModelInterface(), test_name)(test_suite, *(args or []), **kwargs)

# def run_test_list(tests, testing_model, methods_kwargs=None, **kwargs):
#     """
#     Метод позволяющий прогонять отдельные тесты для конкретной модели. Нужно передавать самому все необходимые параметры
#     param tests: Union(list, str) - тесты, которые хочется прогнать
#     param testing_model: str - Модель, для которой нужно прогнать тесты
#     param methods_kwargs: dict - конфиги для запуска отдельных тестов
#     """
#     methods_kwargs = methods_kwargs or {}
#     tests = get_list(tests)
#     failed_tests = []
#     for method in tests:
#         method_kwargs = methods_kwargs.get(method) or {}
#         method_kwargs.update(kwargs)
#         try:
#             getattr(TestsModelInterface, method)(get_test_suite(testing_model), **method_kwargs)
#             print('{} passed successfully \n'.format(method))
#         except Exception as e:
#             failed_tests.append(method)
#             print('{} ended with errors for {}: {} \n '.format(method, testing_model, e))
#     print('---------------------------------------------------')
#     if len(failed_tests) > 0:
#         print('{} tests out of {} failed. \n \n Failed tests are {}'.format(len(failed_tests), len(tests),
#                                                                             ', '.join(failed_tests)))
#     else:
#         print('All tests passed')
#
#
# def run_all(testing_model, methods_kwargs=None, **kwargs):
#     """
#     Запускает все тесты для конкретной модели (формирует полный список тестов и честно запускает run_test_list)
#     param testing_model: str - Модель, для которой нужно прогнать тесты
#     param methods_kwargs: dict - конфиги для запуска отдельных тестов
#      """
#     methods_kwargs = methods_kwargs or {}
#     all_tests = [x for x in dir(TestsModelInterface) if not (x.startswith('_') or x.startswith('pytest'))
#                  if 'tests' in x if x is not 'model_interface_tests']
#     run_test_list(all_tests, testing_model, methods_kwargs, **kwargs)
#
#
#
#
