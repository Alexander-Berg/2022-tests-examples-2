import pytest


@pytest.mark.parametrize(
    ['abc_slug', 'description', 'updated'],
    [('test-slug', 'test-desription', True), (None, None, False)],
)
async def test_update_service_info_attrs(
        call_cube_handle,
        abc_slug,
        description,
        updated,
        abc_mockserver,
        nanny_mockserver,
):
    abc_mock = abc_mockserver(services=['test-slug'])
    await call_cube_handle(
        'NannyUpdateServiceInfoAttrs',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': {
                    'service_abc': abc_slug,
                    'description': description,
                    'nanny_name': 'test-nanny-service',
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert nanny_mockserver.get_info_attrs.times_called == 1
    if updated:
        assert abc_mock.times_called == 1
        assert nanny_mockserver.put_info_attrs.times_called == 1
        update_call = nanny_mockserver.put_info_attrs.next_call()
        assert update_call.body.keys() == {'content', 'comment', 'snapshot_id'}
        assert (
            update_call.body['comment']
            == 'Automated change of info attrs by clownductor'
        )
        assert update_call.body['content']['abc_group'] == 3155
        assert update_call.body['content']['desc'] == description
    else:
        assert not abc_mock.times_called
        assert not nanny_mockserver.put_info_attrs.times_called
