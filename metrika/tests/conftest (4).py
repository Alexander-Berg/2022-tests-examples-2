import os
import pytest

import metrika.pylib.config as mpc
import metrika.pylib.structures.dotdict as mdd
import metrika.admin.python.clickhouse_configs_fetcher.lib.bishop_watcher as ccf_bishop_watcher
import metrika.admin.python.clickhouse_configs_fetcher.lib.master as master


os.environ['ROBOT_METRIKA_ADMIN_OAUTH'] = 'hello, this is token'


@pytest.fixture
def bishop_watcher(monkeypatch):
    monkeypatch.setattr(master.Master, 'get_config', lambda this: mpc.get_xml_config_from_builtin('config.xml'))
    return ccf_bishop_watcher.BishopWatcher(mpc.get_xml_config_from_builtin('config.xml').bishop_watcher.configs, master=master.Master())


@pytest.fixture
def missing_config():
    return mdd.DotDict.from_dict({
        'path': 'missing.data',
        'environemnt': 'environment',
        'program': 'program',
    })


@pytest.fixture
def exists_config():
    # md5sum is 5d41402abc4b2a76b9719d911017c592
    with open('exists.data', 'w') as fd:
        fd.write("hello")

    return mdd.DotDict.from_dict({
        'path': 'exists.data',
        'environemnt': 'environment',
        'program': 'program',
    })
