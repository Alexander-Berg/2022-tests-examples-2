async def test_configs(library_context):
    result = await library_context.client_configs.get_all()
    assert result == {}
