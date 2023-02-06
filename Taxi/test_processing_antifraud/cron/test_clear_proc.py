# pylint: disable=redefined-outer-name
from processing_antifraud.generated.cron import run_cron


async def test_clear_proc(db, simple_secdist):
    await run_cron.main(
        ['processing_antifraud.crontasks.clear_proc', '-t', '0'],
    )

    res = await db.antifraud_proc.find({}).to_list(None)
    assert len(res) == 1
    assert res[0]['_id'] == 'document_2'
