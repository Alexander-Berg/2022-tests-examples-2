import pytest

HEADERS = {'X-YaTaxi-Api-Key': 'fake_token'}


@pytest.mark.parametrize(
    'cgroup_name,expected',
    [
        (
            None,
            [
                'taxi_billing_docs',
                'taxi_billing_replication',
                'taxi_logserrors',
            ],
        ),
        ('bill', ['taxi_billing_docs', 'taxi_billing_replication']),
        ('repl', ['taxi_billing_replication']),
    ],
)
@pytest.mark.pgsql('logs_errors_filters', files=['test_get_cgroup_list.sql'])
async def test_get_cgroup_list(web_app_client, auth, cgroup_name, expected):
    await auth()

    params = {}
    if cgroup_name is not None:
        params['cgroup_name'] = cgroup_name
    response = await web_app_client.get(
        '/v1/cgroup/list/', headers=HEADERS, params=params,
    )
    assert response.status == 200
    result = await response.json()
    cgroups_by_name = {cgroup['name']: cgroup for cgroup in result['cgroups']}
    assert sorted(cgroups_by_name.keys()) == expected
    if 'taxi_billing_replication' in cgroups_by_name:
        assert cgroups_by_name['taxi_billing_replication']['subscribers'] == [
            'nevladov',
        ]
