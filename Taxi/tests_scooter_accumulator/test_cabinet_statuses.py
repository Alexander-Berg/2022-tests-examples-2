import pytest

from . import sql

TESTPOINT_NAME = 'mqtt_cabinet_statuses'
PERIODIC_TASK = 'update_cabinet_statuses'


@pytest.mark.suspend_periodic_tasks(PERIODIC_TASK)
async def test_update_cabinet_statuses(
        taxi_scooter_accumulator, testpoint, testpoint_cabinet_statuses, pgsql,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cabinet_statuses(data):
        return testpoint_cabinet_statuses

    await taxi_scooter_accumulator.run_periodic_task(PERIODIC_TASK)
    assert mqtt_cabinet_statuses.times_called == 1

    assert sql.select_accumulators_info(pgsql, select_charge=True) == [
        ('accum_id1', None, 'cabinet_id2', None, 95),
        ('accum_id2', None, 'aretl8d4gho7e6i3tvn1', None, 5),
        ('accum_id3', None, 'aretl8d4gho7e6i3tvn1', None, 95),
        ('accum_id4', None, 'cabinet_id2', None, 6),
    ]
