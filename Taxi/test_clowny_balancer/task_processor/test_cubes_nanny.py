import pytest


@pytest.mark.parametrize(
    'cube_name, input_data, payload',
    [
        (
            'NannySetL7MonitoringSettings',
            {
                'service_id': 1,
                'env': 'stable',
                'nanny_service': 'rtc_balancer_some',
            },
            None,
        ),
        (
            'NannyReallocatePods',
            {'nanny_name': 'balancer_service_sas'},
            {'reallocation_id': '123abc'},
        ),
        (
            'NannyReallocatePods',
            {'nanny_name': 'balancer_service_man'},
            {'reallocation_id': '123abc'},
        ),
        (
            'NannyReallocateWaitFor',
            {
                'service_id': 'abc',
                'reallocation_id': 'sepohhmdyqm6rqljvchenwbt',
            },
            None,
        ),
    ],
)
async def test_cubes(
        mockserver,
        mock_clownductor,
        nanny_mockserver,
        call_cube,
        cube_name,
        input_data,
        payload,
        mock_get_project,
):
    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-sets/ListPodsGroups/',
    )
    def _list_pods_groups(_):
        return {
            'podsGroups': [
                {'allocationRequest': {}, 'summaries': [{'id': 'pod-1'}]},
            ],
        }

    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-reallocation/GetPodReallocationSpec/',
    )
    def _reallocation_spec(request):
        if request.json['serviceId'] == 'balancer_service_man':
            return mockserver.make_response(status=400)
        return {
            'spec': {
                'id': 'reallocation-id',
                'snapshotId': 'snapshot-id',
                'degradeParams': {
                    'maxUnavailablePods': 1,
                    'minUpdateDelaySeconds': 300,
                },
            },
        }

    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-reallocation/StartPodReallocation/',
    )
    def _start_reallocation(_):
        return {'reallocationId': '123abc'}

    @mock_clownductor('/v1/services/')
    async def _services_handler(_):
        return [
            {
                'id': 1,
                'name': 'test',
                'cluster_type': 'nanny',
                'project_id': 1,
            },
        ]

    mock_get_project('taxi')

    response = await call_cube(cube_name, input_data)
    result = {'status': 'success'}
    if payload is not None:
        result['payload'] = payload
    assert response == result
