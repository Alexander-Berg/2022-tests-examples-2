import os
import pytest
import time
from functools import partial

from pahtest.browser import Browser
from pahtest.options import PlainOptions
from pahtest.folder import Folder
from pahtest import helpers, utils


NO_ELEMENT = 'Page has no element'


@pytest.mark.skip(reason='Boilerplate for the future tests')
def test_wait_integration(tap):
    tests = Folder('tests/functional/assets/wait.yml')
    gen = tests.loop()

    # long notation tests for active test
    res = next(gen)  # get_ok Common case
    tap.ok(res.success, res.description)
    res = next(gen)  # get_ok Takes timeout from options.timeout
    tap.ok(res.success, res.description)
    res = next(gen)  # get_ok Takes timeout from options.timeout
    tap.ok(res.success, res.description)
    res = next(gen)  # get_ok Active test. Leads to error.
    tap.ok(res.success, res.description)
    res = next(gen)  # get_ok Such short notation is not allowed in active test
    tap.ok(res.success, res.description)

    # short notation for active test
    res = next(gen)  # get_ok Take desc from the first has
    tap.ok(res.success, res.description)

    # notation for passive test
    res = next(gen)  # get_ok Common case
    tap.ok(res.success, res.description)
    res = next(gen)  # get_ok Takes timeout from options.timeout
    tap.ok(res.success, res.description)


def test_wait_with_steps():
    # - accepts args and calculates correct results
    results, _ = utils.wait_with_steps(
        timeout=10.0,
        funcs=3*[lambda x, y: x + y],
        funcs_args=[(1, 2), (3, 4), (5, 6)],
        condition=lambda result: bool(result),
        step=0.01
    )
    assert [3, 7, 11] == results

    # - really waits for success results
    timeout = 0.2
    current = time.time()
    utils.wait_with_steps(
        timeout=timeout,
        funcs=3*[lambda x: x],
        funcs_args=[(0,), (1,), (2,)],
        condition=lambda result: bool(result),
        step=0.01
    )
    assert time.time() - current >= timeout


def test_extract_env():
    url, width = 'http://nginx', '800'
    os.environ['SITE_URL'] = url
    os.environ['SITE_WIDTH'] = width
    try:
        assert url == utils.extract_env(f'env:SITE_URL:{url}')
        assert width == utils.extract_env(f'env:SITE_WIDTH:{width}')
    finally:
        os.environ.pop('SITE_URL')
        os.environ.pop('SITE_WIDTH')


def test_traverse():
    def key(x):
        return f'K{x}'

    def value(x):
        return f'V{x}'

    do = partial(utils.traverse, key_callback=key, value_callback=value)
    # flat list
    assert ['V1', 'V2'] == do([1, 2])
    # flat dict
    assert {'K1': 'V1', 'K2': 'V2'} == do({1: '1', 2: '2'})
    # just scalar
    assert 'V1' == do(1)
    # empty dict, list, scalar
    assert ({}, [], 'V', 'V0') == (do({}), do([]), do(''), do(0))
    # assembled dict with list and scalar
    large_output = {
        'K1': 'V1', 'K2': ['Vtwo', 'Vzwei', ['VTWO', 'VTwo']],
        'K3': {'K3': 'Vthree'}
    }
    large_input = {1: '1', 2: ['two', 'zwei', ['TWO', 'Two']], 3: {3: 'three'}}
    assert large_output == do(large_input)

    # just key func
    assert {'K1': '1'} == utils.traverse({1: '1'}, key_callback=key)
    # just value func
    assert {1: 'V1'} == utils.traverse({1: '1'}, value_callback=value)
    # no key, no value
    assert {1: '1'} == utils.traverse({1: '1'})


def test_singleton():
    class A(metaclass=helpers.Singleton):
        pass

    assert id(A()) == id(A())
