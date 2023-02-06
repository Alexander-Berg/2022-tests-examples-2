import pytest


@pytest.mark.parametrize(
    ['input_data', 'payload'],
    [
        ({}, {'cpu_quota': 0, 'ram_quota': 0, 'ssd_quota': 0}),
        (
            {
                'first_cpu_quota': 2000,
                'first_ram_quota': 1024,
                'second_ram_quota': 2048,
            },
            {'cpu_quota': 2000, 'ram_quota': 3072, 'ssd_quota': 0},
        ),
        (
            {
                'first_cpu_quota': 1000,
                'second_cpu_quota': 2000,
                'first_ram_quota': 1024,
                'second_ram_quota': 3072,
                'first_ssd_quota': 2048,
                'second_ssd_quota': 512,
            },
            {'cpu_quota': 3000, 'ram_quota': 4096, 'ssd_quota': 2560},
        ),
    ],
)
async def test_sum_quotas(call_cube_handle, input_data, payload):
    await call_cube_handle(
        'DispenserSumQuotas',
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
