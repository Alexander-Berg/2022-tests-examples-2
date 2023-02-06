# pylint: disable=protected-access
async def test_solomon(web_context, mockserver, patch):
    base_url = web_context.client_solomon._base_url
    assert base_url == '$mockserver/solomon/unittests'
