# pylint: disable=redefined-outer-name
from processing_antifraud.generated.cron import run_cron


async def test_example(db, simple_secdist):
    await run_cron.main(
        ['processing_antifraud.crontasks.clear_events', '-t', '0'],
    )

    res = await db.antifraud_events.find({}).to_list(None)
    assert len(res) == 1
    assert res[0]['_id'] == 'new_event'
