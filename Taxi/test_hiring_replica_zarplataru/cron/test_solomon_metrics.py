# pylint: disable=redefined-outer-name


async def test_fetch_responds(simple_secdist, run_crontask):

    await run_crontask('solomon_metrics')
