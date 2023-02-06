import pytest

from clownductor.internal.tasks import cubes


def task_data(name='name'):
    return {
        'id': 123,
        'job_id': 456,
        'name': name,
        'sleep_until': 0,
        'input_mapping': {},
        'output_mapping': {},
        'payload': {},
        'retries': 0,
        'status': 'in_progress',
        'error_message': None,
        'created_at': 0,
        'updated_at': 0,
    }


@pytest.mark.parametrize('is_uservices', [True, False])
async def test_send_yp_podsets_to_solomon(
        web_context, nanny_yp_mockserver, solomon_mockserver, is_uservices,
):
    nanny_yp_mockserver()
    mock = solomon_mockserver()

    env = 'unstable'
    regions = ['region1', 'region2']
    name = 'some-name'

    cube = cubes.CUBES['SendYpPodsetsToSolomon'](
        web_context,
        task_data('SendYpPodsetsToSolomon'),
        {
            'env': env,
            'nanny_name': name,
            'regions': regions,
            'is_uservices': is_uservices,
            'is_stq': False,
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert mock.has_calls

    putted_regions = set()
    calls = []
    while mock.has_calls:
        call = mock.next_call()
        calls.append(call)
        if call['request'].method == 'PUT':
            data = call['request'].json
            putted_regions.update({x['cluster'] for x in data['ypClusters']})

    expected_paths = {
        '/client-api-solomon/projects/taxi/clusters/taxi_unstable',
    }
    if is_uservices:
        expected_paths.add(
            (
                '/client-api-solomon/projects/taxi/clusters'
                '/taxi_unstable_uservices'
            ),
        )
    assert expected_paths == {x['request'].path for x in calls}
    assert len(calls) == (4 if is_uservices else 2)

    assert putted_regions == {'region1', 'region2', 'test-cluster'}
