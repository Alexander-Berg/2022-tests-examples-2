import pytest


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.parametrize(
    'degrade_params, expected_degrade_params',
    [
        pytest.param(
            {'maxUnavailablePods': 2, 'minUpdateDelaySeconds': 600},
            {'maxUnavailablePods': 2, 'minUpdateDelaySeconds': 600},
        ),
        pytest.param(
            None, {'maxUnavailablePods': 1, 'minUpdateDelaySeconds': 300},
        ),
    ],
)
async def test_pods_reallocation(
        call_cube_handle,
        nanny_mockserver,
        prepared_allocation_request,
        nanny_yp_pod_reallocation_spec,
        nanny_yp_start_pod_reallocation,
        degrade_params,
        expected_degrade_params,
):
    await call_cube_handle(
        'ClownNannyReallocatePods',
        {
            'content_expected': {
                'payload': {'reallocation_id': 'tuxuyawpnyh7qxmqnhvznnz7'},
                'status': 'success',
            },
            'data_request': {
                'input_data': {
                    'nanny_name': 'test_service_stable',
                    'allocation_request': prepared_allocation_request,
                    'degrade_params': degrade_params,
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert nanny_mockserver.get_nanny_service.times_called == 1
    assert nanny_yp_pod_reallocation_spec.times_called == 1
    assert nanny_yp_start_pod_reallocation.times_called == 1

    call = nanny_mockserver.get_nanny_service.next_call()
    assert call.nanny_name == 'test_service_stable'
    assert nanny_yp_pod_reallocation_spec.next_call()['request'].json == {
        'serviceId': 'test_service_stable',
    }
    assert nanny_yp_start_pod_reallocation.next_call()['request'].json == {
        'allocationRequest': prepared_allocation_request,
        'degradeParams': expected_degrade_params,
        'serviceId': 'test_service_stable',
        'snapshotId': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
        'previousReallocationId': 'sepohhmdyqm6rqljvchenwbt',
    }
