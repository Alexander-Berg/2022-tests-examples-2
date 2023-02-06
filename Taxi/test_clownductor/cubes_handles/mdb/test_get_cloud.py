async def test_mdb_get_cloud(call_cube_handle, mdb_mockserver):
    mock = mdb_mockserver(slug='test-slug')
    await call_cube_handle(
        'MDBGetCloud',
        {
            'content_expected': {
                'payload': {'cloud_id': 'test-slug'},
                'status': 'success',
            },
            'data_request': {
                'input_data': {'service_abc': 'test-slug'},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert mock.times_called == 2
