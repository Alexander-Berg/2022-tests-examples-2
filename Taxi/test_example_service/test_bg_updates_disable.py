import asyncio


async def test_web(web_context):
    assert isinstance(web_context.config.task, asyncio.Task)
    assert web_context.grokker.disable_background_updates is False
    assert web_context.example_adder.disable_background_updates is False


async def test_cron(cron_context):
    assert cron_context.config.task is None
    assert cron_context.grokker.disable_background_updates is True
    assert cron_context.example_adder.disable_background_updates is True
