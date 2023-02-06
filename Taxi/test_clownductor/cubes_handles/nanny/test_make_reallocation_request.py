import pytest


@pytest.mark.parametrize('with_non_auto_policy', [True, False])
@pytest.mark.features_on('enable_update_root_io_limit')
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.config(
    CLOWNDUCTOR_REALLOCATION_PARAMS={
        '__default__': {
            'max_unvailable_pods': 1,
            'min_update_delay_seconds': 300,
        },
        'test_project': {
            '__default__': {
                'max_unvailable_pods': 2,
                'min_update_delay_seconds': 600,
            },
            'test_service': {
                'max_unvailable_pods': 5,
                'min_update_delay_seconds': 200,
            },
        },
    },
)
async def test_make_request_reallocation(
        call_cube_handle, prepared_allocation_request, with_non_auto_policy,
):
    payload_allocation_request = prepared_allocation_request.copy()
    payload_allocation_request['vcpuLimit'] = 1440
    payload_allocation_request['vcpuGuarantee'] = 1440
    payload_allocation_request['rootBandwidthGuaranteeMegabytesPerSec'] = 3
    payload_allocation_request['rootBandwidthLimitMegabytesPerSec'] = 6

    input_allocation_request = prepared_allocation_request.copy()
    if with_non_auto_policy:
        input_allocation_request['anonymousMemoryLimitMegabytes'] = 1000
    await call_cube_handle(
        'MakeReallocationRequest',
        {
            'content_expected': {
                'payload': {
                    'allocation_request': payload_allocation_request,
                    'degrade_params': {
                        'maxUnavailablePods': 5,
                        'minUpdateDelaySeconds': 200,
                    },
                },
                'status': 'success',
            },
            'data_request': {
                'input_data': {
                    'changes': {
                        'mem': 2048,
                        'cpu': 1440,
                        'root_bandwidth_guarantee_mb_per_sec': 3,
                    },
                    'original_allocation_request': input_allocation_request,
                    'project_name': 'test_project',
                    'service_name': 'test_service',
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
