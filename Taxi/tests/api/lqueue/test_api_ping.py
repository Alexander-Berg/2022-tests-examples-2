from stall.lqueue import LQueue

async def test_ping(api, tmpdir):
    t = await api()

    t.tap.plan(3)

    pusher = LQueue(cache_dir=tmpdir)
    t.tap.ok(pusher, 'инстанцирован')
    t.app.pusher = pusher

    await t.get_ok('api_lqueue_ping')
    t.status_is(200, diag=True)

    t.tap()
