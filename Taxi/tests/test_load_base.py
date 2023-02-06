import os

import ymlcfg


def test_empty(tap, test_cfg_dir):
    tap.plan(1)
    cfg = ymlcfg.loader(test_cfg_dir('empty'))
    tap.eq(cfg(''), {}, 'empty cfg')
    tap.done_testing()


def test_base(tap, test_cfg_dir):
    tap.plan(4)
    cfg = ymlcfg.loader(test_cfg_dir('base'))
    tap.eq(
        cfg(''),
        {
            'hello': 'world',
            'array': [
                {'a': 'b', 'c': 'd'},
                {'d': 'e', 'f': 'g'}
            ]
        },
        'config once')

    tap.eq(cfg('hello'), 'world', 'path1')
    tap.eq(cfg('array.0.a'), 'b', 'path array 1')
    tap.eq(cfg('array.1.f'), 'g', 'path array 2')
    tap.done_testing()


def test_env(tap, test_cfg_dir):
    with tap.plan(8):
        os.environ['BLA'] = 'HELLO'
        os.environ['BLE'] = 'HELP'
        os.environ['HA'] = ''

        if 'HE' in os.environ:
            del os.environ['HE']

        tap.eq(os.getenv('BLA', ''), 'HELLO', 'env1')
        tap.eq(os.getenv('BLE', ''), 'HELP', 'env2')

        cfg = ymlcfg.loader(test_cfg_dir('env'))
        tap.ok(cfg, 'tests/cfg/env')
        tap.eq(cfg('hello'), 'HELLO', 'env from first config')
        tap.eq(cfg('array.0.a'), 'b', 'normal value')
        tap.eq(cfg('array.1'), 'HELP', 'env second config')

        tap.eq(cfg('default'), 'default for default', 'default for empty')
        tap.eq(cfg('default2'), 'default for default2', 'default2 for none')


def test_configname(tap, test_cfg_dir):
    with tap.plan(4):
        os.environ['CONFIGNAME'] = 'bed82e8c-051d-11e9-b57e-336e55b3cf31'

        cfg = ymlcfg.loader(test_cfg_dir('merge'))
        tap.ok(cfg, 'tests/cfg/merge')
        tap.eq(cfg('hello'), 'ERROR-THE-CONFIG', 'env from first config')
        tap.eq(cfg('array.0.a'), 'b', 'normal value')
        tap.eq(cfg('array.1'), {'d': 'e', 'f': 'g'}, 'env second config')
