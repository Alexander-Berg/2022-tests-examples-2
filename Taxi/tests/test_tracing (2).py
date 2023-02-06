from typing import Callable
from typing import List
from typing import Union

from util.swaggen import tracing


TEST_DICT_SIMPLE = {
    'hello': {'world': 1, 'hello': 1},
    'hello_2': {'world': 2},
    'hi': {'there': 2},
    'goto': {'is bad': 3},
    'London': {'is a capital of Great Britain': 4},
}


TEST_LIST_SAMPLE = [1, 2.3, 'test', [1, 'test'], {'hello': 'world'}]


def assert_raise(func: Callable) -> tracing.TracingException:
    try:
        func()
    except tracing.TracingException as exc:
        return exc

    raise AssertionError('Function have to raise an TracingException')


def test_empty_tracing_dict():
    empty = tracing.TracingDict('empty_tracing_dict', {})
    assert empty.filename() == 'empty_tracing_dict'
    assert empty.path() == ''


def test_simple_tracing_dict():
    native_dict = {
        'hello': 'world',
        'hi': 'there',
        'goto': 'is bad',
        'London': 'is a capital of Great Britain',
    }

    trace_dict = tracing.TracingDict('simple_tracing_dict', native_dict)
    for key, value in native_dict.items():
        assert trace_dict.strict_get_str(key) == value


def test_tracing_dict_str():
    trace_dict = tracing.TracingDict('str', TEST_DICT_SIMPLE.copy())
    assert str(trace_dict) == str(TEST_DICT_SIMPLE)


def test_tracing_dict_keys():
    trace_dict = tracing.TracingDict('keys', TEST_DICT_SIMPLE.copy())
    assert set(trace_dict.keys()) == set(TEST_DICT_SIMPLE.keys())


def test_tracing_dict_values():
    trace_dict = tracing.TracingDict('values', TEST_DICT_SIMPLE.copy())
    assert list(trace_dict.strict_values_any()) == list(
        TEST_DICT_SIMPLE.values(),
    )


def test_tracing_dict_values_invalid():
    trace_dict = tracing.TracingDict('values_t', TEST_DICT_SIMPLE.copy())
    assert_raise(lambda: list(trace_dict.strict_values_int()))
    assert_raise(lambda: list(trace_dict.strict_values_float()))
    assert_raise(lambda: list(trace_dict.strict_values_str()))
    assert_raise(lambda: list(trace_dict.strict_values_list()))
    assert_raise(lambda: list(trace_dict.strict_values_bool()))
    assert_raise(lambda: list(trace_dict.strict_values_t(types=bool)))


def test_tracing_dict_items():
    trace_dict = tracing.TracingDict('items', TEST_DICT_SIMPLE.copy())
    assert list(trace_dict.strict_items_any()) == list(
        TEST_DICT_SIMPLE.items(),
    )


def test_tracing_dict_missing_key():
    def _get(_src: tracing.TracingDict, *_keys: str) -> tracing.TracingDict:
        for _key in _keys:
            _src = _src.strict_get_dict(_key)
        return _src

    trace_dict = tracing.TracingDict('missing_key', TEST_DICT_SIMPLE.copy())
    try:
        _get(trace_dict, 'London', 'does not exist')
        assert False
    except tracing.TracingException as exc:
        assert 'missing_key' in str(exc)
        assert 'London' in str(exc)


def test_tracing_dict_contains():
    trace_dict = tracing.TracingDict('contains', TEST_DICT_SIMPLE.copy())
    assert 'London' in trace_dict
    assert 'goto' in trace_dict
    assert 'something that does not exist' not in trace_dict


def test_tracing_dict_iteration():
    def _get(_src: tracing.TracingDict, *_keys: str) -> tracing.TracingDict:
        for _key in _keys:
            _src = _src.strict_get_dict(_key)
        return _src

    trace_dict = tracing.TracingDict('iteration', TEST_DICT_SIMPLE.copy())
    for key, value in TEST_DICT_SIMPLE.items():
        assert _get(trace_dict, key).filename() == 'iteration'
        assert _get(trace_dict, key).path() == key
        assert _get(trace_dict, key) == value

    assert len(trace_dict) == len(TEST_DICT_SIMPLE)


def test_tracing_dict_get_with_default():
    def _get(_src: tracing.TracingDict, *_keys: str) -> tracing.TracingDict:
        for _key in _keys:
            _src = _src.strict_get_dict(_key)
        return _src

    trace_dict = tracing.TracingDict(
        'get_with_default', TEST_DICT_SIMPLE.copy(),
    )

    value = _get(trace_dict, 'London').strict_get_dict(
        'does not exist', {'after': {'Brexit': 6}},
    )
    assert value.path() == 'London.does not exist'
    assert _get(value, 'after').path() == 'London.does not exist.after'
    assert _get(value, 'after').filename() == 'get_with_default'
    assert 'Brexit' in _get(value, 'after')
    assert _get(value, 'after').strict_get_int('Brexit') == 6


def test_tracing_dict_update():
    def _get(_src: tracing.TracingDict, *_keys: str) -> tracing.TracingDict:
        for _key in _keys:
            _src = _src.strict_get_dict(_key)
        return _src

    trace_dict = tracing.TracingDict('update', TEST_DICT_SIMPLE.copy())
    trace_dict.update({'hello': 'world', 'goto': {'bad': {'after': 'all'}}})
    assert trace_dict.strict_get_str('hello') == 'world'

    _get(trace_dict, 'goto', 'bad').update({'after': 'Basic'})
    assert _get(trace_dict, 'goto', 'bad').path() == 'goto.bad'
    assert _get(trace_dict, 'goto', 'bad').filename() == 'update'
    assert _get(trace_dict, 'goto', 'bad').strict_get_str('after') == 'Basic'


def test_tracing_dict_copy_and_del():
    def _get(_src: tracing.TracingDict, _first: str, _second: str) -> int:
        return _src.strict_get_dict(_first).strict_get_int(_second)

    trace_dict = tracing.TracingDict('copy_and_del', TEST_DICT_SIMPLE.copy())
    trace_dict_copy = trace_dict.copy()

    assert 'hello' in trace_dict
    assert _get(trace_dict, 'hello', 'world') == 1
    assert 'hello' in trace_dict_copy
    assert _get(trace_dict_copy, 'hello', 'world') == 1

    del trace_dict_copy['hello']

    assert 'hello' in trace_dict
    assert _get(trace_dict, 'hello', 'world') == 1
    assert 'hello' not in trace_dict_copy


def test_empty_tracing_complex_path():
    def _get(
            _src: Union[tracing.TracingDict, tracing.TracingList],
            *_keys: Union[str, int],
    ) -> Union[tracing.TracingDict, tracing.TracingList]:
        for _key in _keys:
            if isinstance(_src, tracing.TracingDict):
                assert isinstance(_key, str), (
                    'TracingDict param "key" must be of type "str"',
                )
                _src = _src.strict_get_t((dict, list), _key)
            else:
                assert isinstance(
                    _key, int,
                ), 'TracingList param "index" must be of type "int"'
                _src = _src[_key]

        return _src

    native_dict = {
        'test1': 'foo',
        'The': [
            {'item': {'zero': 0}},
            {'items': {'in this': {'dict': [0, 1, 2, 3, 4, 5, 6]}}},
        ],
        'test2': 'string',
    }
    trace_dict = tracing.TracingDict('complex_path', native_dict)

    # Simple access
    nested = _get(trace_dict, 'The', 1, 'items', 'in this')
    assert nested.path() == 'The.1.items.in this'
    assert nested.filename() == 'complex_path'

    # Iterations
    nested = None
    for lvl1 in trace_dict:
        for lvl2 in trace_dict.strict_get_any(lvl1):
            if 'items' in lvl2:
                nested = _get(lvl2, 'items', 'in this')
    assert nested.path() == 'The.1.items.in this'
    assert nested.filename() == 'complex_path'
    assert _get(nested, 'dict', 3) == 3

    # Missing list element
    try:
        _get(nested, 'dict', 100)
        assert False
    except tracing.TracingException as exc:
        assert 'The.1.items.in this.dict' in str(exc)
        assert 'complex_path' in str(exc)


def test_tracing_seq_addition_and_comparisons():
    native_seq = [0, 1, 2]
    trace_seq = tracing.TracingList('seq_addition_and_comparisons', native_seq)

    assert trace_seq + [3, 4] == [0, 1, 2, 3, 4]
    assert trace_seq + trace_seq == [0, 1, 2, 0, 1, 2]

    trace_seq += [3, 4]
    assert trace_seq == [0, 1, 2, 3, 4]


def test_tracing_guard():
    trace_dict = tracing.TracingDict('tracing_guard', TEST_DICT_SIMPLE.copy())
    try:
        with tracing.tracing_guard(trace_dict.strict_get_dict('London')):
            raise Exception('Testing exceptions')
    except tracing.TracingException as exc:
        assert 'tracing_guard' in str(exc)
        assert 'London' in str(exc)
    except Exception:  # pylint: disable=broad-except
        assert False


def test_typed_get_ok():
    trace_dict = tracing.TracingDict('tracing_guard', TEST_DICT_SIMPLE.copy())
    hello = trace_dict.strict_get_dict('hello')
    hello.strict_get_int('world')


def test_typed_items_ok():
    trace_dict = tracing.TracingDict('tracing_guard', TEST_DICT_SIMPLE.copy())
    for _, i in trace_dict.strict_items_dict():
        for _, _ in i.strict_items_int():
            pass


def test_typed_items_invalid():
    trace_dict = tracing.TracingDict('tracing_guard', TEST_DICT_SIMPLE.copy())
    assert_raise(lambda: [i for i in trace_dict.strict_items_float()])
    assert_raise(lambda: [i for i in trace_dict.strict_items_int()])
    assert_raise(lambda: [i for i in trace_dict.strict_items_str()])
    assert_raise(lambda: [i for i in trace_dict.strict_items_list()])
    assert_raise(lambda: [i for i in trace_dict.strict_items_bool()])


def test_typed_get_invalid():
    trace_dict = tracing.TracingDict('tracing_guard', TEST_DICT_SIMPLE.copy())
    hello = trace_dict.strict_get_dict('hello')

    assert_raise(lambda: trace_dict.strict_get_list('hello'))
    assert_raise(lambda: trace_dict.strict_get_int('hello'))
    assert_raise(lambda: trace_dict.strict_get_int('missing'))
    assert_raise(lambda: trace_dict.strict_get_dict('missing'))

    assert_raise(lambda: hello.strict_get_str('world'))
    assert_raise(lambda: hello.strict_get_dict('world'))
    assert_raise(lambda: hello.strict_get_list('world'))


def test_tracing_exception_message():
    exc = tracing.TracingException(
        filename='some/file/path',
        path='path.to.field',
        message='Some error message',
        context=None,
    )
    valid_message = (
        '\n'
        '###############################################################\n'
        'In "some/file/path"\n'
        'At YAML path "path.to.field"\n'
        'Error:\n'
        'Some error message\n'
        '###############################################################'
    )

    assert str(exc) == valid_message


def test_tracing_exception_message_with_context():
    exc = tracing.TracingException(
        filename='some/file/path',
        path='path.to.field',
        message='Some error message',
        context='schema "swagger 2.0"',
    )
    valid_message = (
        '\n'
        '###############################################################\n'
        'In "some/file/path" with schema "swagger 2.0"\n'
        'At YAML path "path.to.field"\n'
        'Error:\n'
        'Some error message\n'
        '###############################################################'
    )

    assert str(exc) == valid_message


def test_methods_deprecation():
    def _get():
        trace_dict = tracing.TracingDict('items', TEST_DICT_SIMPLE.copy())
        trace_dict.set_errors_context('schema "swagger 2.0"')
        _ = trace_dict.get('hello')

    def _getitem():
        trace_dict = tracing.TracingDict('items', TEST_DICT_SIMPLE.copy())
        trace_dict.set_errors_context('schema "swagger 2.0"')
        _ = trace_dict['hello']

    def _assert_raise(func, msg):
        try:
            func()
            assert False, 'This assert should never happen'
        except tracing.TracingException as exc:
            assert msg in str(exc), 'Invalid error message'
        except Exception:  # pylint: disable=broad-except
            assert False, 'This assert should never happen'

    error_msg = (
        'Error:\n\n'
        'Method "{method}" of "TracingDict" is deprecated.\n'
        'See stacktrace for invalid usage.\n'
        'See wiki for more info:\n'
        'https://wiki.yandex-team.ru'
        '/taxi/backend/userver/etc/tracing_dict_typed_get/\n'
    )
    _assert_raise(_get, error_msg.format(method='get'))
    _assert_raise(_getitem, error_msg.format(method='__getitem__'))


def test_typo_raise_on_unknown_field():
    def _assert_raise(func: Callable, msg: str) -> None:
        exc = assert_raise(func)
        assert msg in str(exc)

    trace_dict = tracing.TracingDict(
        filename='items', data=TEST_DICT_SIMPLE.copy(),
    )

    _assert_raise(
        func=lambda: trace_dict.raise_on_unknown_field(
            ['hellow', 'hi', 'goto', 'London'],
        ),
        msg='Field "hello" not allowed\nDid you mean "hellow"?',
    )

    _assert_raise(
        func=lambda: trace_dict.raise_on_unknown_field(
            ['hellow', 'helloy', 'hi', 'goto', 'London'],
        ),
        msg=(
            'Field "hello" not allowed\n'
            'Did you mean one of those values: [\'hellow\', \'helloy\']?'
        ),
    )


def test_typo_typed_get():
    def _assert_raise(func: Callable, msg: str) -> None:
        exc = assert_raise(func)
        assert msg in str(exc)

    trace_dict = tracing.TracingDict(
        filename='items', data=TEST_DICT_SIMPLE.copy(),
    )

    _assert_raise(
        func=lambda: trace_dict.strict_get_dict('hellow'),
        msg=(
            'Key "hellow" does not exists\n'
            'But key "hello" found, is it a typo?'
        ),
    )

    _assert_raise(
        func=lambda: trace_dict.strict_get_dict('hello_'),
        msg=(
            'Key "hello_" does not exists\n'
            'But keys [\'hello\', \'hello_2\'] found, is one of them a typo?'
        ),
    )


def test_edit_mutable_dict():
    def _work(_t_d):
        _t_d['test'] = 'hello'
        _t_d.update({'test': 'world'})
        _t_d.pop('test')

    trace_dict = tracing.TracingDict('tracing_guard', TEST_DICT_SIMPLE.copy())
    _work(trace_dict)
    _work(trace_dict.strict_get_dict('hello'))


def test_edit_immutable_dict():
    _immutable_message = 'test immutable'

    def _assert_raise(
            _funcs: List[Callable], _dict: tracing.TracingDict,
    ) -> None:
        for func in _funcs:
            try:
                func(_dict)
                assert False, 'This assert should never happen'
            except AssertionError as exc:
                raise exc
            except tracing.TracingDeprecationException:
                pass
            except Exception as exc:  # pylint: disable=broad-except
                msg = str(exc)
                if _immutable_message != msg:
                    raise exc

    def _set(_t_d):
        _t_d['test'] = 'hello'

    def _del(_t_d):
        del _t_d['hi']

    def _update(_t_d):
        _t_d.update({'test': 'world'})

    def _pop(_t_d):
        _t_d.pop('hello')

    def _get(_t_d):
        _t_d.get('test')

    def _popitem(_t_d):
        _t_d.popitem()

    def _setdefault(_t_d):
        _t_d.setdefault('test1', default='world')

    def _clear(_t_d):
        _t_d.clear()

    trace_dict = tracing.TracingDict(
        'tracing_guard',
        TEST_DICT_SIMPLE.copy(),
        immutable_error=_immutable_message,
    )

    actions = [_set, _del, _update, _pop, _get, _popitem, _setdefault, _clear]

    _assert_raise(actions, trace_dict)
    _assert_raise(actions, trace_dict.strict_get_dict('hello'))


def test_edit_mutable_list():
    trace_list = tracing.TracingList('list', TEST_LIST_SAMPLE)
    trace_list[0] = 0
    trace_list += [1]
    trace_list.insert(0, 0)
    del trace_list[0]


def test_edit_immutable_list():
    _immutable_message = 'test immutable'

    def _assert_raise(
            _funcs: List[Callable], _list: tracing.TracingList,
    ) -> None:
        for func in _funcs:
            try:
                func(_list)
                assert False, 'This assert should never happen'
            except AssertionError as exc:
                raise exc
            except tracing.TracingDeprecationException:
                pass
            except Exception as exc:  # pylint: disable=broad-except
                msg = str(exc)
                if _immutable_message != msg:
                    raise exc

    def _set(_list):
        _list[0] = 0

    def _del(_list):
        del _list[0]

    def _iadd(_list):
        _list += [1, 2]

    def _insert(_list):
        _list.insert(1, 2)

    def _clear(_list):
        _list.clear()

    def _pop(_list):
        _list.pop()

    def _expand(_list):
        _list.extend([1, 2, 3])

    def _remove(_list):
        _list.remove(1)

    def _reverse(_list):
        _list.reverse()

    trace_list = tracing.TracingList(
        'list', TEST_LIST_SAMPLE, immutable_error=_immutable_message,
    )
    actions = [
        _set,
        _del,
        _iadd,
        _insert,
        _clear,
        _pop,
        _expand,
        _remove,
        _reverse,
    ]
    _assert_raise(actions, trace_list)
    _assert_raise(actions, trace_list[3])
