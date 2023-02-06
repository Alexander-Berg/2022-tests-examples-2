from aiohttp import web
import pytest


@pytest.mark.features_on('secrets_project_prefix_naming')
@pytest.mark.parametrize(
    'cube_name',
    [
        'StrongboxCubeAddGroup',
        'StrongboxCubeEnvironments',
        'StrongboxCubeAddPostgres',
        'StrongboxCubeAddDb',
        'StrongboxCubeAddTvm',
    ],
)
async def test_post_strongbox_cube_handles(
        web_app_client,
        cube_name,
        load_json,
        mock_strongbox,
        yav_mockserver,
        mdb_mockserver,
        login_mockserver,
        staff_mockserver,
        add_project,
):
    @mock_strongbox('/v1/groups/')
    # pylint: disable=W0612
    async def handler(request):  # pylint: disable=unused-argument
        if request.method == 'GET':
            status = 200
        else:
            status = 409

        if status == 200:
            data = {
                'yav_secret_uuid': 'sec-XXX',
                'yav_version_uuid': 'ver-YYY',
                'service_name': 'some-service',
                'env': 'unstable',
            }
            return web.json_response(data, status=status)
        return web.json_response({}, status=status)

    @mock_strongbox('/v1/secrets/')
    # pylint: disable=W0612
    async def get_secrets(request):  # pylint: disable=unused-argument
        return web.json_response(
            {
                'yav_secret_uuid': 'sec-XXX',
                'yav_version_uuid': 'ver-YYY',
                'name': 'TVM_NAME',
            },
        )

    yav_mockserver()
    mdb_mockserver(slug='test-db')
    login_mockserver()
    staff_mockserver()
    await add_project('taxi-devops')

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']
