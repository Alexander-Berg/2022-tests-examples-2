async def test_tap(tap):
    tap.plan(1)
    tap.ok(True, 'ok test')
    tap()
