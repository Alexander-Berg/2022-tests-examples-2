import pymongo
import pytest

from taxi_qc_exams.generated.cron import run_cron
from test_taxi_qc_exams import utils


@pytest.mark.config(QC_JOB_SETTINGS=dict(mqc_passes_sync=utils.job_settings()))
async def test_mqc_passes_sync(mongo):
    # crontask
    old = await mongo.qc_passes.find(
        {}, sort=[('_id', pymongo.ASCENDING)],
    ).to_list(length=None)
    new = await mongo.mqc_passes.find(
        {}, sort=[('_id', pymongo.ASCENDING)],
    ).to_list(length=None)
    assert old != new

    await run_cron.main(
        ['taxi_qc_exams.crontasks.sync_mdb.qc_passes', '-t', '0'],
    )

    old = await mongo.qc_passes.find(
        {}, sort=[('_id', pymongo.ASCENDING)],
    ).to_list(length=None)
    new = await mongo.mqc_passes.find(
        {}, sort=[('_id', pymongo.ASCENDING)],
    ).to_list(length=None)
    assert old == new
