# coding: utf-8
from business_models.cross_platform import PYTHON_VERSION

from past.builtins import basestring
from typing import Iterable
from copy import deepcopy
import numpy as np
import pandas as pd
import pytest
from pandas.util.testing import assert_frame_equal
import itertools
from business_models.util import *
from business_models.util.log import Handler, ImportHandler, get_logger_with_default
from business_models.config_holder import ConfigHolder
from business_models.util.taskmanager import RaisingProcess
import time
import os
import sys
if sys.version_info[0] < 3:
    from contextlib2 import nullcontext
else:
    from contextlib import nullcontext


@pytest.mark.parametrize(
    "with_print,with_start,with_raise,raise_exceptions,with_logfile",
    [[True, True, False, False, False],
     [True, False, False, False, False],
     [False, False, False, False, False],
     [True, True, True, False, False],
     [True, True, True, True, True],
     [False, True, True, True, True]
     ]
)
def run_timer_tests(capsys, tmpdir, with_print,with_start,with_raise, raise_exceptions, with_logfile):
    '''
    :param capsys:  фикстура, перехватывающая stdout и stderr исполняемого
    :param tmpdir: фикстура временной папки для данных
    :param with_print: передается в Timer, ожидаем ли вывод в stdout
    :param with_start: передается в Timer, ожидаем ли вывод сообщения о старте
    :param with_raise:  bool, добавить ли выброс  исключения в оборачиваемую команду
    :param raise_exceptions: передается в Timer, ожидаем ли падения в случае эксепшена
    :param with_logfile: bool, добавить ли опцию logfile в Timer
    :return:
    '''
    logfile = None
    if with_logfile:
        logfile = os.path.join(str(tmpdir), 'timer_log')
    context_manager =  pytest.raises(RuntimeError) if with_raise and raise_exceptions else nullcontext()
    with context_manager:
        with Timer('test_stuff', with_start=with_start, with_print=with_print, raise_exceptions=raise_exceptions,
                   logfile=logfile):
            time.sleep(1)
            if with_raise:
                raise RuntimeError('AAAA')
    captured = capsys.readouterr()
    def test_out(resource):
        assert not with_start or 'test_stuff starts' in resource
        assert 'test_stuff ends' in resource
        assert not with_raise or 'AAAA\n  Raised exception: {}'.format(raise_exceptions) in resource
    if with_print:
        test_out(captured.out)
    if logfile is not None:
        logged = open(logfile).read()
        test_out(logged)
        os.remove(logfile)

def import_handler_tests():
    with pytest.warns(ImportWarning):
        with ImportHandler(__file__):
            import blablabla
    with ImportHandler(__file__) as _ih:
        import blablabla
    assert not _ih.success


@pytest.mark.parametrize(
    'testing_a',
    [[True], [False]]
)
def finally_call_tests(testing_a):
    some_dict = {'k': 1}

    def some_function(a):
        if a:
            return a
        else:
            raise ValueError

    def change():
        some_dict['k'] = 2

    with Handler(finally_call=change):
        some_function(testing_a)
    assert some_dict['k'] == 2


class TestsHandler(object):
    @staticmethod
    def bad_method():
        raise ValueError("I'm bad")

    def simple_tests(self):
        with Handler():
            self.bad_method()

    def raising_tests(self):
        with pytest.raises(ValueError):
            with Handler(raise_exceptions=True):
                self.bad_method()

    @Handler(raise_exceptions=True)
    def deco_bad(self):
        raise ValueError()

    def deco_tests(self):
        with pytest.raises(ValueError) as e_info:
            self.deco_bad()

    def non_ascii_trace_tests(self):
        logger = get_logger_with_default()
        df = pd.DataFrame([[u'ололо', 1], [u'лалал', 2]], columns=[u'тэкст', 'чесло'])
        parse_dates(df, date_columns=u'тэкст', skip_errors=True, logger=logger)


@pytest.mark.parametrize(
    "date_from,date_to,scale,answer",
    [
        ('2018-01-01', '2018-02-01', 'month', 1),
        ('2018-01-01', '2018-01-08', 'week', 1),
        (['2018-01-01', '2018-01-01'], ['2018-02-01', '2018-01-08'], 'day', [31, 7]),
        (pd.Series(['2018-01-01', '2018-01-01']), pd.Series(['2018-02-01', '2018-01-08']), 'day', pd.Series([31, 7])),
        ('2019-02-01', '2019-03-01', 'month', 1),
        ('2019-03-01', '2019-03-01', 'month', 0),
    ],
)
def diff_scales_tests(date_from, date_to, scale, answer):
    if isinstance(date_from, basestring):
        assert diff_scales(date_from, date_to, scale) == answer
    else:
        assert (diff_scales(date_from, date_to, scale).values == answer).all()


def drop_keys_tests():
    dct = {'a': 1, 'b': [1, 2, 3], 1: 'a'}
    old_dct = dct.copy()
    assert {} == drop_keys(dct, *dct.keys())
    assert old_dct == dct
    assert {'a': 1, 1: 'a'} == drop_keys(dct, 'b')
    assert dct == drop_keys(dct, 'c', 2)
    assert {} == drop_keys({}, 1, 2, 3)


def smart_update_tests():
    old = {1: 'a', 2: 'b', 3: 'c'}
    new = {1: 'd', 2: 3, 4: 'd'}
    result = ({1: 'd', 2: 3, 3: 'c'}, {4: 'd'})
    assert result == smart_update(old, new)
    assert (old, {}) == smart_update(old, {})
    assert ({}, new) == smart_update({}, new)


def check_column_names_in_df_tests():
    df = pd.DataFrame([], columns=['one', 'two', 'three'])

    assert check_column_names_in_df(df, 'one')
    assert check_column_names_in_df(df, u'two')
    assert check_column_names_in_df(df, *[u'two', 'two'])
    assert check_column_names_in_df(df, u'two', 'two')

    with pytest.raises(ValueError):
        check_column_names_in_df(df, 'month')


def get_list_tests():
    assert get_list('text') == ['text']
    assert get_list(None) is None
    assert get_list(None, none_as_empty=True) == []
    assert get_list([1, 2, 3]) == [1, 2, 3]


def change_index_tests():
    df = pd.DataFrame({
        'one': [1, 2, 3],
        'two': [4, 5, 6]
    })

    assert 'one' == change_index(df, 'one').index.name
    assert 'one' == change_index(df, u'one').index.name
    assert 'one' == change_index(df, ['one']).index.name
    assert change_index(df, None).index.name is None
    assert change_index(df, [None]).index.name is None

    df = df.set_index('one')
    df = change_index(df, 'two')
    assert ['one'] == df.columns
    assert 'two' == df.index.name


def change_coding_tests():
    str_norm = ['а', 'и', 'б']
    str_unicode = [u'а', u'и', u'б']
    not_text = [1, 2, 3]
    mixed_norm = ['а', 1, np.nan]
    mixed_unicode = [u'а', 1, np.nan]

    df = pd.DataFrame({
        'str_norm': str_norm,
        'str_unicode': str_unicode,
        'not_text': not_text,
        'mixed_norm': mixed_norm,
        'mixed_unicode': mixed_unicode
    })

    def compare(to_unicode, str_expected, mixed_expected):
        df_norm = change_coding(df, to_unicode=to_unicode)
        assert list(df_norm['str_norm'].values) == str_expected
        assert list(df_norm['str_unicode'].values) == str_expected
        assert list(df_norm['not_text'].values) == not_text
        assert list(df_norm['mixed_norm'].values) == mixed_expected
        assert list(df_norm['mixed_unicode'].values) == mixed_expected

    compare(True, str_unicode, mixed_unicode)
    compare(False, str_norm, mixed_norm)

    change_coding(pd.DataFrame(), True)


def get_sample_tests():
    """
    get_sample(data, dimensions=None, less_dimensions=None, sort=None, index=None, to_unicode=False)
        Фильтрует data_frame по списку значений в dimentions, сортирует
        по колонкам из sort и делает индексом колонки из index
        :param data: исходные данные
        :type data: DataFrame
        :param dimensions: по каким измерениям и значениям отфильтровать данные
            на совпадение значений
        :type dimensions: dict(column: Union(list(values), value))
        :param less_dimensions: по каким измерениям и значениям отфильтровать
            данные с помощью < (строго меньше)
        :type less_dimensions: dict(column: value)
        :param sort: по каким колонкам сортировать (порядок важен!)
        :type sort: Union(str, list)
        :param index: что сделать индексом результирующего датафрейма
        :type index: Union(str, list)
        :return: DataFrame
    """
    pass


def get_sample_week_number_tests():
    """
    get_sample_week_number(data_full, week_number, city=None)
    Срез данных по заданному номеру недели и городу и их сортировка
    по городу (если city is None) и когорте
    """
    pass


def get_sample_week_tests():
    """
    get_sample_week(data_full, week, city=None)
    Срез данных по заданной неделе и городу и их сортировка
    по городу (если city is None) и когорте
    """
    pass


@pytest.mark.parametrize(
    "date, shift, scale, answer",
    [
        ['2019-12-31 00:00:00',1, 'day','2020-01-01 00:00:00'],
        ['2019-12-31 00:00:00',1, 'month','2020-01-31 00:00:00'],
        ['2019-01-31 00:00:00',1, 'month','2019-02-28 00:00:00'],
        ['2019-01-01 00:00:00',12, 'month','2020-01-01 00:00:00'],
        ['2019-01-01 00:00:00',1, 'week','2019-01-08 00:00:00'],
        ['2019-12-26 00:00:00', 1,'week','2020-01-02 00:00:00'],
        ['2019-12-31 12:30:01',1, 'day','2020-01-01 12:30:01'],
        ['2019-12-26 12:30:01', 1,'week','2020-01-02 12:30:01'],
        ['2019-12-26 12:30:01',1, 'month','2020-01-26 12:30:01'],
        ['2019-12-31 12:30:01',1, 'month','2020-01-31 12:30:01'],
        ['2019-01-31 12:30:01',1, 'month','2019-02-28 12:30:01'],
        [['2019-12-31 12:30:01', '2019-12-26 12:30:01'], [1,2], 'day', ['2020-01-01 12:30:01', '2019-12-28 12:30:01']],
        [['2019-12-31 12:30:01', '2019-12-26 12:30:01'], 1, 'day', ['2020-01-01 12:30:01', '2019-12-27 12:30:01']],
    ],
)
def shift_date_tests(date,shift, scale, answer):
    if (not isinstance(date, Iterable)) or (isinstance(date, str)):
        assert shift_date(date, shift,scale, False, '%Y-%m-%d') == pd.to_datetime(answer)
        assert shift_date(date, shift,scale, True, '%Y-%m-%d') == to_start(answer,'day',True)
    else:
        for f1 in (pd.Series, np.array, list):
            if isinstance(shift, Iterable):
                for f2 in (pd.Series, np.array, list):
                    assert (shift_date(f1(date), f2(shift), scale, False, '%Y-%m-%d') == pd.to_datetime(answer)).all()
                    assert (shift_date(f1(date), f2(shift), scale, True, '%Y-%m-%d') == to_start(answer,'day',True)).all()
            else:
                assert (shift_date(f1(date), shift, scale, False, '%Y-%m-%d') == pd.to_datetime(answer)).all()
                assert (shift_date(f1(date), shift, scale, True, '%Y-%m-%d') == to_start(answer,'day',True)).all()


def range_gen(n):
    i = 0
    while i < n:
        yield i
        i += 1


def zip_with_defaults_tests():
    generators = ["x", [6, 0, -3], range_gen(4)]
    result = [v for v in zip_with_defaults(*generators)]
    expected = [('x', 6, 0), ('x', 0, 1), ('x', -3, 2)]
    assert result == expected

    generators = ["x", [6, 0, -3], range_gen(4)]
    result = [v for v in zip_with_defaults(*generators, exclude_iterable_types=())]
    expected = [('x', 6, 0)]
    assert result == expected

    with pytest.raises(ValueError):
        [v for v in zip_with_defaults(1, 2, None)]

    generators = ["x", [6, 0, -3], range_gen(4)]
    result = [v for v in zip_with_defaults(*generators, align=True)]
    expected = [('x', 6, 0), ('x', 0, 1), ('x', -3, 2), ('x', None, 3)]
    assert result == expected


class TestsTaskHandler(object):
    @staticmethod
    def test_function(a=-1, b=None, c="x"):
        return a, b, c

    @staticmethod
    def kwargs_generator(max_pow):
        for power in range(max_pow):
            yield {"b": 2 ** power}

    @staticmethod
    def args_generator(arg_count):
        for i in range(arg_count):
            yield [j ** i for j in range(i)]

    @pytest.fixture(autouse=True, scope='class')
    def manager(self):
        return TaskManager()

    @pytest.fixture(autouse=True, scope='class')
    def n(self):
        return 3

    @staticmethod
    def die_on_three(i):
        if i == 3:
            raise RuntimeError()

    def start_with_return_secondary_kwargs_tests(self, manager, n):
        wrapped_result_expected = [([], 1, 'y'), ([0], 2, 'y'), ([0, 1], 4, 'y')]
        assert wrapped_result_expected == manager.start_with_return(self.test_function,
                                                                    args_generator=self.args_generator(n),
                                                                    kwargs_generator=self.kwargs_generator(n),
                                                                    secondary_kwargs={"c": "y"},
                                                                    sync_if_less=100,
                                                                    wrap_list=True)

    def start_with_return_failing_tests(self, manager, n):
        with pytest.raises(TypeError):
            manager.start_with_return(self.test_function,
                                      args_generator=self.args_generator(n),
                                      kwargs_generator=self.kwargs_generator(n),
                                      secondary_kwargs={"c": "y"},
                                      sync_if_less=100,
                                      wrap_list=False)

    def start_with_return_small_sync_tests(self, manager, n):
        unwrapped_expected = [(0, 1, 'x'), (1, 2, 'x'), (2, 4, 'x')]
        assert unwrapped_expected == manager.start_with_return(self.test_function,
                                                               args_generator=range(n),
                                                               kwargs_generator=self.kwargs_generator(n),
                                                               sync_if_less=1,
                                                               wrap_list=False)

    def start_with_return_no_kwargs_tests(self, manager, n):
        no_kwargs_expected = [(0, None, 'x'), (1, None, 'x'), (2, None, 'x')]
        assert no_kwargs_expected == manager.start_with_return(self.test_function,
                                                               args_generator=range(n),
                                                               sync_if_less=1,
                                                               wrap_list=False)

    def start_with_return_no_args_tests(self, manager, n):
        noargs_expected = [(-1, 1, 'x'), (-1, 2, 'x'), (-1, 4, 'x')]
        assert noargs_expected == manager.start_with_return(self.test_function,
                                                            kwargs_generator=self.kwargs_generator(n),
                                                            sync_if_less=1,
                                                            wrap_list=False)

    def start_with_return_with_secondary_args_tests(self, manager, n):
        noargs_with_secondary = [(8, 1, 'x'), (8, 2, 'x'), (8, 4, 'x')]
        assert noargs_with_secondary == manager.start_with_return(self.test_function,
                                                                  secondary_args=[8],
                                                                  kwargs_generator=self.kwargs_generator(n),
                                                                  sync_if_less=1,
                                                                  wrap_list=False)

    def start_raising_tests(self, manager):
        with pytest.raises(RuntimeError):
            manager.start(self.die_on_three, args_generator=range(8))

    def start_no_raising_tests(self, manager):
        manager.start(self.die_on_three, args_generator=range(8), raise_child_exceptions=False)


def dictalikeobject_tests():
    class A(DictAlikeObject):
        def __init__(self, a=1, b=2):
            self.a = a
            self.b = b
            self._r = 0

        @property
        def c(self):
            return 3

        def foo(self):
            return 3

        @property
        def r(self):
            return self._r

        @r.setter
        def r(self, value):
            self._r = value

    a_obj = A(a=10)
    a_obj.r = 5
    a_copy = a_obj.copy()
    assert a_obj.a == a_copy.a
    assert a_obj._r == a_copy._r

    a_obj.r = []
    a_obj.a = []
    a_deepcopy = deepcopy(a_obj)
    a_deepcopy._r.append(5)
    a_deepcopy.a.append(5)
    assert a_obj.a == []
    assert a_obj._r == []


@pytest.mark.parametrize(
    'file_type, to_frame',
    [(type_, False) for type_ in ['pkl', 'pickle', 'json', '']] +
    [(type_, True) for type_ in ['pkl', 'pickle', 'csv', 'xls', 'xlsx', ''] + (['msg', 'msgpack'] if hasattr(pd, 'read_msgpack') else [])]
)
def d_interact_file_tests(file_type, to_frame, tmpdir):
    data = {'city': [1, 2, 3, 4], 'value': [1, 2, 3, 4]}
    if to_frame:
        data = pd.DataFrame(data)
    filename = str(tmpdir.join("'test_data'"))

    kwargs = {}
    if file_type in ['csv', 'xls', 'xlsx']:
        kwargs = {'index': False}
    full_filename = data_to_file(data, filename, filetype=file_type, **kwargs)

    data_read = data_from_file(filename=full_filename, determine_type=True)

    if isinstance(data, pd.DataFrame):
        assert_frame_equal(data, data_read)
    else:
        assert data == data_read


def data_from_file_general_tests(tmpdir):
    text_file = str(tmpdir.join("SOME.absurd"))

    text = 'Some content'
    with open(text_file, 'w') as f_out:
        f_out.write(text)

    result = data_from_file(text_file, determine_type=True, read_unknown=True)
    assert text == result


@pytest.mark.parametrize(
    "date, scale, answer",
    [
        (pd.to_datetime('2019-05-04 19:45:45'), 'day', '2019-05-04'),
        ('2019-05-04 19:45:45', 'day',  '2019-05-04'),
        (['2019-05-04 19:45:45', '2019-06-04 19:06:45', '2020-05-01 09:25:45'], 'day',
         ['2019-05-04', '2019-06-04', '2020-05-01']),
        (np.array(['2019-05-04 19:45:45', '2019-06-04 19:06:45', '2020-05-01 09:25:45']), 'day',
        ['2019-05-04', '2019-06-04', '2020-05-01']),
        (pd.Series(['2019-05-04 19:45:45', '2019-06-04 19:06:45', '2020-05-01 09:25:45']), 'day',
        ['2019-05-04', '2019-06-04', '2020-05-01'])
    ],
)
def to_start_string_tests(date, scale, answer):
    if (not isinstance(date, Iterable)) or (isinstance(date, str)):
        assert to_start(date, scale, False, '%Y-%m-%d') == pd.to_datetime(answer)
        assert to_start(date, scale, True, '%Y-%m-%d') == answer
        assert to_start(date, scale, True, '%Y-%m-%d-%H') == (answer+'-00')
    else:
        assert (to_start(date, scale, False, '%Y-%m-%d') == pd.to_datetime(answer)).all()
        assert (to_start(date, scale, True, '%Y-%m-%d') == answer).all()


def dict_recursive_update_tests():
    left = {"a": 1, "b": 2, "c": {"d": {"e": 5}}}
    right = {"b": 4, "c": {"d": {"e": 4}, "o": 13}, "f": 15}
    rez = {"a": 1, "b": 4, "c": {"d": {"e": 4}, "o": 13}, "f": 15}
    dict_recursive_update(left, right)
    assert left == rez


def left_first_tests():
    left = pd.DataFrame([['a', 1, 2], ['b', 3, 4], ['c', 5 , 46]], columns=['key', 'value_a', 'value_b'])
    right = pd.DataFrame([['a', 8, 20], ['x', 16, 32]], columns=['key', 'value_a', 'value_c'])

    expected = change_index(pd.DataFrame([['a', 1., 2., 20.], ['b', 3., 4., np.nan],
                             ['c', 5., 46., np.nan], ['x', 16., np.nan, 32.]],
                                         columns=['key', 'value_a', 'value_b', 'value_c']), 'key')

    result = left_first_join(left, right, left_on='key')
    pd.testing.assert_frame_equal(result, expected, check_like=True)

@pytest.mark.parametrize(
    "iterate_dct, return_dct, return_empty, golden",
    [
        [True, False, True, (('some', []), ('value.1.2', 3), ('value.1.inside', []),
                             ('is', {}), ('empty', 5), ('ox.0.1', 2))],
        [False, False, True, (('some', []), ('value', {1: {2: 3, 'inside': []}}),
                             ('is', {}), ('empty', 5), ('ox.0', {1: 2}))],
        [True, True, True, (('value', {1: {2: 3, 'inside': []}}),
                            ('value.1', {2: 3, 'inside': []}),
                            ('ox.0', {1: 2}), ('is', {}))],
        [False, True, True, (('value', {1: {2: 3, 'inside': []}}),
                            ('ox.0', {1: 2}), ('is', {}))],
        [True, False, False, (('value.1.2', 3), ('empty', 5), ('ox.0.1', 2))]
    ],
)
def iterate_values_tests(iterate_dct, return_dct, return_empty, golden):
    dict_convertable = {
        'some': [],
        'value': {1: {2: 3, 'inside': []}},
        'is': {},
        'empty': 5,
        'ox': [{1: 2}]
    }

    not_iterate_types = (pd.DataFrame, ) if iterate_dct else (pd.DataFrame, dict, )
    return_types = dict if return_dct else None
    result = dict(iterate_values(dict_convertable, not_iterate_types=not_iterate_types,
                                      return_types=return_types, return_empty=return_empty))
    golden = dict(golden)
    for k in set(golden.keys()) | set(result.keys()):
        assert result.get(k) == golden.get(k), \
            '{}: result "{}" != "{}" golden'.format(k, result.get(k), golden.get(k))


class ObjectWithDict:
    def __init__(self, extend=False, replace=False):
        self.array = np.array([1, 2, 3])
        self.array_and_int = [1, np.array([1, 2, 3])]
        self.string = 'some_str'
        if extend:
            self.new_key = 'WoW'

        if replace:
            self.string = 'str_some'
            self.array = np.array([3, 2, 1])


class TestsDeepCompare():
    testing_iterables = [[1, 2],
                         [[1, 2]],
                         [np.array([1, 2])],
                         [(1, 2)],
                         [{0: [1, 2]}],
                         [pd.Series([1, 2])],
                         [pd.DataFrame([[1, 2], [3, 4]])],
                         {0: 1},
                         {0: [1, 2]},
                         {0: (1, 2)},
                         {0: np.array([1, 2])},
                         {0: {0: 1}},
                         pd.Series([1, 2]),
                         pd.DataFrame([[1, 2], [3, 4]]),
                         np.array([1, 2]),
                         ['some_str']]

    testing_iterables_with_extra_keys = [[1, 2, 3],
                                         [[1, 2, 3]],
                                         [np.array([1, 2, 3])],
                                         [(1, 2), 3],
                                         [{0: [1, 2], 1: 3}],
                                         [pd.Series([1, 2, 3])],
                                         [pd.DataFrame([[1, 2, 3], [3, 4, 5]])],
                                         {0: 1, 1: 2},
                                         {0: [1, 2, 3]},
                                         {0: (1, 2, 3)},
                                         {0: np.array([1, 2, 3])},
                                         {0: {0: 1, 1: 2}},
                                         pd.Series([1, 2, 3]),
                                         pd.DataFrame([[1, 2, 3], [3, 4, 5]]),
                                         np.array([1, 2, 3]),
                                         ['some_str', 'str']]

    testing_iterables_with_replaced_values = [[1, 3],
                                              [[2, 2]],
                                              [np.array([2, 2])],
                                              [(2, 2)], [{0: [2, 2]}],
                                              [pd.Series([2, 2])],
                                              [pd.DataFrame([[1, 3], [3, 4]])],
                                              {0: 2},
                                              {0: [3, 2]}, {0: (1, 3)},
                                              {0: np.array([2, 2])},
                                              {0: {0: 2}},
                                              pd.Series([4, 2]),
                                              pd.DataFrame([[4, 2], [3, 4]]),
                                              np.array([1, 4]),
                                              ['str_some']]

    def class_consistency_tests(self):
        message = 'class TestsDeepCompare inconsistent!'
        assert len(self.testing_iterables) == len(self.testing_iterables_with_extra_keys), message
        assert len(self.testing_iterables) == len(self.testing_iterables_with_replaced_values), message

    @pytest.mark.parametrize(
        'iterable',
        testing_iterables
    )
    def self_compare_tests(self, iterable):
        deep_compare(iterable, iterable)

    @pytest.mark.parametrize(
        'iterable, golden',
        [[[1, 2, 3], (1, 2, 3)],
         [["abracadabra"], [u"abracadabra"]]]
    )
    def equal_types_tests(self, iterable, golden):
        deep_compare(iterable, golden)

    @pytest.mark.parametrize(
        'iterable, golden',
        [
            [[1, 2, 3], [3, 2, 1]],
            [[[1, 2, 3]], [[3, 2, 1]]],  # теперь на бОльшем уровне вложенности
        ]
    )
    def ordered_fail_tests(self, iterable, golden):
        with pytest.raises(ValueError):
            deep_compare(iterable, golden, ordered=True)

    @pytest.mark.parametrize(
        'iterable',
        [
            [ObjectWithDict()],
            [[1, np.array([1, 2, 3])]],
        ]
    )
    def ordered_tests(self, iterable):
        deep_compare(iterable, iterable, ordered=True)

    @pytest.mark.parametrize(
        'iterable, golden',
        [[[1, 2, 3], [3, 2, 1]],
         [[[1, 2, 3]], [[3, 2, 1]]]]
    )
    def not_ordered_tests(self, iterable, golden):
        deep_compare(iterable, golden, ordered=False)

    @staticmethod
    def validate_message(deep_compare_result, golden_message):
        for key in deep_compare_result:
            assert deep_compare_result[key].startswith(golden_message), 'Error in path "{}"'.format(key)

    @pytest.mark.parametrize(
        'iterable, golden',
        list(zip(testing_iterables, testing_iterables_with_extra_keys))
    )
    def key_not_found_tests(self, iterable, golden):
        with pytest.raises(ValueError):
            deep_compare(iterable, golden, ordered=True)
        errors = deep_compare(iterable, golden, with_return=True, ordered=True)
        self.validate_message(errors, 'Key not found in')

    @pytest.mark.parametrize(
        'iterable, golden',
        list(zip(testing_iterables, testing_iterables_with_replaced_values))
    )
    def wrong_value_tests(self, iterable, golden):
        with pytest.raises(ValueError):
            deep_compare(iterable, golden)
        errors = deep_compare(iterable, golden, with_return=True)
        self.validate_message(errors, 'Wrong value passed')

    @pytest.mark.parametrize(
        'iterable, golden',
        [[[1, 2, 3], {u'0': 1, u'1': 2, u'2': 3}],
         [{'a': {u'0': 1}}, {'a': [1]}]]
    )
    def wrong_type_tests(self, iterable, golden):
        with pytest.raises(ValueError):
            deep_compare(iterable, golden)
        errors = deep_compare(iterable, golden, with_return=True)
        self.validate_message(errors, 'Wrong type passed')

    @pytest.mark.parametrize(
        'iterable',
        testing_iterables
    )
    def copy_tests(self, iterable):
        a = deepcopy(iterable)
        b = deepcopy(iterable)
        deep_compare(a, b, validate_copy=True)

    @pytest.mark.parametrize(
        'iterable',
        testing_iterables
    )
    def copy_fail_tests(self, iterable):
        a = deepcopy(iterable)
        b = a
        with pytest.raises(ValueError):
            deep_compare(a, b, validate_copy=True)
        errors = deep_compare(a,b, validate_copy=True, with_return=True)
        self.validate_message(errors, 'Value was not copied')


@pytest.mark.parametrize(
    "dates, scale, base_scale, golden",
    [
        [['2020-01-02', '2020-02-15'], 'day', 'month', ('2020-01-01', '2020-02-29')],
        [['2020-01-02', '2020-02-15'], 'day', 'week', ('2019-12-30', '2020-02-16')],
        [['2020-01-02', '2020-02-15'], 'week', 'month', ('2019-12-30', '2020-02-24')],
        [['2020-01-02', '2020-02-15'], 'week', None, ('2019-12-30', '2020-02-10')],
        [['2020-01-02', '2020-02-15'], 'month', None, ('2020-01-01', '2020-02-01')]
    ]
)
def get_full_borders_tests(dates, scale, base_scale, golden):
    assert get_full_date_borders(dates, scale, base_scale) == tuple(pd.Timestamp(x) for x in golden)


def init_config_holder_tests():
    """ConfigHolder при создании любит уходить в бесконечную рекурсию. Надо аккуратно вносить
    даже минорные правки"""
    ConfigHolder()
    ConfigHolder(yav_secret_ids='sec-dksfhhfsknm')

