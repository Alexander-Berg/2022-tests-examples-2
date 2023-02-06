from rida.generated.cron import run_cron


async def test_send_default_metrics(cron_context):
    await run_cron.main(['rida.crontasks.send_default_metrics', '-t', '0'])
