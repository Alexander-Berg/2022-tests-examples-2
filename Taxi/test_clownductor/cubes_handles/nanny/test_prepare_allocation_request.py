import pytest


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_prepare_allocation_request(
        call_cube_handle,
        nanny_yp_list_pods_groups,
        prepared_allocation_request,
        original_allocation_request,
        mockserver,
):
    @mockserver.json_handler('/yp-api/ObjectService/SelectObjects')
    def _handler(request):
        body = request.json
        query = '[/status/pod_id]=\"taxi-clownductor-stable-4\"'
        assert body['object_type'] == 'internet_address'
        assert body['filter']['query'] == query
        value = {
            'type': 'internet_address',
            'ip4_address_pool_id': '1517:1361',
        }
        return {'result': {'values': [value]}}

    original_allocation_request['ip4AddressPoolId'] = '1517:1361'
    prepared_allocation_request['ip4AddressPoolId'] = '1517:1361'
    await call_cube_handle(
        'NannyPrepareAllocationRequest',
        {
            'content_expected': {
                'payload': {
                    'original_allocation_request': original_allocation_request,
                    'prepared_allocation_request': prepared_allocation_request,
                },
                'status': 'success',
            },
            'data_request': {
                'input_data': {
                    'nanny_name': 'test_service_stable',
                    'nanny_pod_id': 'taxi-clownductor-stable-4',
                    'region': 'MAN',
                    'reallocation_coefficient': 1.6,
                    'ignore_properties': ['memoryGuaranteeMegabytes'],
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert nanny_yp_list_pods_groups.times_called == 1
    assert _handler.times_called == 1
    call = nanny_yp_list_pods_groups.next_call()['request']
    assert call.json == {
        'cluster': 'MAN',
        'pod_filter': '[/meta/id]="taxi-clownductor-stable-4"',
        'service_id': 'test_service_stable',
    }
