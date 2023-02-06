import pytest


@pytest.mark.parametrize(
    'cube_name', ['DNSCreateRecord', 'DNSWaitForJob', 'DNSCreateAlias'],
)
async def test_post_dns_cube(
        web_app_client, web_context, cube_name, load_json, dns_mockserver,
):
    dns_mockserver()

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']
