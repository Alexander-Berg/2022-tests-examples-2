from __future__ import absolute_import, division, print_function

import pytest

import pickle
import six
import time

from sandbox.projects.yabs.sandbox_task_tracing.util import (
    coalesce,
    decorator_function,
    frozendict,
    microseconds_from_utc_iso,
    pairwise,
    time_microseconds,
)


# Truth values of all items below are False # to make sure
# `coalesce` does not return the first true value.
TAG1 = ()
TAG2 = ()
TAG3 = ()


@pytest.mark.parametrize(
    ('args', 'expected'),
    [
        ([], None),
        ([None], None),
        ([TAG1], TAG1),
        ([None, None], None),
        ([TAG1, None], TAG1),
        ([None, TAG2], TAG2),
        ([TAG1, TAG2], TAG1),
        ([None, None, None], None),
        ([None, None, TAG3], TAG3),
        ([TAG1, None, TAG3], TAG1),
    ],
    ids=repr,
)
def test_coalesce(args, expected):
    assert coalesce(*args) is expected


# the following must have global scope to be picklable

@decorator_function
def decorator_function_name(decorator_function_argument='default'):
    def decorator(function):
        def wrapper(*args, **kwargs):
            return (decorator_function_argument, function(*args, **kwargs))
        return wrapper
    return decorator


@decorator_function_name
def decorated_function_direct(argument):
    return argument


@decorator_function_name()
def decorated_function_empty(argument):
    return argument


@decorator_function_name('positional')
def decorated_function_positional(argument):
    return argument


@decorator_function_name(decorator_function_argument='keyword')
def decorated_function_keyword(argument):
    return argument


@pytest.mark.parametrize('decorator_function_arguments_type', ['direct', 'empty', 'positional', 'keyword'])
@pytest.mark.parametrize('after_pickle', [False, True])
def test_decorator_function_without_arguments(decorator_function_arguments_type, after_pickle):
    function, argument_value = {
        'direct': (decorated_function_direct, 'default'),
        'empty': (decorated_function_empty, 'default'),
        'keyword': (decorated_function_keyword, 'keyword'),
        'positional': (decorated_function_positional, 'positional'),
    }[decorator_function_arguments_type]

    if after_pickle:
        function = pickle.loads(pickle.dumps(function))

    inner_function_name = 'decorated_function_{}'.format(decorator_function_arguments_type)
    assert function.__name__ == inner_function_name
    assert function._wrapped.__name__ == inner_function_name
    assert function(1) == (argument_value, 1)
    assert function(argument=1) == (argument_value, 1)


@pytest.mark.parametrize('init_args', [[], [{}], [{'existing_key': 'value'}]], ids=repr)
class TestFrozendictGeneralAccess(object):

    def test_len(self, init_args):
        sut = frozendict(*init_args)
        control = dict(*init_args)
        assert len(sut) == len(control)

    def test_iter(self, init_args):
        sut = frozendict(*init_args)
        control = dict(*init_args)
        assert tuple(iter(sut)) == tuple(iter(control))

    @pytest.mark.parametrize(
        'six_method_name', [
            'iteritems',
            'iterkeys',
            'itervalues',
            'viewitems',
            'viewkeys',
            'viewvalues',
        ],
        ids=repr,
    )
    def test_six_iterating_methods(self, init_args, six_method_name):
        sut = frozendict(*init_args)
        control = dict(*init_args)
        six_method = getattr(six, six_method_name)
        assert tuple(six_method(sut)) == tuple(six_method(control))

    def test_clear(self, init_args):
        sut = frozendict(*init_args)
        with pytest.raises(TypeError):
            sut.clear()

    def test_popitem(self, init_args):
        sut = frozendict(*init_args)
        with pytest.raises(TypeError):
            sut.popitem()

    def test_repr(self, init_args):
        sut = frozendict(*init_args)
        control = dict(*init_args)
        assert repr(sut) != repr(control)


@pytest.mark.parametrize(
    ('init_args', 'key'),
    [
        ([], 'new_key'),
        ([{}], 'new_key'),
        ([{'old_key': 'value'}], 'old_key'),
        ([{'old_key': 'value'}], 'new_key'),
    ],
    ids=repr,
)
class TestFrozendictKeyedAccess(object):

    @classmethod
    def make_other(self, key, other_type, value='new_value'):
        result = ((key, value),)
        if other_type == 'iterable':
            pass
        elif other_type == 'dict':
            result = dict(result)
        elif other_type in ('frozendict', 'kwargs'):
            result = frozendict(result)
        else:
            raise ValueError('Unsupported other_type: {}'.format(other_type))
        return result

    def test_getitem(self, init_args, key):
        sut = frozendict(*init_args)
        control = dict(*init_args)
        if key in control:
            assert sut[key] == control[key]
        else:
            with pytest.raises(KeyError):
                assert sut[key] == 'missing'
            with pytest.raises(KeyError):
                assert control[key] == 'missing'

    def test_setitem(self, init_args, key):
        sut = frozendict(*init_args)
        with pytest.raises(TypeError):
            sut[key] = 'new_value'

    def test_delitem(self, init_args, key):
        sut = frozendict(*init_args)
        with pytest.raises(TypeError):
            del sut[key]

    def test_contains(self, init_args, key):
        sut = frozendict(*init_args)
        control = dict(*init_args)
        assert (key in sut) == (key in control)

    def test_get(self, init_args, key):
        sut = frozendict(*init_args)
        control = dict(*init_args)
        assert sut.get(key, 'default') == control.get(key, 'default')

    def test_pop(self, init_args, key):
        sut = frozendict(*init_args)
        with pytest.raises(TypeError):
            sut.pop(key, 'default')

    def test_setdefault(self, init_args, key):
        sut = frozendict(*init_args)
        with pytest.raises(TypeError):
            sut.setdefault(key, 'new_value')

    @pytest.mark.parametrize('other_type', ('iterable', 'dict', 'frozendict', 'kwargs'))
    def test_update(self, init_args, key, other_type):
        sut = frozendict(*init_args)
        other = self.make_other(key, other_type)
        with pytest.raises(TypeError):
            if other_type == 'kwargs':
                sut.update(**other)
            else:
                sut.update(other)

    @pytest.mark.parametrize('other_type', ('iterable', 'dict', 'frozendict', 'kwargs'))
    def test_ior(self, init_args, key, other_type):
        sut = frozendict(*init_args)
        other = self.make_other(key, other_type)
        with pytest.raises(TypeError):
            sut |= other

    @pytest.mark.parametrize('other_type', ('iterable', 'dict', 'frozendict'))
    def test_add(self, init_args, key, other_type):
        sut = frozendict(*init_args)
        other = self.make_other(key, other_type)
        result = sut + other
        assert sut == frozendict(*init_args)
        assert other == self.make_other(key, other_type)
        assert isinstance(result, frozendict)
        assert result is not sut
        assert result is not other
        assert result[key] == 'new_value'
        if key != 'old_key':
            assert result.get('old_key') == sut.get('old_key')

    @pytest.mark.parametrize('other_type', ('iterable', 'dict', 'frozendict'))
    def test_radd(self, init_args, key, other_type):
        sut = frozendict(*init_args)
        other = self.make_other(key, other_type)
        result = other + sut
        assert sut == frozendict(*init_args)
        assert other == self.make_other(key, other_type)
        assert isinstance(result, frozendict)
        assert result is not sut
        assert result is not other
        assert result.get('old_key') == sut.get('old_key')
        if key != 'old_key':
            assert result[key] == 'new_value'

    @pytest.mark.parametrize('other_type', ('iterable', 'dict', 'frozendict', 'kwargs'))
    def test_updated(self, init_args, key, other_type):
        sut = frozendict(*init_args)
        other = self.make_other(key, other_type)
        if other_type == 'kwargs':
            result = sut.updated(**other)
        else:
            result = sut.updated(other)
        assert sut == frozendict(*init_args)
        assert other == self.make_other(key, other_type)
        assert isinstance(result, frozendict)
        assert result is not sut
        assert result is not other
        assert result[key] == 'new_value'
        if key != 'old_key':
            assert result.get('old_key') == sut.get('old_key')

    @pytest.mark.parametrize('other_type', ('iterable', 'dict', 'frozendict'))
    def test_updated_kwargs_priority(self, init_args, key, other_type):
        sut = frozendict(*init_args)
        arg_other = self.make_other(key, other_type, value='arg_value')
        kwargs_other = self.make_other(key, 'kwargs', value='kwargs_value')
        result = sut.updated(arg_other, **kwargs_other)
        assert sut == frozendict(*init_args)
        assert arg_other == self.make_other(key, other_type, value='arg_value')
        assert kwargs_other == self.make_other(key, 'kwargs', value='kwargs_value')
        assert isinstance(result, frozendict)
        assert result is not sut
        assert result is not arg_other
        assert result is not kwargs_other
        assert result[key] == 'kwargs_value'
        if key != 'old_key':
            assert result.get('old_key') == sut.get('old_key')


@pytest.mark.parametrize('time_separator', [' ', 'T'])
def test_microseconds_from_utc_iso_whole(time_separator):
    text = '2022-02-28{}12:35:12Z'.format(time_separator)
    parsed_value = microseconds_from_utc_iso(text)
    assert parsed_value == 1646051712 * 10**6


@pytest.mark.parametrize('time_separator', [' ', 'T'])
@pytest.mark.parametrize('decimal_separator', ['.', ','])
@pytest.mark.parametrize('precision', list(range(10)))
def test_microseconds_from_utc_iso_fractional(time_separator, decimal_separator, precision):
    text = '2022-02-28{}12:35:12{}{}Z'.format(time_separator, decimal_separator, '123456789'[:precision])
    parsed_value = microseconds_from_utc_iso(text)
    assert parsed_value == 1646051712123456 - 123456 % 10**max(6-precision, 0)


def test_pairwise_small_examples():
    assert list(pairwise([])) == []
    assert list(pairwise([1])) == []
    assert list(pairwise([1, 2])) == [(1, 2)]
    assert list(pairwise([1, 2, 3])) == [(1, 2), (2, 3)]


def test_pairwise_return_type():
    result = pairwise([1, 2])
    # make sure result is iterable, not container
    assert not isinstance(result, (list, tuple))
    assert next(result)


def test_time_microseconds():
    result1 = time_microseconds()
    time.sleep(0.01)
    result2 = time_microseconds()
    assert 1646051712E6 < result1 < 1646051712E7
    assert 1E3 < result2 - result1 < 1E6
