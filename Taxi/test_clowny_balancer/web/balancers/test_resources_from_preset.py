import pytest

DATACENTER_INSTANCES = {'vla': 1, 'man': 1, 'sas': 1, 'myt': 1, 'iva': 1}
DEFAULT_BW = 1

ROOT_VOLUME = {
    'type': 'hdd',
    'size': 512,
    'path': '/',
    'bandwidth_guarantee_mb_per_sec': 1,
    'bandwidth_limit_mb_per_sec': 1,
}

ROOT_VOLUME_HIGH = {
    'type': 'hdd',
    'size': 512,
    'path': '/',
    'bandwidth_guarantee_mb_per_sec': 5,
    'bandwidth_limit_mb_per_sec': 5,
}

AWACS_VOLUME = {
    'type': 'hdd',
    'size': 120,
    'path': '/awacs',
    'bandwidth_guarantee_mb_per_sec': 1,
    'bandwidth_limit_mb_per_sec': 1,
}

LOGS_VOLUME_NANO_HIGH = {
    'type': 'hdd',
    'size': 10240,
    'path': '/logs',
    'bandwidth_guarantee_mb_per_sec': 9,
    'bandwidth_limit_mb_per_sec': 24,
}

LOGS_VOLUME_NANO = {
    'type': 'hdd',
    'size': 10240,
    'path': '/logs',
    'bandwidth_guarantee_mb_per_sec': 1,
    'bandwidth_limit_mb_per_sec': 1,
}


@pytest.mark.parametrize(
    'project_name, preset_name, io_intensity, '
    'request_dc, expected_dc, expected_response',
    [
        pytest.param(
            'test-project',
            'NANO',
            'HIGH',
            None,
            {'vla': 1, 'man': 1, 'sas': 1},
            {
                'cpu': 0.5,
                'ram': 1.5,
                'persistent_volumes': [LOGS_VOLUME_NANO_HIGH, AWACS_VOLUME],
                'root_volume': ROOT_VOLUME_HIGH,
            },
            id='test NANO preset',
        ),
        pytest.param(
            'test-project',
            'NANO',
            'NORMAL',
            None,
            {'vla': 1, 'man': 1, 'sas': 1},
            {
                'cpu': 0.5,
                'ram': 1.5,
                'persistent_volumes': [LOGS_VOLUME_NANO, AWACS_VOLUME],
                'root_volume': ROOT_VOLUME,
            },
            id='test NANO preset low io_intensity',
        ),
        pytest.param(
            'test-project',
            'NANO',
            'HIGH',
            {'vla': 5, 'man': 0, 'sas': 2, 'myt': 5, 'iva': 0},
            {'vla': 5, 'man': 0, 'sas': 2, 'myt': 5, 'iva': 0},
            {
                'cpu': 0.5,
                'ram': 1.5,
                'persistent_volumes': [LOGS_VOLUME_NANO_HIGH, AWACS_VOLUME],
                'root_volume': ROOT_VOLUME_HIGH,
            },
            id='test NANO preset with custom dc',
        ),
        pytest.param(
            'some-project',
            'NANO',
            'HIGH',
            None,
            {'vla': 1, 'man': 1, 'sas': 1},
            {
                'cpu': 0.5,
                'ram': 1.5,
                'persistent_volumes': [LOGS_VOLUME_NANO_HIGH, AWACS_VOLUME],
                'root_volume': ROOT_VOLUME_HIGH,
            },
            id='test NANO preset with unknown project_name',
        ),
    ],
)
@pytest.mark.config(
    CLOWNDUCTOR_AVAILABLE_DATACENTERS={
        'all_datacenters': ['vla', 'man', 'sas', 'iva', 'myt'],
        'projects': [
            {'datacenters': ['vla', 'iva', 'sas'], 'name': '__default__'},
            {'datacenters': ['vla', 'sas', 'myt'], 'name': 'test-project'},
        ],
    },
)
async def test_get_resources(
        taxi_clowny_balancer_web,
        project_name,
        preset_name,
        io_intensity,
        request_dc,
        expected_dc,
        expected_response,
):
    request_body = {
        'preset': preset_name,
        'project_name': project_name,
        'io_intensity': io_intensity,
    }
    if request_dc:
        request_body['datacenter_instances'] = request_dc

    response = await taxi_clowny_balancer_web.post(
        '/balancers/v1/resources/convert/',
        json=request_body,
        headers={'X-Yandex-Login': 'azhuchkov'},
    )

    expected_resources = expected_response.copy()
    expected_resources['datacenter_instances'] = DATACENTER_INSTANCES
    if expected_dc:
        expected_resources['datacenter_instances'] = expected_dc

    response_json = await response.json()
    assert response.status == 200
    assert response_json == expected_resources


@pytest.mark.parametrize(
    'project_name, preset_name, datacenter_instances',
    [('test-project', 'OHNOOOOO', None), (None, 'NANO', None)],
)
@pytest.mark.config(
    CLOWNDUCTOR_AVAILABLE_DATACENTERS={
        'all_datacenters': ['vla', 'man', 'sas', 'iva', 'myt'],
    },
)
async def test_get_resources_error(
        taxi_clowny_balancer_web,
        project_name,
        preset_name,
        datacenter_instances,
):
    request_body = {'preset': preset_name}
    if project_name:
        request_body['project_name'] = project_name
    if datacenter_instances:
        request_body['datacenter_instances'] = datacenter_instances

    response = await taxi_clowny_balancer_web.post(
        '/balancers/v1/resources/convert/',
        json=request_body,
        headers={'X-Yandex-Login': 'azhuchkov'},
    )

    response_json = await response.json()
    assert response.status == 400, response_json
