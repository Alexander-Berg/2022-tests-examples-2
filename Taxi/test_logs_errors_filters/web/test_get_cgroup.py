import pytest

HEADERS = {'X-YaTaxi-Api-Key': 'fake_token'}


@pytest.mark.parametrize(
    'cgroup_name,expected_status,expected_data',
    [
        ('taxi_billing_docs', 404, None),
        (
            'taxi_test-service_stable',
            200,
            {
                'last_errors_kibana_link': 'test_link',
                'name': 'taxi_test-service_stable',
                'status': 'OK',
                'subscribers': [],
                'type': 'rtc',
            },
        ),
    ],
)
@pytest.mark.pgsql('logs_errors_filters', files=['test_get_cgroup.sql'])
async def test_get_cgroup_list(
        web_app_client, auth, cgroup_name, expected_status, expected_data,
):
    await auth()

    params = {}
    if cgroup_name is not None:
        params['cgroup_name'] = cgroup_name
    response = await web_app_client.get(
        '/v1/cgroup/', headers=HEADERS, params=params,
    )
    assert response.status == expected_status
    if expected_data is not None:
        result = await response.json()
        kibana_link = result.pop('kibana_link')
        if result['type'] == 'rtc':
            assert 'pre_stable' in kibana_link
        assert result == expected_data
