async def test_mdb_update_cluster(
        call_cube_handle, mdb_mockserver, mockserver,
):
    mock = mdb_mockserver()

    await call_cube_handle(
        'MDBUpdateCluster',
        {
            'content_expected': {
                'payload': {'operation_id': 'mdbq9ue8i0gdv0grghrj'},
                'status': 'success',
            },
            'data_request': {
                'input_data': {
                    'cluster_id': 'mdbq9iqofu9vus91r2j9',
                    'db_type': 'pgaas',
                    'flavor': 's2.micro',
                    'idempotency_token': '3a34772d5543423bbf3eb3f66d921f22',
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert mock.times_called == 2
    mock.next_call()
    update_request = mock.next_call()['request']
    assert update_request.json == {
        'updateMask': 'configSpec.resources.resourcePresetId',
        'configSpec': {'resources': {'resourcePresetId': 's2.micro'}},
    }
