import pytest


@pytest.mark.parametrize(
    'cube_name',
    [
        'MDBCubeWaitForService',
        'MDBCubeWaitForOperation',
        'MDBCubeCreateCluster',
    ],
)
async def test_post_mdb_cube_handles(
        web_app_client, cube_name, load_json, yav_mockserver, mdb_mockserver,
):
    yav_mockserver()
    mdb_mockserver(slug='test-db')
    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']


async def test_mdb_get_cluster(call_cube_handle, mdb_mockserver):
    mock = mdb_mockserver()
    await call_cube_handle(
        'MDBGetCluster',
        {
            'content_expected': {
                'payload': {
                    'flavor': 's2.micro',
                    'hosts_number': 3,
                    'folder_id': 'mdb-junk',
                    'cluster_name': 'karachevda-test',
                },
                'status': 'success',
            },
            'data_request': {
                'input_data': {
                    'cluster_id': 'mdbq9iqofu9vus91r2j9',
                    'db_type': 'pgaas',
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert mock.times_called == 3
