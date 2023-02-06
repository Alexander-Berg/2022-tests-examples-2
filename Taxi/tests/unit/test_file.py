import os
import pytest

from pahtest import case
from pahtest.file import File
from pahtest.errors import PahtestError
from pahtest.results import PlanResult, Note


def test_validation():
    # - common case
    code = File(dict(options={}, tests=[]))
    code.validate()

    # - optional name field
    code = File(dict(name='', options={}, tests=[]))
    code.validate()

    # - missed fields
    with pytest.raises(PahtestError) as e:
        File(dict(options={})).validate()
        assert 'must contain' in str(e)

    # - excess fields
    with pytest.raises(PahtestError) as e:
        File(dict(wrong='', options={}, tests=[])).validate()
        assert 'not allowed sections' in str(e)

    # - not a dict
    with pytest.raises(PahtestError) as e:
        File(code='').validate()
        assert 'must contain keys' in str(e)


def test_resolve_yaml():
    f = 'tests/unit/assets/file/{}.yml'.format

    # - resolve dict
    raw = {'options': {'import': f('dict')}, 'tests': []}
    resolved = {
        'options': {'base_url': 'http://nginx', 'browser': 'chrome'},
        'tests': []
    }
    assert File(resolved) == File(raw).resolve_yaml_imports(), File(raw)

    # - resolve list
    raw = {'options': {}, 'tests': [
        {'get_ok': '/'}, {'has': '/html/body'},
        {'import': f('list')},
    ]}
    resolved = {'options': {}, 'tests': [
        {'get_ok': '/'}, {'has': '/html/body'},
        {'url': '/'}, {'wait': [{'has': '/html/body/div'}]}, {'has': 'css:#to-click'},
    ]}
    assert File(resolved) == File(raw).resolve_yaml_imports(), File(raw)

    # - not existing file
    raw = {'options': {'import': f('not-existing')}, 'tests': []}
    with pytest.raises(PahtestError) as e:
        File(raw).resolve_yaml_imports()
        assert 'No such file or directory' in str(e)

    # - wrong structure type: import list to dict
    raw = {'options': {'import': f('list')}, 'tests': []}
    with pytest.raises(PahtestError) as e:
        File(raw).resolve_yaml_imports()
        assert 'wrong data structure' in str(e)

    # - wrong structure type: import dict to list
    raw = {'options': {}, 'tests': [{'import': f('dict')}]}
    resolved = {'options': {}, 'tests': [
        {'base_url': 'http://nginx', 'browser': 'chrome'}
    ]}
    assert File(resolved) == File(raw).resolve_yaml_imports()

    # - recursive import
    raw = {'options': {}, 'tests': [{'import': f('recursive/parent')}]}
    resolved = {
        'options': {},
        'tests': [
            {'get_ok': '/'},
            {'has': {'xpath': '/html/body/div', 'desc': 'Has div'}},
            {'has': 'css:#to-click'},
        ]
    }
    assert resolved == File(raw).resolve_yaml_imports().code

    # - dict unpack does NOT redefine values
    raw = {'options': {'import': f('dict'), 'browser': 'safari'}}
    resolved = {'options': {'base_url': 'http://nginx', 'browser': 'safari'}}
    assert resolved == File(raw).resolve_yaml_imports().code

    # - dict unpack DO redefine values
    raw = {'options': {'browser': 'safari', 'import': f('dict')}}
    resolved = {'options': {'base_url': 'http://nginx', 'browser': 'chrome'}}
    assert resolved == File(raw).resolve_yaml_imports().code

    # - list unpack skips some keys
    raw = {'tests': [{'import': f('list'), 'some_key': 'we\'ll be thrown'}]}
    resolved = {'tests': [
        {'url': '/'}, {'wait': [{'has': '/html/body/div'}]}, {'has': 'css:#to-click'},
    ]}
    assert resolved == File(raw).resolve_yaml_imports().code

    # - resolve relative filepath
    raw = {'options': {}, 'tests': [
        {'import': f('recursive/parent_with_relative')}
    ]}
    resolved = {
        'options': {},
        'tests': [
            {'get_ok': '/'},
            {'has': {'xpath': '/html/body/div', 'desc': 'Has div'}},
            {'has': 'css:#to-click'},
        ]
    }
    assert File(resolved) == File(raw).resolve_yaml_imports(), File(raw)


def test_skip_with_env():
    code = dict(
        options=dict(
            skip='env:SKIP', selenium_hub_url='http://localhost:4450/wd/hub'
        ),
        tests=[dict(get_ok='base.html')]
    )

    # - skip for the text
    os.environ['SKIP'] = 'True'
    loop = File(code=code).resolve_env_vars().loop()
    res = next(loop, None)
    assert case.SKIP_MESSAGE == res.message

    # - no skip for empty str env var
    os.environ['SKIP'] = ''
    loop = File(code=code).resolve_env_vars().loop()
    res = next(loop, None)
    assert case.SKIP_MESSAGE != res.message

    # - no skip for no env var
    os.environ.pop('SKIP')
    loop = File(code=code).resolve_env_vars().loop()
    res = next(loop, None)
    assert case.SKIP_MESSAGE != res.message


def test_no_tests_list():
    # 1. wrong type case
    results = File(code=dict(options={}, tests={})).run()
    # - only two results: plan and "not ok" with error
    assert 2 == len(results.list), results
    assert isinstance(results.list[0], PlanResult)
    assert isinstance(results.list[1], Note)
    # - second result tells about wrong tests section
    assert 'loading tests' == results.list[1].description
    assert '"tests" section must be list.' == results.list[1].message

    # 2. empty tests case
    results = File(code=dict(options={}, tests=[])).run()
    # - only two results: plan and "not ok" with error
    assert 2 == len(results.list), results
    assert isinstance(results.list[0], PlanResult)
    assert isinstance(results.list[1], Note)
    # - second result tells about wrong tests section
    assert 'loading tests' == results.list[1].description
    assert '"tests" section is empty.' == results.list[1].message
