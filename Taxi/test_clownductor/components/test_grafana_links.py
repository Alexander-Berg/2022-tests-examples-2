import pytest

from clownductor.internal import services as services_module


GRAFANA_PREFIX = 'https://grafana.yandex-team.ru/d/someuuid'


@pytest.fixture(name='grafana_api_search_existed_dashboard')
def _grafana_api_search_existed_dashboard():
    return [
        'nanny_taxi_nanny-1_stable',
        'nanny_taxi_nanny-1_testing',
        'nanny_taxi_nanny-2_stable',
        'taxi_conductor_taxi_conductor-3',
        'nanny_eda_nanny-5_stable',
    ]


@pytest.mark.pgsql('clownductor', files=['default.sql'])
async def test_grafana_links(web_context):
    expected_links = [
        (
            'taxi_nanny-1_stable',
            services_module.ClusterType.NANNY,
            f'{GRAFANA_PREFIX}/nanny_taxi_nanny-1_stable',
        ),
        ('taxi_nanny-1_pre_stable', services_module.ClusterType.NANNY, None),
        (
            'taxi_nanny-1_testing',
            services_module.ClusterType.NANNY,
            f'{GRAFANA_PREFIX}/nanny_taxi_nanny-1_testing',
        ),
        ('taxi_nanny-1_unstable', services_module.ClusterType.NANNY, None),
        (
            'taxi_nanny-2_stable',
            services_module.ClusterType.NANNY,
            f'{GRAFANA_PREFIX}/nanny_taxi_nanny-2_stable',
        ),
        ('taxi_nanny-2_pre_stable', services_module.ClusterType.NANNY, None),
        (
            'taxi_conductor-3',
            services_module.ClusterType.CONDUCTOR,
            f'{GRAFANA_PREFIX}/taxi_conductor_taxi_conductor-3',
        ),
        ('pg-direct-link-4', services_module.ClusterType.POSTGRES, None),
        (
            'eda_nanny-5_stable',
            services_module.ClusterType.NANNY,
            f'{GRAFANA_PREFIX}/nanny_eda_nanny-5_stable',
        ),
        ('eda_nanny-5_testing', services_module.ClusterType.NANNY, None),
    ]
    for direct_link, cluster_type, expected_grafana_link in expected_links:
        grafana_link = web_context.grafana_links.get_by_direct_link(
            direct_link, cluster_type,
        )
        assert grafana_link == expected_grafana_link
