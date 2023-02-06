import pytest


@pytest.mark.parametrize(
    ['input_data', 'payload'],
    [
        (
            {
                'source_flavor': 's2.small',
                'flavor_change_level': 2,
                'count_hosts': 3,
                'source_ram_quota': 20 * 3 * 1024 * 1024 * 1024,
                'source_cpu_quota': 12500,
            },
            {
                'flavor': 's2.large',
                'cpu_quota': 36500,
                'ram_quota': 52 * 3 * 1024 * 1024 * 1024,
                'skip_cpu': False,
                'skip_ram': False,
                'quota_fields': {
                    'cpu': {'new': 36500, 'old': 12500},
                    'flavor': {'new': 's2.large', 'old': 's2.small'},
                    'ram': {
                        'new': 52 * 3 * 1024 * 1024 * 1024,
                        'old': 20 * 3 * 1024 * 1024 * 1024,
                    },
                },
            },
        ),
        (
            {
                'source_flavor': 's2.small',
                'flavor_change_level': -3,
                'count_hosts': 3,
                'source_ram_quota': 20 * 3 * 1024 * 1024 * 1024,
                'source_cpu_quota': 12500,
            },
            {
                'flavor': 's2.nano',
                'cpu_quota': 3500,
                'ram_quota': 8 * 3 * 1024 * 1024 * 1024,
                'skip_cpu': False,
                'skip_ram': False,
                'quota_fields': {
                    'cpu': {'new': 3500, 'old': 12500},
                    'flavor': {'new': 's2.nano', 'old': 's2.small'},
                    'ram': {
                        'new': 8 * 3 * 1024 * 1024 * 1024,
                        'old': 20 * 3 * 1024 * 1024 * 1024,
                    },
                },
            },
        ),
        (
            {
                'source_flavor': 'm2.medium',
                'flavor_change_level': 1,
                'count_hosts': 2,
                'source_ram_quota': 28 * 2 * 1024 * 1024 * 1024,
                'source_cpu_quota': 8500,
            },
            {
                'flavor': 'm2.large',
                'cpu_quota': 8500,
                'ram_quota': 36 * 2 * 1024 * 1024 * 1024,
                'skip_cpu': True,
                'skip_ram': False,
                'quota_fields': {
                    'cpu': {'new': 8500, 'old': 8500},
                    'flavor': {'new': 'm2.large', 'old': 'm2.medium'},
                    'ram': {
                        'new': 36 * 2 * 1024 * 1024 * 1024,
                        'old': 28 * 2 * 1024 * 1024 * 1024,
                    },
                },
            },
        ),
    ],
)
async def test_prepare_to_change_flavor(call_cube_handle, input_data, payload):
    await call_cube_handle(
        'MDBPrepareToChangeFlavor',
        {
            'content_expected': {'payload': payload, 'status': 'success'},
            'data_request': {
                'input_data': input_data,
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
