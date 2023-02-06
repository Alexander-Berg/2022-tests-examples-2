# pylint: disable=redefined-outer-name
import pytest

from sf_data_load.generated.cron import run_cron
from sf_data_load.stq import sf_load_object
from test_sf_data_load import conftest

SF_DATA_LOAD_SF_RULES = conftest.SF_DATA_LOAD_SF_RULES
SF_DATA_LOAD_LOOKUPS = conftest.SF_DATA_LOAD_LOOKUPS


@pytest.mark.pgsql(
    'sf_data_load', files=('sf_data_load_update_in_virtual.sql',),
)
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=SF_DATA_LOAD_SF_RULES,
    SF_DATA_LOAD_LOOKUPS=SF_DATA_LOAD_LOOKUPS,
)
async def test_update_in_virtual(patch, stq3_context, pgsql):
    @patch('multi_salesforce.multi_salesforce.BulkObject.create')
    async def _create(record):
        return {'successful': record, 'failed': []}

    @patch('sf_data_load.generated.service.stq_client.plugin.QueueClient.call')
    async def _call(**kwargs):
        await sf_load_object.task(
            stq3_context,
            kwargs['kwargs']['lookup_alias'],
            kwargs['kwargs']['tuple_fields'],
        )

    cursor = pgsql['sf_data_load'].cursor()
    cursor.execute('SELECT * FROM sf_data_load.loading_fields')
    data = cursor.fetchall()
    offsets = [str(x[-2]) for x in data]

    await run_cron.main(['sf_data_load.crontasks.sf_load', '-t', '0'])

    cursor.execute(
        f"""
        SELECT * FROM sf_data_load.loading_fields
        WHERE id IN ({', '.join(offsets)})""",
    )
    data = cursor.fetchall()

    assert data
    new_offsets = [x[-2] for x in data]
    assert set(new_offsets) == {1, 2, 3}

    cursor.execute(
        f"""
            SELECT * FROM sf_data_load.sf_b2b_task
        """,
    )
    tasks = cursor.fetchall()
    assert tasks
    assert len(tasks[0][0]) == 32
    assert len(tasks[1][0]) == 32
    assert tasks[0][1] == 'ID1'
    assert tasks[1][1] == 'ID2'
    assert tasks[0][2] == '+7928348868282'
    assert tasks[1][2] == '+7928348868282'
    assert tasks[0][3] == '868482'
    assert tasks[1][3] == '868482'
    assert tasks[0][4] == 'NEWIDFORCONTACT'
    assert tasks[1][4] == 'NEWIDFORCONTACT'
    assert tasks[0][5] == '0051q000006GytfAAC'
    assert tasks[1][5] == '0051q000006GytfAAC'
