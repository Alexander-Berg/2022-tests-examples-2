import os
import ymlcfg


def test_predefine_empty(tap, test_cfg_dir):
    tap.plan(1)
    cfg = ymlcfg.loader(test_cfg_dir('empty'), predefine={'a': 'b'})
    tap.eq(cfg(''), {'a': 'b'}, 'empty config')
    tap()


def test_predefine_base(tap, test_cfg_dir):
    tap.plan(4)
    cfg = ymlcfg.loader(test_cfg_dir('base'), predefine={'a': 'b'})
    tap.eq(cfg(''),
           {
               'hello': 'world',
               'array': [
                   {'a': 'b', 'c': 'd'},
                   {'d': 'e', 'f': 'g'}
               ],
               'a': 'b'
           },  # noqa
           'config once')
    tap.eq(cfg('hello'), 'world', 'path1')
    tap.eq(cfg('array.0.a'), 'b', 'path array 1')
    tap.eq(cfg('array.1.f'), 'g', 'path array 2')
    tap()


def test_predefine_env(tap, test_cfg_dir):
    tap.plan(7)
    os.environ['BLA'] = 'HELLO'
    os.environ['BLE'] = 'HELP'

    tap.eq(os.getenv('BLA', ''), 'HELLO', 'env1')
    tap.eq(os.getenv('BLE', ''), 'HELP', 'env2')

    cfg = ymlcfg.loader(test_cfg_dir('env'), predefine={'a': 'env:BLA'})
    tap.ok(cfg, 'tests/cfg/env')
    tap.eq(cfg('hello'), 'HELLO', 'env from first config')
    tap.eq(cfg('array.0.a'), 'b', 'normal value')
    tap.eq(cfg('array.1'), 'HELP', 'env second config')
    tap.eq(cfg('a'), 'HELLO', 'predefined env value')
    tap()
