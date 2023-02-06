import pytest


@pytest.mark.pgsql('clowny_alert_manager', files=['simple.sql'])
@pytest.mark.parametrize(
    ['clown_branch_id', 'expected_resp_code', 'expected_resp_json'],
    [
        (
            777,
            200,
            {'clown_branch_id': 777, 'juggler_host': 'some_direct_link'},
        ),
        (
            666,
            404,
            {
                'code': 'JUGGLER_HOST_NOT_FOUND',
                'message': 'juggler_host not found for branch',
            },
        ),
        (
            228,
            404,
            {
                'code': 'JUGGLER_HOST_NOT_FOUND',
                'message': 'juggler_host not found for branch',
            },
        ),
    ],
)
async def test_simple(
        taxi_clowny_alert_manager_web,
        clown_branch_id,
        expected_resp_code,
        expected_resp_json,
):
    response = await taxi_clowny_alert_manager_web.get(
        '/v1/policy', params={'clown_branch_id': clown_branch_id},
    )

    assert response.status == expected_resp_code
    assert await response.json() == expected_resp_json
