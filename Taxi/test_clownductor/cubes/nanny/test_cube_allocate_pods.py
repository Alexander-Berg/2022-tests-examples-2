import pytest


@pytest.mark.features_on('disk_profiles')
@pytest.mark.features_on('use_network_guarantee_config')
async def test_nanny_cube_allocate_pods_flag(
        mockserver,
        nanny_mockserver,
        nanny_yp_mockserver,
        abc_mockserver,
        web_context,
        get_cube,
):
    abc_mockserver()
    nanny_yp_mockserver()

    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-sets/CreatePodSet/',
    )
    def yp_handler(data):
        allocation_request = data.json['allocationRequest']
        assert (
            allocation_request.get('networkBandwidthGuaranteeMegabytesPerSec')
            == 8
        )
        assert allocation_request.get('anonymousMemoryLimitMegabytes') is None
        assert allocation_request.get('anonLimitPolicy') == 'AUTO'
        return {}

    body = {
        'name': 'taxi_kitty_unstable',
        'regions': ['man', 'sas'],
        'instances': [2, 2],
        'allocation_abc': 'someabcslug',
        'network': '_KITTY_NETS_',
        'root_size': 4096,
        'volumes': [
            {
                'path': '/cores',
                'size': 10240,
                'type': 'ssd',
                'bandwidth_guarantee_mb_per_sec': 3,
                'bandwidth_limit_mb_per_sec': 6,
            },
            {
                'path': '/logs',
                'size': 50000,
                'type': 'ssd',
                'bandwidth_guarantee_mb_per_sec': 6,
                'bandwidth_limit_mb_per_sec': 12,
            },
            {
                'path': '/var/cache/yandex',
                'size': 2048,
                'type': 'ssd',
                'bandwidth_guarantee_mb_per_sec': 3,
                'bandwidth_limit_mb_per_sec': 6,
            },
        ],
        'cpu': 1000,
        'mem': 1024,
        'work_dir': 256,
    }
    cube = get_cube('NannyCubeAllocatePods', body)
    await cube.update()

    assert cube.success
    assert yp_handler.times_called == 2
