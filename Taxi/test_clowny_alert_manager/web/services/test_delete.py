async def test_handler(get_service, delete_service):
    srv = await get_service(1)
    assert all(not x['is_deleted'] for x in srv['branches'])
    await delete_service(1)
    srv = await get_service(1)
    assert srv['is_deleted']
    assert all(x['is_deleted'] for x in srv['branches'])
