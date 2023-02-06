import pytest


@pytest.fixture(name='nanny_yp_list_pods')
def _nanny_yp_list_pods(mockserver):
    def make_pod(pod_id: str, state: str = 'ACTIVE'):
        return {
            'status': {
                'agent': {'iss': {'currentStates': [{'currentState': state}]}},
            },
            'meta': {'creationTime': '1628931000883990', 'id': pod_id},
        }

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _handler(request):
        data = request.json
        cluster = data['cluster']

        if cluster == 'IVA':
            return {
                'total': 3,
                'pods': [
                    make_pod('IVA_old_0'),
                    make_pod('IVA_old_1'),
                    make_pod('IVA_old_2', 'UNKNOWN'),
                ],
            }
        if cluster == 'SAS':
            return {
                'total': 5,
                'pods': [
                    make_pod('SAS_old_0'),
                    make_pod('SAS_old_1'),
                    make_pod('SAS_old_2'),
                    make_pod('SAS_old_3'),
                    make_pod('SAS_old_4', 'UNKNOWN'),
                ],
            }
        if cluster == 'VLA':
            return {'total': 1, 'pods': [make_pod('VLA_old_0')]}

        return {'total': 0, 'pods': []}

    return _handler


@pytest.mark.usefixtures('mocks_for_service_creation')
@pytest.mark.features_on(
    'use_cube_allocate_all_additional_pods', 'use_network_guarantee_config',
)
@pytest.mark.parametrize(
    'file_name, yp_handler_calls',
    [
        pytest.param(
            'NannyAllocateAllRegionsAdditionalPods',
            2,
            id='delete active pods',
        ),
        pytest.param(
            'NannyAllocateAllRegionsAdditionalPodsUnknown',
            1,
            id='delete active and unknown pods',
            marks=pytest.mark.features_on('delete_unknown_pods_from_snapshot'),
        ),
    ],
)
async def test_cube_allocate_all_regions(
        load_json,
        nanny_mockserver,
        nanny_yp_mockserver,
        add_service,
        add_nanny_branch,
        call_cube_handle,
        mockserver,
        nanny_yp_list_pods,
        file_name,
        yp_handler_calls,
):
    nanny_yp_mockserver()

    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-sets/CreatePods/',
    )
    def yp_handler(*args, **kwargs):
        data = args[0].json
        cluster = data['cluster']
        network_bw_guarantee = data['allocationRequest'][
            'networkBandwidthGuaranteeMegabytesPerSec'
        ]
        network_bw_limit = data['allocationRequest'][
            'networkBandwidthLimitMegabytesPerSec'
        ]
        assert network_bw_guarantee == 8
        assert network_bw_limit == 0
        snapshots_count = data['allocationRequest']['replicas']
        return {
            'podIds': [f'{cluster}_new_{i}' for i in range(snapshots_count)],
        }

    await add_service(
        project_name='taxi',
        service_name='test-service',
        direct_link='taxi_test-service',
    )
    await add_nanny_branch(service_id=1, branch_name='test-branch')

    json_datas = load_json(f'{file_name}.json')
    for json_data in json_datas:
        await call_cube_handle(
            'NannyAllocateAllRegionsAdditionalPods', json_data,
        )
    assert yp_handler.times_called == yp_handler_calls
