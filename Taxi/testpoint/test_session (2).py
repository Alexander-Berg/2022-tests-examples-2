from taxi_tests.plugins import testpoint


async def test_session():
    session = testpoint.TestPointSession()

    @session('foo')
    def point(data):
        pass

    assert session['foo'] is point

    await session.handle({'name': 'foo', 'data': 'bar'})
    assert point.next_call() == {'data': 'bar'}

    await session.handle({'name': 'unknown'})
