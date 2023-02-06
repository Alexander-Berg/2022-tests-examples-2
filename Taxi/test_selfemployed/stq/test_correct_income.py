import pytest

from taxi.stq import async_worker_ng as async_worker
from testsuite.utils import http

from selfemployed.fns import client as fns_client
from selfemployed.fns import client_models as fns_models
from selfemployed.stq import correct_income
from .. import conftest

_ENTRIES_SELECT_QUERY = """
SELECT id, park_id, contractor_id, agreement_id, sub_account,
    doc_ref, event_at::TEXT, inn_pd_id, is_own_park, do_send_receipt,
    status, amount::TEXT, order_id, reverse_entry_id,
    receipt_id, receipt_url
FROM se_income.entries
ORDER BY id
"""


@pytest.mark.pgsql('selfemployed_orders@0', files=['setup_entries@0.sql'])
@pytest.mark.pgsql('selfemployed_orders@1', files=['setup_entries@1.sql'])
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.now('2021-11-15T12:00:00Z')
@pytest.mark.config(
    SELFEMPLOYED_INCOME_EVENTS={
        'entries_receipt_properties': {},
        'correction_max_retries': 10,
    },
)
@pytest.mark.parametrize('already_deleted', [False, True])
async def test_correct_income(
        stq3_context, load_json, stq, patch, mock_personal, already_deleted,
):
    @mock_personal('/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        pd_id = request.json['id']
        return {'value': pd_id[:-6], 'id': pd_id}

    @patch('selfemployed.fns.client.Client.revert_income_raw')
    async def _register_income_raw(
            income_data: fns_models.RevertIncomeRawModel,
    ):
        return income_data.inn

    @patch('selfemployed.fns.client.Client.get_revert_income_response')
    async def _get_revert_income_response(msg_id):
        if already_deleted:
            raise fns_client.ReceiptAlreadyDeleted(
                message='', code=fns_client.SmzErrorCode.ALREADY_DELETED,
            )
        return 'DELETED'

    corrections_to_schedule = []  # type: ignore
    for shard in stq3_context.pg.orders_masters:
        records = await shard.fetch(
            'SELECT id, park_id, contractor_id FROM se_income.entries '
            'WHERE reverse_entry_id IS NOT NULL',
        )
        corrections_to_schedule.extend(records)

    for record in corrections_to_schedule:
        await correct_income.task(
            stq3_context,
            async_worker.TaskInfo(
                id=str(record['id']),
                exec_tries=0,
                reschedule_counter=0 if record['id'] != 8 else 10,
                queue='selfemployed_fns_correct_income',
            ),
            entry_id=record['id'],
            park_id=record['park_id'],
            contractor_id=record['contractor_id'],
        )

    receipts_by_shards = {}
    for num, shard in enumerate(stq3_context.pg.orders_masters):
        shard_records = await shard.fetch(_ENTRIES_SELECT_QUERY)
        receipts_by_shards[str(num)] = [
            dict(record) for record in shard_records
        ]

    assert receipts_by_shards == load_json('expected_entries.json')

    assert stq.selfemployed_fns_report_income.times_called == 1
