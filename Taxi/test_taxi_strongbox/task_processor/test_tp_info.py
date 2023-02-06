import pytest


@pytest.mark.parametrize(
    'job_id, expected_data',
    [
        pytest.param(
            11,
            {'status': 'in_progress', 'sleep_duration': 10},
            id='pr_not_exists',
        ),
        pytest.param(
            12,
            {
                'status': 'success',
                'payload': {'pull_request_url': 'mocked_pull_request_url'},
            },
            id='found_pr',
        ),
    ],
)
async def test_cube_get_arcadia_pr_url(
        call_cube, tp_mock, job_id, expected_data,
):
    tp_mock()
    data = await call_cube('GetArcadiaPrUrl', {'job_id': job_id})
    assert data == expected_data
