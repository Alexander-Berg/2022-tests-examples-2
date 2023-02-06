import pytest


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_nanny_get_newest_pod(call_cube_handle, nanny_yp_list_pods):
    await call_cube_handle(
        'NannyGetNewestPod',
        {
            'content_expected': {
                'payload': {
                    'newest_pod_id': 'taxi-clownductor-stable-4',
                    'region': 'MAN',
                },
                'status': 'success',
            },
            'data_request': {
                'input_data': {'nanny_name': 'test_service_stable'},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert nanny_yp_list_pods.times_called == 3
    clusters = {'MAN', 'SAS', 'VLA'}
    for _ in range(3):
        call = nanny_yp_list_pods.next_call()['request']
        assert call.json['serviceId'] == 'test_service_stable'
        clusters.remove(call.json['cluster'])
    assert not clusters
