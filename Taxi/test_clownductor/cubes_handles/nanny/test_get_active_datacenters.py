import pytest


@pytest.mark.parametrize(
    'env, expected_payload',
    [
        pytest.param('testing', {'active_datacenters': []}),
        pytest.param(
            'stable',
            {
                'active_datacenters': [
                    {'branch_id': 2, 'regions': ['man', 'sas', 'vla']},
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_get_active_dc(
        call_cube_handle, nanny_yp_mockserver, env, expected_payload,
):
    nanny_yp_mockserver()
    await call_cube_handle(
        'NannyCubeGetActiveDatacenters',
        {
            'content_expected': {
                'payload': expected_payload,
                'status': 'success',
            },
            'data_request': {
                'input_data': {'service_id': 1, 'env': env},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
