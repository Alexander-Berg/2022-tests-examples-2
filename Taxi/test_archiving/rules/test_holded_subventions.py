import datetime

import pytest

from archiving import core
from archiving import cron_run


@pytest.mark.now('2018-01-10T11:57:00.0')
async def test_archiving_holded_subventions(
        cron_context,
        load_all_mongo_docs,
        replication_state_min_ts,
        fake_task_id,
        patch_current_date,
        requests_handlers,
):
    replication_state_min_ts.apply(
        {'holded_subventions': ('u', datetime.datetime(2018, 1, 2, 0, 0, 29))},
    )
    archivers = await cron_run.prepare_archivers(
        cron_context, 'holded_subventions', fake_task_id,
    )
    archiver = next(iter(archivers.values()))

    ids_to_spare = {
        'cleared_to_spare_id',
        'cleared_to_spare_second_id',
        'cleared_to_spare_third_id',
        'cleared_ahead_of_the_line_first_id',
        'cleared_ahead_of_the_line_second_id',
    }
    ids_to_remove = {'cleared_to_remove_first_id'}
    holded_subventions = await load_all_mongo_docs('holded_subventions')

    assert set(holded_subventions) == ids_to_spare.union(ids_to_remove)
    await core.remove_documents(archiver, cron_context.client_solomon)

    cleared_holded_subventions = await load_all_mongo_docs(
        'holded_subventions',
    )
    assert set(cleared_holded_subventions) == ids_to_spare
