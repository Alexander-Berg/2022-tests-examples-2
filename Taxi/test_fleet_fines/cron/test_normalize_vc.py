# pylint: disable=redefined-outer-name
import pytest

from fleet_fines.generated.cron import cron_context as context_module
from fleet_fines.generated.cron import run_cron


@pytest.mark.config(
    FLEET_FINES_NORMALIZE_VCS={
        'is_enabled': True,
        'max_batches_per_run': 2,
        'batch_limit': 10,
    },
)
@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_vc
        (park_id, car_id, vc_original, vc_normalized,
         is_normalized, is_valid)
    VALUES
        ('p1', 'd1', '\tcqwe12AFoPvm-№_', NULL,
         FALSE, FALSE)
    """,
    ],
)
async def test_normalize_vc(cron_context: context_module.Context):
    await run_cron.main(['fleet_fines.crontasks.normalize_vc', '-t', '0'])
    normalized_docs, _ = await cron_context.pg_access.docs.get_vcs(10, '')
    assert normalized_docs == ['СЕ12АФОРВМ']
