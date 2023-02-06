async def test_mdb_get_folder(call_cube_handle, mdb_mockserver):
    mock = mdb_mockserver(slug='test-slug')
    await call_cube_handle(
        'MDBGetFolder',
        {
            'content_expected': {
                'payload': {'folder_id': 'test-slug'},
                'status': 'success',
            },
            'data_request': {
                'input_data': {'cloud_id': 'test-slug'},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert mock.times_called == 2
    mock.next_call()
    assert mock.next_call()['request'].query == {'cloudId': 'test-slug'}
