import pytest

HEADERS = {'X-YaTaxi-Api-Key': 'fake_token'}


@pytest.mark.parametrize(
    'name,expected_code,expected_data',
    [
        (
            'taxi_logserrors',
            200,
            {
                'name': 'taxi_logserrors',
                'subscribers': ['nevladov'],
                'type': 'conductor',
                'status': 'OK',
            },
        ),
        ('taxi_imports', 404, None),
    ],
)
@pytest.mark.pgsql('logs_errors_filters', files=['test_update_cgroup.sql'])
async def test_update_cgroup(
        web_app_client, auth, name, expected_code, expected_data,
):
    await auth()

    params = {'cgroup_name': name}
    response = await web_app_client.put(
        '/v1/cgroup/',
        headers=HEADERS,
        params=params,
        json={'subscribers': ['nevladov'], 'type': 'conductor'},
    )
    assert response.status == expected_code
    if response.status == 200:
        params = {'cgroup_name': name}
        response = await web_app_client.get(
            '/v1/cgroup/list/', headers=HEADERS, params=params,
        )
        result = await response.json()
        cgroups_by_name = {
            cgroup['name']: cgroup for cgroup in result['cgroups']
        }
        assert cgroups_by_name[name] == expected_data
