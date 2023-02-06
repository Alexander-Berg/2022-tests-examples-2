import http


async def test_ping(cbox):
    await cbox.query('/ping')
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body == ''
