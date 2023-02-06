# pylint: disable=redefined-outer-name
import pytest

from fleet_fines.generated.cron import cron_context as context_module
from fleet_fines.generated.cron import run_cron


@pytest.mark.config(
    FLEET_FINES_NORMALIZE_DLS={
        'is_enabled': True,
        'max_batches_per_run': 2,
        'batch_limit': 10,
    },
)
@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_dl
        (park_id, driver_id, dl_pd_id_original, dl_pd_id_normalized,
         is_normalized, is_valid)
    VALUES
        ('p1', 'd1', '1234567890', NULL,
         FALSE, FALSE)
    """,
    ],
)
async def test_normalize_vc(cron_context: context_module.Context, patch):
    @patch('taxi.clients.personal.PersonalApiClient.bulk_retrieve')
    async def _retrieve_pd(*args, **kwargs):
        return [{'license': '\tcqwe12AFoPvm-№_', 'id': '1234567890'}]

    @patch('taxi.clients.personal.PersonalApiClient.bulk_store')
    async def _store_pd(*args, **kwargs):
        return [{'license': 'СЕ12АФОРВМ', 'id': '0987654321'}]

    await run_cron.main(['fleet_fines.crontasks.normalize_dl', '-t', '0'])
    normalized_docs, _ = await cron_context.pg_access.docs.get_dl_pd_ids(
        10, '',
    )
    assert normalized_docs == ['0987654321']
