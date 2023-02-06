async def test_mdb_move_cluster(call_cube_handle, mdb_mockserver):
    mock = mdb_mockserver(slug='test-slug')
    await call_cube_handle(
        'MDBMoveCluster',
        {
            'content_expected': {
                'payload': {'operation_id': 'mdbq9ue8i0gdv0grghrj'},
                'status': 'success',
            },
            'data_request': {
                'input_data': {
                    'cluster_id': 'cluster-id',
                    'destination_folder_id': 'destination-id',
                    'db_type': 'pgaas',
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
    assert mock.next_call()['request'].json == {
        'destinationFolderId': 'destination-id',
    }
