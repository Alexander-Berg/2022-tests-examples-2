async def test_400(cbox):
    await cbox.query('/v1/tasks/bad_id/')
    assert cbox.status == 400


async def test_404(cbox):
    await cbox.post('/wrong/path', data={})
    assert cbox.status == 404
