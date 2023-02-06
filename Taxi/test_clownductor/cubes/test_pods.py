import pytest

from clownductor.internal.tasks import cubes


def task_data(name):
    return {
        'id': 123,
        'job_id': 456,
        'name': name,
        'sleep_until': 0,
        'input_mapping': {},
        'output_mapping': {},
        'payload': {},
        'retries': 0,
        'status': 'in_progress',
        'error_message': None,
        'created_at': 0,
        'updated_at': 0,
    }


async def test_nanny_cube_create(
        nanny_mockserver, nanny_yp_mockserver, abc_mockserver, web_context,
):
    abc_mockserver()
    nanny_yp_mockserver()

    cube = cubes.CUBES['NannyCubeCreate'](
        web_context,
        task_data('NannyCubeCreate'),
        {
            'name': 'taxi_kitty_unstable',
            'project': 'taxi',
            'service': 'kitty',
            'branch': 'unstable',
            'service_abc': 'someabcslug',
            'description': 'another fake service',
            'secret_id': 'sec-XXX',
            'secret_version': 'sec-YYY',
            'secret_delegation_token': 'del_toc_123',
            'new_service_ticket': 'TAXIADMIN-1',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success


# pylint: disable=invalid-name
@pytest.mark.features_on('use_new_params_in_cube_addpodstodeploy')
async def test_nanny_cube_add_pods_to_deploy(
        nanny_mockserver, nanny_yp_mockserver, web_context,
):
    nanny_yp_mockserver()

    cube = cubes.CUBES['NannyCubeAddPodsToDeploy'](
        web_context,
        task_data('NannyCubeAddPodsToDeploy'),
        {
            'name': 'taxi_kitty_unstable',
            'regions': ['man', 'sas'],
            'pods_ids_by_region': {},
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success


# pylint: disable=invalid-name
async def test_nanny_cube_remove_pods_from_deploy(
        nanny_mockserver, nanny_yp_mockserver, web_context,
):
    nanny_yp_mockserver()

    cube = cubes.CUBES['NannyCubeRemovePodsFromDeploy'](
        web_context,
        task_data('NannyCubeRemovePodsFromDeploy'),
        {
            'name': 'taxi_kitty_unstable',
            'vla_pods_ids_to_remove': ['jpa75d4ifcp724r2', 'znuucofbn3ix2ag2'],
            'sas_pods_ids_to_remove': None,
            'man_pods_ids_to_remove': [],
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success


async def test_nanny_get_pods(
        nanny_mockserver, nanny_yp_mockserver, staff_mockserver, web_context,
):
    nanny_yp_mockserver()
    staff_mockserver()

    cube = cubes.CUBES['NannyGetPods'](
        web_context,
        task_data('NannyGetPods'),
        {'nanny_name': 'balancer_taxi_kitty_unstable_man'},
        [],
        None,
    )

    await cube.update()

    assert cube.success

    assert cube.data['payload']['region'] == 'man'
    assert cube.data['payload']['pod_ids'] == [
        'jpa75d4ifcp724r2',
        'znuucofbn3ix2ag2',
    ]


@pytest.mark.parametrize('use_active', [True, False])
async def test_nanny_get_service_pods(
        nanny_mockserver,
        nanny_yp_mockserver,
        staff_mockserver,
        web_context,
        use_active,
        mockserver,
):
    nanny_yp_mockserver()
    staff_mockserver()

    @mockserver.json_handler(
        '/client-nanny/v2/services/'
        'balancer_taxi_kitty_unstable/runtime_attrs/',
    )
    def _request(request):
        return {
            '_id': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
            'content': {
                'instances': {
                    'yp_pod_ids': {
                        'pods': [
                            {'cluster': 'VLA', 'pod_id': 'znuucofbn3ix2ag2'},
                            {'cluster': 'MAN', 'pod_id': 'jpa75d4ifcp724r2'},
                        ],
                    },
                },
            },
        }

    body = {'nanny_name': 'balancer_taxi_kitty_unstable'}
    if use_active:
        body['use_active'] = True
    cube = cubes.CUBES['NannyGetServicePods'](
        web_context, task_data('NannyGetServicePods'), body, [], None,
    )

    await cube.update()
    assert cube.success

    pod_ids = ['jpa75d4ifcp724r2', 'znuucofbn3ix2ag2']
    man_expected = pod_ids if not use_active else ['jpa75d4ifcp724r2']
    vla_expected = pod_ids if not use_active else ['znuucofbn3ix2ag2']
    sas_expected = pod_ids if not use_active else []
    iva_expected = pod_ids if not use_active else []
    myt_expected = pod_ids if not use_active else []
    assert cube.data['payload'] == {
        'man': man_expected,
        'vla': vla_expected,
        'sas': sas_expected,
        'pod_ids_by_region': {
            'iva': iva_expected,
            'man': man_expected,
            'myt': myt_expected,
            'sas': sas_expected,
            'vla': vla_expected,
        },
        'vla_region': 'vla',
        'man_region': 'man',
        'sas_region': 'sas',
    }


async def test_nanny_get_pod_info(
        nanny_mockserver, nanny_yp_mockserver, staff_mockserver, web_context,
):
    nanny_yp_mockserver()
    staff_mockserver()

    cube = cubes.CUBES['NannyGetPodsInfo'](
        web_context,
        task_data('NannyGetPodsInfo'),
        {'pod_ids': ['jpa75d4ifcp724r2', 'znuucofbn3ix2ag2'], 'region': 'man'},
        [],
        None,
    )

    await cube.update()

    assert cube.success

    pod_info = cube.data['payload']['pod_info']
    assert pod_info['mem'] == 2048
    assert pod_info['cpu'] == 1000
    assert pod_info['network'] == '_TAXITESTNETS_'
    assert pod_info['logs_quota'] == 10240
    assert pod_info['root_fs_quota_mb'] == 512
    assert pod_info['work_dir_quota'] == 512


async def test_allocate_additional_pod(
        nanny_mockserver, nanny_yp_mockserver, staff_mockserver, web_context,
):
    nanny_yp_mockserver()
    staff_mockserver()

    cube = cubes.CUBES['NannyAllocateAdditionalPods'](
        web_context,
        task_data('NannyAllocateAdditionalPods'),
        {
            'pod_info': {
                'cpu': 1000,
                'mem': 2048,
                'network': '_TAXITESTNETS_',
                'logs_quota': 10240,
                'root_fs_quota_mb': 512,
                'work_dir_quota': 512,
                'sysctl': [
                    {'name': 'net.ipv4.tcp_tw_reuse', 'value': '1'},
                    {'name': 'net.ipv4.tcp_retries2', 'value': '8'},
                ],
            },
            'region': 'man',
            'nanny_name': 'some-service',
            'slb_fqdn': 'some-service.taxi.yandex.net',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success

    assert cube.data['payload']['new_pod_ids'] == ['s7ajherhpvykeclh']


async def test_allocate_additional_pod_bad_request(
        web_context, patch, nanny_mockserver, nanny_yp_mockserver, mockserver,
):
    nanny_yp_mockserver()

    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-sets/CreatePods/',
    )
    def yp_handler(_):
        return mockserver.make_response(status=400)

    cube = cubes.CUBES['NannyAllocateAdditionalPods'](
        web_context,
        task_data('NannyAllocateAdditionalPods'),
        {
            'pod_info': {
                'cpu': 1000,
                'mem': 2048,
                'network': '_TAXITESTNETS_',
                'logs_quota': 10240,
                'root_fs_quota_mb': 512,
                'work_dir_quota': 512,
                'sysctl': [
                    {'name': 'net.ipv4.tcp_tw_reuse', 'value': '1'},
                    {'name': 'net.ipv4.tcp_retries2', 'value': '8'},
                ],
            },
            'region': 'man',
            'nanny_name': 'some-service',
            'slb_fqdn': 'some-service.taxi.yandex.net',
        },
        [],
        None,
    )

    await cube.update()
    assert yp_handler.times_called == 1
    assert cube.in_progress


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'add_pod_with_request_id': True})
async def test_allocate_additional_pod_retry(
        nanny_mockserver,
        nanny_yp_mockserver,
        staff_mockserver,
        web_context,
        patch,
):
    nanny_yp_mockserver()
    staff_mockserver()

    @patch('clownductor.internal.tasks.cubes.cube.TaskCube.sleep')
    def _sleep(duration, error=False):
        pass

    cube = cubes.CUBES['NannyAllocateAdditionalPods'](
        web_context,
        task_data('NannyAllocateAdditionalPods'),
        {
            'pod_info': {
                'cpu': 1000,
                'mem': 2048,
                'network': '_TAXITESTNETS_',
                'logs_quota': 10240,
                'root_fs_quota_mb': 512,
                'work_dir_quota': 512,
                'sysctl': [
                    {'name': 'net.ipv4.tcp_tw_reuse', 'value': '1'},
                    {'name': 'net.ipv4.tcp_retries2', 'value': '8'},
                ],
            },
            'region': 'man',
            'nanny_name': 'some-service',
            'slb_fqdn': 'some-service.taxi.yandex.net',
        },
        [],
        None,
    )

    await cube.update()
    assert cube.status == 'in_progress'

    await cube.update()
    assert cube.status == 'in_progress'

    await cube.update()
    assert cube.success

    assert cube.data['payload']['new_pod_ids'] == ['yveclebcqmnnmr2j']


async def test_nanny_remove_pod(
        nanny_mockserver, nanny_yp_mockserver, staff_mockserver, web_context,
):
    nanny_yp_mockserver()
    staff_mockserver()

    cube = cubes.CUBES['NannyRemovePods'](
        web_context,
        task_data('NannyRemovePods'),
        {'pod_ids': ['jpa75d4ifcp724r2', 'znuucofbn3ix2ag2'], 'region': 'man'},
        [],
        None,
    )

    await cube.update()

    assert cube.success
