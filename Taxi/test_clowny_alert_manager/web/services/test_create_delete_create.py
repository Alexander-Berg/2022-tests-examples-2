async def test_chain(upsert_service, delete_service):
    create_data = {
        'type': 'rtc',
        'service_name': 'some',
        'project_name': 'taxi-infra',
        'repo_meta': {
            'file_path': 's.yaml',
            'file_name': 's.yaml',
            'config_project': 'taxi',
        },
    }
    srv1 = await upsert_service(create_data)
    await delete_service(srv1['id'])

    srv2 = await upsert_service(create_data)
    assert srv2['id'] != srv1['id']
