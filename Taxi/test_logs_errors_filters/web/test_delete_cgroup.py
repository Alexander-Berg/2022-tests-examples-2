import pytest

HEADERS = {'X-YaTaxi-Api-Key': 'fake_token'}


@pytest.mark.parametrize(
    'params,expected_code,expected_data',
    [
        ({'cgroup_name': 'taxi_imports'}, 200, {}),
        (
            {'cgroup_name': 'taxi_logs_from_yt'},
            404,
            {
                'code': 'CGROUP_IS_NOT_FOUND',
                'message': 'group taxi_logs_from_yt is not found',
            },
        ),
        (
            {'cgroup_name': 'taxi_logserrors'},
            400,
            {
                'code': 'UNABLE_TO_DELETE_CGROUP',
                'message': (
                    'some filters are not removed for cgroup taxi_logserrors'
                ),
            },
        ),
    ],
)
@pytest.mark.pgsql('logs_errors_filters', files=['test_delete_cgroup.sql'])
async def test_delete_cgroup(
        web_app_client, auth, params, expected_code, expected_data,
):
    await auth()

    response = await web_app_client.delete(
        '/v1/cgroup/', headers=HEADERS, params=params,
    )
    assert response.status == expected_code
    result = await response.json()
    assert expected_data == result
