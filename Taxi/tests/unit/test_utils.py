from pahtest.utils import (
    extract_dataset, JsonContainer as JC, _json_get, _json_set
)


def test_json_container_get():
    assert 'one' == _json_get(['zero', 'one'], 1)
    assert _json_get(['zero', 'one'], 2) is None
    assert 1 == _json_get(dict(one=1, two=2), 'one')
    assert _json_get(dict(one=1, two=2), 'three') is None
    assert 22 == _json_get(dict(one=[dict(two=22)], two=2), 'one.0.two')
    assert 12 == _json_get(dict(one=[11, dict(two=12)], two=2), 'one.1.two')
    assert 211 == _json_get([1, dict(one=dict(two=211))], '1.one.two')
    assert _json_get([], 'one') is None
    assert _json_get({}, 1) is None


def test_json_set():
    value = 'hello'
    # - int, list
    assert [value] == _json_set([0], ['0'], value).unwrap()
    # - int, scalar
    assert _json_set(0, ['0'], value).value_or(None) is None
    # - str, scalar
    assert _json_set('one', ['0'], value).value_or(None) is None
    # - int, dict
    assert _json_set({'one': 1}, ['0'], value).value_or(None) is None
    # - int, empty
    assert _json_set({'one': 1}, ['0'], value).value_or(None) is None
    # - str, dict
    assert {'one': value} == _json_set({'one': 1}, ['one'], value).unwrap()
    # - int, empty dict
    assert {'one': value} == _json_set({}, ['one'], value).unwrap()
    # - str, empty list
    assert _json_set([], ['one'], value).value_or(None) is None
    # - int, empty list
    assert [None, value] == _json_set([], ['1'], value).unwrap()
    # - str, empty dict
    assert {'one': value} == _json_set({}, ['one'], value).unwrap()

    # - redefine inner list value
    assert {'one': [{'two': value}]} == _json_set(
        {'one': [{'two': 1}]}, ['one', '0', 'two'], value
    ).unwrap()
    # - append inner list value
    assert {'one': [{'two': 1}, {'two': value}]} == _json_set(
        {'one': [{'two': 1}]}, ['one', '1', 'two'], value
    ).unwrap()
    # - append inner list value
    assert {'one': value} == _json_set(
        {'one': [{'two': 1}]}, ['one'], value
    ).unwrap()


def test_json_container_set():
    value = 'hello'
    c = JC({'one': [{'two': 1}]}).set('one.0.two', value).unwrap()
    assert {'one': [{'two': value}]} == c._content
    assert value == c.get('one.0.two')


def test_extract_dataset():
    value = 'hello'
    JC({'one': [{'two': 1}]}).set('one.0.two', value)
    assert value == extract_dataset('dataset:one.0.two:default')
    assert 'default' == extract_dataset('dataset:one.1.two:default')
    assert 'default' == extract_dataset('dataset:one.one.two:default')
