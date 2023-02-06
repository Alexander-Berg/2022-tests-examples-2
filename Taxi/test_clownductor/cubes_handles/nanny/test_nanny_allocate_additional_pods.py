import pytest

from clownductor.internal.tasks.cubes import cube


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
                    make_pod('taxi-clownductor-stable-iva-0'),
                    make_pod('taxi-clownductor-stable-iva-1'),
                    make_pod('taxi-clownductor-stable-iva-2', 'UNKNOWN'),
                ],
            }
        if cluster == 'SAS':
            return {
                'total': 2,
                'pods': [
                    make_pod('taxi-clownductor-stable-sas-0'),
                    make_pod('taxi-clownductor-stable-sas-1', 'UNKNOWN'),
                ],
            }
        if cluster == 'VLA':
            return {
                'total': 1,
                'pods': [make_pod('taxi-clownductor-stable-vla-0')],
            }

        return {'total': 0, 'pods': []}

    return _handler


@pytest.mark.parametrize(
    'file_name',
    [
        pytest.param(
            'NannyAllocateAdditionalPodsServiceIncrease',
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES_PER_SERVICE={
                    '__default__': {},
                    'test_project': {
                        'test_service': {'enable_ratelimit_mask_change': True},
                        '__default__': {},
                    },
                },
                CLOWNDUCTOR_NETWORK_GUARANTEE_SETTINGS_PER_SERVICE={
                    '__default__': {
                        '__default__': {'network_guarantee_coefficient': 8},
                    },
                    'test_project': {
                        '__default__': {'network_guarantee_coefficient': 12},
                        'test_service': {'network_guarantee_coefficient': 16},
                    },
                },
            ),
            id='test_cube_request_data_enlarge',
        ),
        pytest.param(
            'NannyAllocateAdditionalPodsServiceDownsize',
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES_PER_SERVICE={
                    '__default__': {},
                    'test_project': {
                        'test_service': {'enable_ratelimit_mask_change': True},
                        '__default__': {},
                    },
                },
            ),
            id='test_cube_request_data_downsize',
        ),
        pytest.param(
            'NannyAllocateAdditionalPodsServiceDownsizeUnknown',
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES_PER_SERVICE={
                    '__default__': {},
                    'test_project': {
                        'test_service': {
                            'enable_ratelimit_mask_change': True,
                            'delete_unknown_pods_from_snapshot': True,
                        },
                        '__default__': {},
                    },
                },
            ),
            id='test_cube_request_data_downsize_with_unknown_pods',
        ),
    ],
)
@pytest.mark.features_on('use_network_guarantee_config')
async def test_nanny_allocate_additional_pods(
        load_json,
        call_cube_handle,
        mockserver,
        file_name,
        nanny_yp_mockserver,
        nanny_yp_list_pods,
):
    nanny_yp_mockserver()
    json_data = load_json(f'{file_name}.json')

    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-sets/CreatePods/',
    )
    async def request(request):
        assert json_data['request_expected'] == request.json
        return {'podIds': ['s7ajherhpvykeclh']}

    cube_name = 'NannyAllocateAdditionalPods'
    await call_cube_handle(cube_name, json_data)
    if json_data.get('request_expected'):
        assert request.times_called == 1


@pytest.mark.parametrize(
    'ranges, value_for_remove, expected',
    [
        ('', 1, ''),
        ('1', 1, ''),
        ('0', 1, '0'),
        ('2', 1, '2'),
        ('1-127', 1, '2-127'),
        ('0-127', 1, '0,2-127'),
        ('0-1,3-127', 1, '0,3-127'),
        ('1-3,5-127', 1, '2-3,5-127'),
        ('1,3-127', 1, '3-127'),
        ('0,3,5-127', 3, '0,5-127'),
        ('0-1,3,5-127', 3, '0-1,5-127'),
        ('0-1,3,5-7,9,11-127', 3, '0-1,5-7,9,11-127'),
        ('1-127', 127, '1-126'),
    ],
)
def test_remove_value_from_ranges(ranges, value_for_remove, expected):
    assert cube.remove_type_from_value(ranges, value_for_remove) == expected
