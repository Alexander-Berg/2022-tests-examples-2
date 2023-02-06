from TPL_PY_PACKAGE.stq import example


async def test_task(stq3_context):
    await example.task(stq3_context, 1, 'test')
