import inspect
from datetime import timedelta
from time import sleep

import pytest

from dmp_suite import datetime_utils as dtu, scales
from dmp_suite.task.args import (
    use_arg,
    func,
    use_datetime_arg,
    use_period_arg,
    const_arg,
    const_datetime_arg,
    const_period_arg,
    utcnow_arg,
    msknow_arg,
    ArgumentNotFoundError)


class InnerData:
    attr1 = 'foo'
    attr2 = 'bar'
    map = {
        'okey1': 'ovalue1',
        'okey2': 'ovalue2'
    }


class UseArgsData:
    map = {
        'key1': 'value1',
        'key2': 'value2',
        'obj': InnerData(),
        'inner_map': {'subkey1': 'subvalue1'}
    }
    list = ['list1', {'lkey1': 'lvalue'}, ['sublist1', 'sublist2']]

    attr1 = 'attr'
    obj = InnerData()


@pytest.mark.parametrize('path, expected', [
    ('attr1', 'attr'),
    ('list.0', 'list1'),
    ('list.2.1', 'sublist2'),
    ('map.key1', 'value1'),
    ('map.obj.attr2', 'bar'),
    ('map.inner_map.subkey1', 'subvalue1'),
    ('obj.attr1', 'foo'),
    ('obj.map.okey1', 'ovalue1'),
])
def test_use_arg_extract_by_path(path, expected):
    assert use_arg(path).get_value(UseArgsData, None) == expected


@pytest.mark.parametrize('path', [
    'attr99', 'list.99', 'obj.attr99', 'map.key99'
])
def test_use_arg_exception(path):
    with pytest.raises(ArgumentNotFoundError):
        use_arg(path).get_value(UseArgsData, None)


def test_use_arg_transform():
    args = dict(s='arg')
    arg = use_arg('s')
    arg_t1 = arg.transform(lambda s: s + '_t1')
    assert arg.get_value(args, None) == 'arg'
    assert arg_t1.get_value(args, None) == 'arg_t1'
    arg_t2 = arg_t1.transform(lambda s: s + '_t2')
    assert arg.get_value(args, None) == 'arg'
    assert arg_t1.get_value(args, None) == 'arg_t1'
    assert arg_t2.get_value(args, None) == 'arg_t1_t2'


def test_use_arg_converter_and_transform():
    args = dict(s='arg')
    arg = use_arg('s', lambda s: s + '_c')
    assert arg.get_value(args, None) == 'arg_c'
    assert arg.transform(lambda s: s + '_t').get_value(args, None) == 'arg_c_t'
    assert arg.get_value(args, None) == 'arg_c'


def test_use_datetime_arg_transform_datetime():
    args = dict(d=dtu.parse_datetime('2020-01-01 00:00:00'))
    arg = (
        use_datetime_arg('d')
        .transform_datetime(lambda d: d.replace(hour=10))
        .transform_datetime(lambda d: d.replace(day=10))
        .format_datetime()
    )
    assert arg.get_value(args, None) == '2020-01-10 10:00:00'


def test_use_datetime_arg_shift():
    args = dict(d=dtu.parse_datetime('2020-01-01 00:00:00'))
    arg = (
        use_datetime_arg('d')
        .offset(hours=10, days=9)
        .format_datetime()
    )
    assert arg.get_value(args, None) == '2020-01-10 10:00:00'


def test_use_datetime_arg_formats():
    date = dtu.parse_datetime('2020-01-01 00:00:00')
    args = dict(d=date)
    arg = use_datetime_arg('d')
    formats = inspect.getmembers(
        arg,
        lambda attr: callable(attr) and attr.__name__.startswith('format'),
    )
    for name, arg_format in formats:
        utils_format = getattr(dtu, name)
        assert arg_format().get_value(args, None) == utils_format(date)
    assert arg.get_value(args, None) == date


@pytest.mark.parametrize('scale', scales.all_scales())
def test_use_datetime_arg_round(scale):
    date = dtu.parse_datetime('2019-12-31 00:00:00')
    args = dict(d=date)
    shift_params = dict(days=1, hours=10)
    arg = use_datetime_arg('d').offset(**shift_params)
    actual = arg.round_down(scale).get_value(args, None)
    expected = scale.extract_start(date + timedelta(**shift_params))
    assert actual == expected
    actual = arg.round_up(scale).get_value(args, None)
    expected = scale.extract_end(date + timedelta(**shift_params))
    assert actual == expected


def test_use_period_arg_init():
    period = dtu.period('2020-01-01', '2020-01-02')
    args = dict(period=period)
    assert use_period_arg().get_value(args, None) == period

    args = dict(some_period=period)

    with pytest.raises(ArgumentNotFoundError):
        use_period_arg().get_value(args, None)

    assert use_period_arg('some_period').get_value(args, None) == period


@pytest.mark.parametrize('scale', scales.all_scales())
def test_use_period_arg_extend(scale):
    period = dtu.period('2020-01-01', '2020-01-02')
    args = dict(period=period)
    arg = use_period_arg().extend(scale)
    assert arg.get_value(args, None) == scale.extend_period(period)


def test_use_period_arg_offset():
    period = dtu.period('2020-01-01', '2020-01-02')
    args = dict(period=period)
    shift_params = dict(days=1, hours=10)
    arg = use_period_arg().offset(**shift_params)
    assert arg.get_value(args, None) == period.add_offset(timedelta(**shift_params))


@pytest.mark.parametrize('offset', [None, dict(days=1, hours=10)])
def test_use_period_arg_start_end(offset):
    arg = use_period_arg()
    if offset:
        arg = arg.offset(**offset)
    start = '2020-01-01'
    end = '2020-01-02'
    period = dtu.period(start, end)
    args = dict(period=period)
    if offset:
        period = period.add_offset(**offset)

    def check(arg, expected):
        assert arg.get_value(args, None) == expected

    check(arg.start, period.start)
    check(arg.start.format_date(), dtu.format_date(period.start))
    check(arg.end.format_date(), dtu.format_date(period.end))
    check(arg.end, period.end)
    check(arg, period)


def test_const_arg():
    arg = const_arg(1)
    assert arg.get_value(None, None) == 1
    assert arg.get_value(dict(a=10), None) == 1
    assert arg.transform(lambda i: i + 10).get_value(None, None) == 11
    assert arg.get_value(None, None) == 1


def test_const_datetime_arg_incorrect_date():
    with pytest.raises(ValueError):
        arg = const_datetime_arg('sadf')


@pytest.mark.parametrize('date, expected', [
    ('2020-01-01', '2020-01-01'),
    (dtu.parse_datetime('2020-01-01'), '2020-01-01'),
])
def test_const_datetime_arg(date, expected):
    arg = const_datetime_arg(date)
    assert arg.format_date().get_value(None, None) == expected


def test_const_period_arg_incorrect_date():
    with pytest.raises(ValueError):
        arg = const_period_arg(start='sadf', end='sadf')


@pytest.mark.parametrize('period, expected', [
    (
        dict(start='2020-01-01', end='2020-01-02'),
        dtu.period('2020-01-01', '2020-01-02'),
    ),
    (
        dict(value=dtu.period('2020-01-01', '2020-01-02')),
        dtu.period('2020-01-01', '2020-01-02'),
    ),
])
def test_const_period_arg(period, expected):
    arg = const_period_arg(**period)
    assert arg.get_value(None, None) == expected
    assert arg.start.get_value(None, None) == expected.start
    assert arg.end.get_value(None, None) == expected.end


def test_func_no_args():
    assert func(lambda: 1).get_value(UseArgsData, None) == 1


@pytest.mark.parametrize('args, kwargs, expected', [
    (['hello', 'world'], dict(), 'hello world'),
    (['hello'], dict(p2='world'), 'hello world'),
    ([], dict(p1='hello', p2='world'), 'hello world'),
    (['hello', use_arg('attr1')], dict(), 'hello attr'),
    (['hello'], dict(p2=use_arg('attr1')), 'hello attr'),
    ([], dict(p1=use_arg('map.key1'), p2=use_arg('attr1')), 'value1 attr'),
])
def test_func_args(args, kwargs, expected):
    def concat(p1, p2):
        return str(p1) + ' ' + str(p2)

    assert func(concat, *args, **kwargs).get_value(UseArgsData, None) == expected


@pytest.mark.parametrize('arg_cls', [
    utcnow_arg,
    msknow_arg,
])
def test_runtime_datetime_arg(arg_cls):
    arg = arg_cls()
    first = arg.get_value(None, None)
    sleep(0.001)
    second = arg.get_value(None, None)
    assert first is second

    arg = arg_cls()
    first = arg.get_value(None, None)
    sleep(0.001)
    second = arg.format_datetime_microseconds().get_value(None, None)
    assert dtu.format_datetime_microseconds(first) == second

    arg = arg_cls(cache_result=False)
    first = arg.get_value(None, None)
    sleep(0.001)
    second = arg.get_value(None, None)
    assert first != second

    arg = arg_cls(cache_result=False)
    first = arg.get_value(None, None)
    sleep(0.001)
    second = arg.format_datetime_microseconds().get_value(None, None)
    assert dtu.format_datetime_microseconds(first) != second
