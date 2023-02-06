def test_raises(tap):
    
    tap.plan(3)

    tap.ok(tap.raises, 'raises method exists')

    with tap.raises(Exception):
        raise Exception('hello, world')
    
    with tap.raises((Exception, RuntimeError)):
        raise RuntimeError('hello, world')

    tap()
