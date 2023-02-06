async def test_handler(get_template, delete_template):
    tmpl = await get_template(1)
    assert not tmpl['is_deleted']
    await delete_template(1)
    tmpl = await get_template(1)
    assert tmpl['is_deleted']
