import pytest


@pytest.mark.parametrize('cube_name', ['SendYpPodsetsToSolomon'])
async def test_post_solomon_cube_handles(
        web_app_client,
        cube_name,
        load_json,
        nanny_yp_mockserver,
        solomon_mockserver,
):
    nanny_yp_mockserver()
    solomon_mockserver()

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']
