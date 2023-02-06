import pymongo
import pytest

from taxi_qc_exams.generated.cron import run_cron
from test_taxi_qc_exams import utils


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(
        mqc_cars_sync=utils.job_settings(),
        mqc_drivers_sync=utils.job_settings(),
    ),
)
async def test_mqc_entities_sync(mongo):
    old = await mongo.qc_entities.find(
        {}, sort=[('_id', pymongo.ASCENDING)],
    ).to_list(length=None)
    new = await mongo.mqc_entities.find(
        {}, sort=[('_id', pymongo.ASCENDING)],
    ).to_list(length=None)
    assert old != new

    await run_cron.main(['taxi_qc_exams.crontasks.sync_mdb.cars', '-t', '0'])

    await run_cron.main(
        ['taxi_qc_exams.crontasks.sync_mdb.drivers', '-t', '0'],
    )

    old = await mongo.qc_entities.find(
        {}, sort=[('_id', pymongo.ASCENDING)],
    ).to_list(length=None)
    new = await mongo.mqc_entities.find(
        {}, sort=[('_id', pymongo.ASCENDING)],
    ).to_list(length=None)
    assert old == new
