import pytest


@pytest.mark.parametrize(
    'cube_name',
    [
        'L3MGRFetchIpv6',
        'L3MGRDisableBalancer',
        'L3MGRWaitForEmptyServiceActivation',
        'L3MGRHideService',
    ],
)
async def test_post_l3mgr_cube(
        web_app_client, web_context, cube_name, load_json, l3mgr_mockserver,
):
    l3mgr_mockserver()
    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']
