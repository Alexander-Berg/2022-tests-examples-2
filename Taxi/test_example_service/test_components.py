def test_web(web_context):
    assert web_context.grokker.get_seed() == 2
    assert web_context.locker.lock() is True
    assert web_context.locker.lock() is False
    assert web_context.grokker.get_seed() == -1


def test_stq(stq3_context):
    assert stq3_context.grokker.get_seed() == 2
    assert not hasattr(stq3_context, 'locker')
