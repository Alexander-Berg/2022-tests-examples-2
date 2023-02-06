import json

import pytest

from clownductor.internal.utils import postgres


@pytest.fixture(name='clowny_balancer_convert_resources')
def _clowny_balancer_convert_resources(mockserver, mock_clowny_balancer):
    @mock_clowny_balancer('/balancers/v1/resources/convert/')
    def _handler(request):
        assert request.json['preset'] == 'MICRO'
        awacs_volume = {
            'type': 'hdd',
            'size': 120,
            'path': '/awacs',
            'bandwidth_guarantee_mb_per_sec': 1,
            'bandwidth_limit_mb_per_sec': 1,
        }

        if request.json['io_intensity'] == 'NORMAL':
            root_volume = {
                'type': 'hdd',
                'size': 512,
                'path': '/',
                'bandwidth_guarantee_mb_per_sec': 1,
                'bandwidth_limit_mb_per_sec': 1,
            }
            logs_volume = {
                'type': 'hdd',
                'size': 10240,
                'path': '/logs',
                'bandwidth_guarantee_mb_per_sec': 1,
                'bandwidth_limit_mb_per_sec': 1,
            }
        else:
            root_volume = {
                'type': 'hdd',
                'size': 512,
                'path': '/',
                'bandwidth_guarantee_mb_per_sec': 5,
                'bandwidth_limit_mb_per_sec': 5,
            }
            logs_volume = {
                'type': 'hdd',
                'size': 10240,
                'path': '/logs',
                'bandwidth_guarantee_mb_per_sec': 9,
                'bandwidth_limit_mb_per_sec': 24,
            }

        if request.json.get('datacenter_instances'):
            datacenter_instances = request.json['datacenter_instances']
        else:
            datacenter_instances = {'man': 1, 'sas': 1, 'vla': 1}

        return {
            'cpu': 1.0,
            'ram': 2.0,
            'datacenter_instances': datacenter_instances,
            'persistent_volumes': [logs_volume, awacs_volume],
            'root_volume': root_volume,
        }

    return _handler


async def _get_parameters(web_context, service_id, branch_id, subsystem_name):
    new_rows = []
    async with postgres.primary_connect(web_context) as conn:
        rows = await conn.fetch(
            """
            select
                p.id,
                p.subsystem_name,
                p.service_id,
                p.branch_id,
                p.remote_values,
                p.service_values
            from
                clownductor.parameters p
            where
                p.service_id = $1
                and p.branch_id = $2
            """,
            service_id,
            branch_id,
        )
    for row in rows:
        if (
                subsystem_name is not None
                and row['subsystem_name'] != subsystem_name
        ):
            continue
        row = dict(row)
        row['remote_values'] = json.loads(row['remote_values'])
        row['service_values'] = json.loads(row['service_values'])
        new_rows.append(row)
    return new_rows


@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
@pytest.mark.parametrize(
    'service_id,branch_id,expected_params',
    [
        pytest.param(
            1,
            1,
            [
                {
                    'service_values': {
                        'clownductor_project': 'taxi-devops',
                        'duty': {
                            'abc_slug': 'some_abc',
                            'primary_schedule': 'some_schedule',
                        },
                        'duty_group_id': None,
                    },
                    'subsystem_name': 'service_info',
                },
                {
                    'service_values': {
                        'cpu': 2000,
                        'datacenters_count': 2,
                        'datacenters_regions': ['vla', 'man', 'sas'],
                        'instances': 1,
                        'network_bandwidth_guarantee_mb_per_sec': 16,
                        'persistent_volumes': [],
                        'ram': 8192,
                        'root_bandwidth_guarantee_mb_per_sec': 1,
                        'root_bandwidth_limit_mb_per_sec': 2,
                        'root_size': 10240,
                        'root_storage_class': 'hdd',
                        'work_dir': 256,
                    },
                    'subsystem_name': 'nanny',
                },
                {
                    'service_values': {
                        'cpu': 1000,
                        'datacenters_instances': {
                            'man': 1,
                            'sas': 1,
                            'vla': 1,
                        },
                        'persistent_volumes': [
                            {
                                'bandwidth_guarantee_mb_per_sec': 9,
                                'bandwidth_limit_mb_per_sec': 24,
                                'path': '/logs',
                                'size': 10240,
                                'storage_class': 'hdd',
                            },
                            {
                                'bandwidth_guarantee_mb_per_sec': 1,
                                'bandwidth_limit_mb_per_sec': 1,
                                'path': '/awacs',
                                'size': 120,
                                'storage_class': 'hdd',
                            },
                        ],
                        'ram': 2048,
                        'root_volume': {
                            'bandwidth_guarantee_mb_per_sec': 5,
                            'bandwidth_limit_mb_per_sec': 5,
                            'path': '/',
                            'size': 512,
                            'storage_class': 'hdd',
                        },
                    },
                    'subsystem_name': 'awacs',
                },
                {
                    'service_values': {
                        'description': {
                            'en': (
                                'You can find general information '
                                'about service on wiki page: '
                                'https://wiki.yandex-team.ru'
                            ),
                            'ru': (
                                'Подробную информацию о сервисе '
                                'можно узнать на странице в wiki: '
                                'https://wiki.yandex-team.ru'
                            ),
                        },
                        'maintainers': ['azhuchkov'],
                        'service_name': {
                            'en': 'taxi-devops/service_exist',
                            'ru': 'taxi-devops/service_exist',
                        },
                    },
                    'subsystem_name': 'abc',
                },
            ],
            id='preset:MICRO, instances defined, io_intensity:HIGH',
        ),
        pytest.param(
            1,
            2,
            [
                {
                    'service_values': {
                        'cpu': 1000,
                        'instances': 3,
                        'datacenters_count': 2,
                        'datacenters_regions': ['vla', 'man', 'sas'],
                        'persistent_volumes': [],
                        'ram': 2048,
                        'root_size': 10240,
                        'work_dir': 256,
                        'root_storage_class': 'hdd',
                        'root_bandwidth_guarantee_mb_per_sec': 1,
                        'root_bandwidth_limit_mb_per_sec': 2,
                        'network_bandwidth_guarantee_mb_per_sec': 8,
                    },
                    'subsystem_name': 'nanny',
                },
                {
                    'service_values': {
                        'cpu': 1000,
                        'datacenters_instances': {
                            'man': 1,
                            'sas': 1,
                            'vla': 1,
                        },
                        'persistent_volumes': [
                            {
                                'bandwidth_guarantee_mb_per_sec': 1,
                                'bandwidth_limit_mb_per_sec': 1,
                                'path': '/logs',
                                'size': 10240,
                                'storage_class': 'hdd',
                            },
                            {
                                'bandwidth_guarantee_mb_per_sec': 1,
                                'bandwidth_limit_mb_per_sec': 1,
                                'path': '/awacs',
                                'size': 120,
                                'storage_class': 'hdd',
                            },
                        ],
                        'ram': 2048,
                        'root_volume': {
                            'bandwidth_guarantee_mb_per_sec': 1,
                            'bandwidth_limit_mb_per_sec': 1,
                            'path': '/',
                            'size': 512,
                            'storage_class': 'hdd',
                        },
                    },
                    'subsystem_name': 'awacs',
                },
            ],
            id='preset:MICRO, io_intensity:NORMAL',
        ),
    ],
)
@pytest.mark.features_on(
    'use_network_guarantee_config',
    'feat_duty_group_id',
    'use_remote_clownductor_project',
)
async def test_service_values_sync_awacs(
        patch_github_single_file,
        web_context,
        service_id,
        web_app_client,
        branch_id,
        expected_params,
        clowny_balancer_convert_resources,
):
    body = {'branch_id': branch_id, 'service_id': service_id}

    get_single_file = patch_github_single_file(
        'clownductor/service.yaml', 'clownductor_py3_awacs.yaml',
    )

    response = await web_app_client.post(
        '/v1/parameters/service_values/sync/',
        json=body,
        headers={'X-Yandex-Login': 'azhuchkov'},
    )
    response_body = await response.json()
    assert response_body == {}
    assert response.status == 200
    assert len(get_single_file.calls) == 1

    rows = await _get_parameters(web_context, service_id, branch_id, None)
    expected = []
    for row in rows:
        expected.append(
            {
                'subsystem_name': row['subsystem_name'],
                'service_values': row['service_values'],
            },
        )

    assert expected_params == expected
