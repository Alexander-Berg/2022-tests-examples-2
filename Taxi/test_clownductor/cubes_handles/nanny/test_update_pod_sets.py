import pytest


@pytest.mark.parametrize(
    'input_data, nanny_yp_mock_calls',
    [
        pytest.param(
            {
                'service_abc': 'test-slug',
                'nanny_name': 'test-nanny-service',
                'regions': ['VLA', 'SAS'],
            },
            4,
        ),
        pytest.param(
            {
                'service_abc': 'test-slug',
                'nanny_name': 'test-nanny-service',
                'regions': [],
                'region': 'VLA',
            },
            2,
        ),
    ],
)
async def test_update_pod_sets(
        call_cube_handle,
        abc_mockserver,
        nanny_yp_mockserver,
        input_data,
        nanny_yp_mock_calls,
):
    abc_mock = abc_mockserver(services=['test-slug'])
    nanny_yp_mock = nanny_yp_mockserver()

    await call_cube_handle(
        'NannyUpdatePodSets',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': input_data,
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert abc_mock.times_called == 1
    assert nanny_yp_mock.times_called == nanny_yp_mock_calls
    for _ in range(nanny_yp_mock_calls // 2):
        nanny_yp_mock.next_call()
    clusters = input_data['regions'] or [input_data['region']]
    clusters_set = set(clusters)
    for _ in range(len(clusters)):
        req = nanny_yp_mock.next_call()['request']
        body = req.json
        cluster = body.pop('cluster')
        clusters_set.remove(cluster)
        assert req.json == {
            'antiaffinityConstraints': {
                'nodeMaxPods': '1',
                'podGroupIdPath': '',
            },
            'nodeAffinity': {'networkCapacity': 'DEFAULT'},
            'quotaSettings': {'abcServiceId': 3155, 'mode': 'ABC_SERVICE'},
            'serviceId': 'test-nanny-service',
            'version': '6371ad16-770c-4c83-a993-bbc8f6d9afdd',
        }
    assert not clusters_set
