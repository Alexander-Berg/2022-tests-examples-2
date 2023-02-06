import pytest


@pytest.mark.features_on('enable_hejmdal_notifications')
async def test_notify_hejmdal_deploy_event_start(
        call_cube_handle, hejmdal_start_event,
):
    mock = hejmdal_start_event
    await call_cube_handle(
        'NotifyHejmdalDeployEvent',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': {
                    'service_id': 999,
                    'env': 0,
                    'state': 0,
                    'skip_prestable': False,
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert mock.times_called == 1
    assert mock.next_call()['request'].json == {
        'env': 'prestable',
        'event_type': 'deploy',
        'service_id': 999,
    }


@pytest.mark.features_on('enable_hejmdal_notifications')
async def test_notify_hejmdal_deploy_event_finish(
        call_cube_handle, hejmdal_finish_event,
):
    mock = hejmdal_finish_event
    await call_cube_handle(
        'NotifyHejmdalDeployEvent',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': {
                    'service_id': 999,
                    'env': 1,
                    'state': 1,
                    'skip_prestable': False,
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert mock.times_called == 1
    assert mock.next_call()['request'].json == {
        'env': 'stable',
        'event_type': 'deploy',
        'service_id': 999,
    }
