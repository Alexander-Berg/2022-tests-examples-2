# pylint: disable=protected-access
import pytest

from taxi_dashboards import utils
from taxi_dashboards.clients import conductor


@pytest.mark.parametrize(
    'conductor_group,hosts,expected_result',
    [
        (
            'taxi_test_api',
            (
                'taxi-api-sas-01.taxi.tst.yandex.net',
                'taxi-api-vla-01.taxi.tst.yandex.net',
            ),
            [
                {
                    'group_name': 'taxi_test_api',
                    'host_addr': 'taxi-api-sas-01.taxi.tst.yandex.net',
                    'host_alias': 'taxi-api-sas-01.taxi.tst.yandex.net',
                    'host_alias_graphite': (
                        'taxi-api-sas-01_taxi_tst_yandex_net'
                    ),
                    'cluster_name': 'testing',
                    'host_short': 'sas-01',
                },
                {
                    'group_name': 'taxi_test_api',
                    'host_addr': 'taxi-api-vla-01.taxi.tst.yandex.net',
                    'host_alias': 'taxi-api-vla-01.taxi.tst.yandex.net',
                    'host_alias_graphite': (
                        'taxi-api-vla-01_taxi_tst_yandex_net'
                    ),
                    'cluster_name': 'testing',
                    'host_short': 'vla-01',
                },
            ],
        ),
        (
            'taxi_api',
            (
                'taxi-api01e.taxi.yandex.net',
                'taxi-api05e.taxi.yandex.net',
                'taxi-api03f.taxi.yandex.net',
            ),
            [
                {
                    'group_name': 'taxi_api',
                    'host_addr': 'taxi-api01e.taxi.yandex.net',
                    'host_alias': 'taxi-api01e.taxi.yandex.net',
                    'host_alias_graphite': 'taxi-api01e_taxi_yandex_net',
                    'cluster_name': 'production',
                    'host_short': '01e',
                },
                {
                    'group_name': 'taxi_api',
                    'host_addr': 'taxi-api03f.taxi.yandex.net',
                    'host_alias': 'taxi-api03f.taxi.yandex.net',
                    'host_alias_graphite': 'taxi-api03f_taxi_yandex_net',
                    'cluster_name': 'production',
                    'host_short': '03f',
                },
                {
                    'group_name': 'taxi_api',
                    'host_addr': 'taxi-api05e.taxi.yandex.net',
                    'host_alias': 'taxi-api05e.taxi.yandex.net',
                    'host_alias_graphite': 'taxi-api05e_taxi_yandex_net',
                    'cluster_name': 'production',
                    'host_short': '05e',
                },
            ],
        ),
        (
            'eda_prod_beta_app',
            (
                'beta-app1-myt.lxc.eda.yandex.net',
                'beta-app1-sas.lxc.eda.yandex.net',
                'beta-app1-vla.lxc.eda.yandex.net',
            ),
            [
                {
                    'group_name': 'eda_prod_beta_app',
                    'host_addr': 'beta-app1-myt.lxc.eda.yandex.net',
                    'host_alias': 'beta-app1-myt.lxc.eda.yandex.net',
                    'host_alias_graphite': 'beta-app1-myt_lxc_eda_yandex_net',
                    'cluster_name': 'UNKNOWN',
                    'host_short': 'myt',
                },
                {
                    'group_name': 'eda_prod_beta_app',
                    'host_addr': 'beta-app1-sas.lxc.eda.yandex.net',
                    'host_alias': 'beta-app1-sas.lxc.eda.yandex.net',
                    'host_alias_graphite': 'beta-app1-sas_lxc_eda_yandex_net',
                    'cluster_name': 'UNKNOWN',
                    'host_short': 'sas',
                },
                {
                    'group_name': 'eda_prod_beta_app',
                    'host_addr': 'beta-app1-vla.lxc.eda.yandex.net',
                    'host_alias': 'beta-app1-vla.lxc.eda.yandex.net',
                    'host_alias_graphite': 'beta-app1-vla_lxc_eda_yandex_net',
                    'cluster_name': 'UNKNOWN',
                    'host_short': 'vla',
                },
            ],
        ),
        (
            'taxi_conductor_taxi_db_mongo_tracker',
            (
                'taxi-tracker-mrs-dev01h.taxi.yandex.net',
                'taxi-tracker-mrs01e.taxi.yandex.net',
                'tracker-mrs-vla-01.taxi.yandex.net',
            ),
            [
                {
                    'group_name': 'taxi_conductor_taxi_db_mongo_tracker',
                    'host_addr': 'taxi-tracker-mrs-dev01h.taxi.yandex.net',
                    'host_alias': 'taxi-tracker-mrs-dev01h.taxi.yandex.net',
                    'host_alias_graphite': (
                        'taxi-tracker-mrs-dev01h_taxi_yandex_net'
                    ),
                    'cluster_name': 'production',
                    'host_short': 'taxi-tracker-mrs-dev01h',
                },
                {
                    'group_name': 'taxi_conductor_taxi_db_mongo_tracker',
                    'host_addr': 'taxi-tracker-mrs01e.taxi.yandex.net',
                    'host_alias': 'taxi-tracker-mrs01e.taxi.yandex.net',
                    'host_alias_graphite': (
                        'taxi-tracker-mrs01e_taxi_yandex_net'
                    ),
                    'cluster_name': 'production',
                    'host_short': 'taxi-tracker-mrs01e',
                },
                {
                    'group_name': 'taxi_conductor_taxi_db_mongo_tracker',
                    'host_addr': 'tracker-mrs-vla-01.taxi.yandex.net',
                    'host_alias': 'tracker-mrs-vla-01.taxi.yandex.net',
                    'host_alias_graphite': (
                        'tracker-mrs-vla-01_taxi_yandex_net'
                    ),
                    'cluster_name': 'production',
                    'host_short': 'tracker-mrs-vla-01',
                },
            ],
        ),
        (
            'taxi_conductor_taxi_db_mongo_tracker',
            [
                'taxi-tracker2-mrs-dev01h.taxi.yandex.net',
                'taxi-tracker2-mrs01e.taxi.yandex.net',
                'taxi-tracker-mrs-vla-01.taxi.yandex.net',
            ],
            [
                {
                    'group_name': 'taxi_conductor_taxi_db_mongo_tracker',
                    'host_addr': 'taxi-tracker-mrs-vla-01.taxi.yandex.net',
                    'host_alias': 'taxi-tracker-mrs-vla-01.taxi.yandex.net',
                    'host_alias_graphite': (
                        'taxi-tracker-mrs-vla-01_taxi_yandex_net'
                    ),
                    'cluster_name': 'production',
                    'host_short': 'tracker-mrs-vla-01',
                },
                {
                    'group_name': 'taxi_conductor_taxi_db_mongo_tracker',
                    'host_addr': 'taxi-tracker2-mrs-dev01h.taxi.yandex.net',
                    'host_alias': 'taxi-tracker2-mrs-dev01h.taxi.yandex.net',
                    'host_alias_graphite': (
                        'taxi-tracker2-mrs-dev01h_taxi_yandex_net'
                    ),
                    'cluster_name': 'production',
                    'host_short': 'tracker2-mrs-dev01h',
                },
                {
                    'group_name': 'taxi_conductor_taxi_db_mongo_tracker',
                    'host_addr': 'taxi-tracker2-mrs01e.taxi.yandex.net',
                    'host_alias': 'taxi-tracker2-mrs01e.taxi.yandex.net',
                    'host_alias_graphite': (
                        'taxi-tracker2-mrs01e_taxi_yandex_net'
                    ),
                    'cluster_name': 'production',
                    'host_short': 'tracker2-mrs01e',
                },
            ],
        ),
        (
            'taxi_conductor_taxi_db_mongo_tracker',
            ['taxi-tracker2-mrs-dev01h.taxi.yandex.net'],
            [
                {
                    'group_name': 'taxi_conductor_taxi_db_mongo_tracker',
                    'host_addr': 'taxi-tracker2-mrs-dev01h.taxi.yandex.net',
                    'host_alias': 'taxi-tracker2-mrs-dev01h.taxi.yandex.net',
                    'host_alias_graphite': (
                        'taxi-tracker2-mrs-dev01h_taxi_yandex_net'
                    ),
                    'cluster_name': 'production',
                    'host_short': 'taxi-tracker2-mrs-dev01h',
                },
            ],
        ),
    ],
)
def test_get_hosts_info(conductor_group, hosts, expected_result, patch):
    @patch('taxi_dashboards.clients.conductor.get_hostlist')
    def _conductor_get_hostlist(cgroup):
        if cgroup == conductor_group:
            return hosts
        raise conductor.NotFoundError

    @patch('taxi_dashboards.clients.conductor.get_groups_for_host')
    def _conductor_get_groups_for_host(host):
        groups = [conductor_group]
        if conductor_group.startswith('taxi_unstable_'):
            groups.append('taxi_unstable_all')
        elif conductor_group.startswith('taxi_test_'):
            groups.append('taxi_test_all')
        elif conductor_group.startswith('taxi_'):
            groups.append('taxi_prod_all')
        return groups

    hosts_info, groups = utils.get_hosts_info(conductor_group)
    assert groups == [conductor_group]
    assert hosts_info == expected_result
