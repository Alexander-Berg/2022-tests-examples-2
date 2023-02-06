import pytest

import yatest.common

import metrika.pylib.confgen as mtcg
import metrika.pylib.config as lib_config


class ConfgenTestError(Exception):
    pass


def test_build_hosts_data():
    hosts = lib_config.get_yaml_config_from_file(yatest.common.source_path('metrika/pylib/confgen/tests/hosts.yaml'))

    result = mtcg.build_hosts_data(hosts)
    all_groups = set()

    for host in hosts:
        for group in host.groups:
            all_groups.add(group)

    assert set(result['groups'].keys()) == all_groups

    assert result['hosts']['interview.man.yp-c.yandex.net'].index == 0
    assert result['hosts']['interview.man.yp-c.yandex.net'].shard == 'noshard'
    assert result['hosts']['interview.man.yp-c.yandex.net'].layer == 'nolayer'

    for host in hosts:
        if 'noneprod' not in host.tags:
            for group in host.groups:
                assert len([h for h in result['groups'][group] if h['fqdn'] == host.fqdn]) == 1

    assert result['by_layer'][1][1]['mtlog'][0]['fqdn'] == 'mtlog01-01-1.yandex.ru'
    assert len(result['by_layer']['nolayer']['noshard']['metrika']) == 2

    assert 'mtcalclog19i.metrika.yandex.net' in result['noneprod']
    assert 'mtcalclog19i.metrika.yandex.net' not in result['hosts']
    assert 'bsbufbuf01k.yabs.yandex.ru' in result['noneprod']
    assert 'bsbufbuf01k.yabs.yandex.ru' in result['hosts']

    result = mtcg.build_hosts_data(hosts, noneprod=True)
    assert not result['noneprod']
    assert 'mtcalclog19i.metrika.yandex.net' in result['hosts']
    assert 'bsbufbuf01k.yabs.yandex.ru' in result['hosts']

    hosts = [
        {'fqdn': 'fakehost'}
    ]

    with pytest.raises(ValueError):
        mtcg.build_hosts_data(hosts)


def test_build_hosts_data_get_hosts_called(monkeypatch):
    def mock_get_hosts(*args, **kwargs):
        raise ConfgenTestError("Test Error")

    monkeypatch.setattr(mtcg, 'get_hosts', mock_get_hosts)
    with pytest.raises(ConfgenTestError):
        mtcg.build_hosts_data()
