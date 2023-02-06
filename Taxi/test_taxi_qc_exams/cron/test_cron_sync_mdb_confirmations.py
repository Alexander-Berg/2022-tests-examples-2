import pymongo
import pytest

from taxi_qc_exams.generated.cron import run_cron
from test_taxi_qc_exams import utils


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(mqc_confirmations_sync=utils.job_settings()),
)
async def test_mqc_confirmations_sync(mongo):
    old = await mongo.confirmations.find(
        {}, sort=[('_id', pymongo.ASCENDING)],
    ).to_list(length=None)
    new = await mongo.mqc_confirmations.find(
        {}, sort=[('_id', pymongo.ASCENDING)],
    ).to_list(length=None)
    assert old != new

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.sync_mdb.confirmations', '-t', '0'],
    )

    old = await mongo.confirmations.find(
        {}, sort=[('_id', pymongo.ASCENDING)],
    ).to_list(length=None)
    new = await mongo.mqc_confirmations.find(
        {}, sort=[('_id', pymongo.ASCENDING)],
    ).to_list(length=None)
    assert old == new
