async def test_lock(web_context):
    assert await web_context.locks.trylock('test1')
    assert not await web_context.locks.trylock('test1')

    assert await web_context.locks.trylock('test2')
    assert not await web_context.locks.trylock('test2')


async def test_lock_unlock(web_context):
    assert await web_context.locks.trylock('test1')
    assert await web_context.locks.unlock('test1')
    assert await web_context.locks.unlock('test1')


async def test_lock_unlock_unknown(web_context):
    assert await web_context.locks.unlock('test1')
    assert await web_context.locks.unlock('test2')


async def test_sequence(web_context):
    assert await web_context.locks.trylock('test1')
    assert await web_context.locks.unlock('test1')
    assert await web_context.locks.trylock('test1')
    assert await web_context.locks.unlock('test1')
    assert await web_context.locks.trylock('test1')
    assert await web_context.locks.unlock('test1')


async def test_lock_timeout(web_context):
    web_context.locks.timeout = 0

    assert await web_context.locks.trylock('test1')
    assert await web_context.locks.trylock('test1')
