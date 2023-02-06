# pylint: disable=redefined-outer-name


async def test_solomon_metrics_send(simple_secdist, run_crontask):
    await run_crontask('solomon_metrics')
