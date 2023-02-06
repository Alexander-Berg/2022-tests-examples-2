import pytest


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'update_hosts_cube_enabled': True})
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_update_hosts(
        web_app_client, web_context, load_json, nanny_mockserver,
):
    cube_name = 'UpdateHosts'
    json_data = load_json(f'{cube_name}.json')
    await _test_cube(web_app_client, json_data, cube_name)
    hosts = await web_context.service_manager.hosts.get_by('branch_id', 1)
    assert [host['name'] for host in hosts] == []
    hosts = await web_context.service_manager.hosts.get_by('branch_id', 2)
    assert [host['name'] for host in hosts] == [
        'qqbyrftajycoh7q2.vla.yp-c.yandex.net',
    ]


async def _test_cube(web_app_client, json_data, cube_name):
    for data in json_data:
        data_request = data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == data['content_expected']
