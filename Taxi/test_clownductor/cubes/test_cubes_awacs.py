import pytest

from clownductor.internal.tasks import cubes


def task_data(name):
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


@pytest.mark.parametrize('endpointset_in_awacs_backends', [True, False])
async def test_awacs_get_namespace_for_service(
        web_context, awacs_mockserver, endpointset_in_awacs_backends,
):
    awacs_mockserver(
        endpointset_in_awacs_backends=endpointset_in_awacs_backends,
    )

    cube = cubes.CUBES['AwacsGetNamespaceForService'](
        web_context,
        task_data('AwacsGetNamespaceForService'),
        {'nanny_name': 'khomikki-test-1', 'environment': 'stable'},
        [],
        None,
    )

    await cube.update()

    if endpointset_in_awacs_backends:
        assert cube.failed
    else:
        assert cube.success
