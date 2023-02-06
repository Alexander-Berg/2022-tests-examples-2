import os
import re

import pytest
import ymlcfg

from stall import cfg


@pytest.fixture(autouse=True)
def restore_env():
    """Поскольку тесты правят окружение процесса, то его надо восстанавливать"""
    hostname    = os.environ.get('HOSTNAME')
    configname  = os.environ.get('CONFIGNAME')

    yield

    if hostname:
        os.environ['HOSTNAME'] = hostname
    else:
        os.environ.pop('HOSTNAME', None)

    if configname:
        os.environ['CONFIGNAME'] = configname
    else:
        os.environ.pop('CONFIGNAME', None)


def test_cfg(tap):

    tap.plan(2)

    tap.ok(cfg, 'конфиг прочитан')
    tap.ok(cfg('description'), 'Доступ к полям есть')

    tap()


def test_cfg_hosts(tap):
    tap.plan(2, 'Для всех хостов валидные конфиги')

    path = os.path.dirname(__file__)
    path = os.path.dirname(path)
    path = os.path.dirname(path)
    config_dir = os.path.join(path, 'config')
    tap.ok(os.path.exists(config_dir), config_dir)
    _, _, files = next(os.walk(config_dir), (None, None, None))

    hostnames = []
    for filename in files:
        parts = re.findall(r'^host-([a-zA-Z0-9-]+)\.(yml|yaml)$', filename)
        if parts:
            hostname = parts[0][0]
            hostnames.append((hostname, filename))

    with tap.subtest(len(hostnames), 'Загрузим конфиги') as taps:
        for hostname, filename in hostnames:
            with taps.subtest(1, filename) as _taps:
                os.environ['HOSTNAME'] = hostname
                os.environ['CONFIGNAME'] = hostname
                loader = ymlcfg.loader(config_dir)
                _taps.ok(loader(), 'Конфиг загружен')
