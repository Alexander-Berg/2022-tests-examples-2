import pytest

HEADERS = {'X-YaTaxi-Api-Key': 'fake_token'}


@pytest.mark.parametrize(
    'data,expected_code,expected_data',
    [
        (
            {'subscribers': [], 'type': 'conductor'},
            400,
            {'code': 'NAME_IS_REQUIRED', 'message': 'name is required'},
        ),
        (
            {'name': 'taxi_imports', 'subscribers': [], 'type': 'conductor'},
            200,
            {},
        ),
        (
            {
                'name': 'taxi_logserrors',
                'subscribers': [],
                'type': 'conductor',
            },
            409,
            {
                'code': 'CGROUP_IS_ALREADY_CREATED',
                'message': 'group taxi_logserrors is already created',
            },
        ),
    ],
)
@pytest.mark.pgsql('logs_errors_filters', files=['test_create_cgroup.sql'])
async def test_create_cgroup(
        web_app_client, auth, data, expected_code, expected_data,
):
    await auth()

    response = await web_app_client.post(
        '/v1/cgroup/', headers=HEADERS, json=data,
    )
    assert response.status == expected_code
    result = await response.json()
    assert expected_data == result
