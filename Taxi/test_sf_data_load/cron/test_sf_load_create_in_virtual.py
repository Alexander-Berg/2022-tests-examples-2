# pylint: disable=redefined-outer-name
import pytest

from sf_data_load.generated.cron import run_cron
from sf_data_load.stq import sf_load_object
from test_sf_data_load import conftest

SF_DATA_LOAD_SF_RULES = conftest.SF_DATA_LOAD_SF_RULES


@pytest.mark.pgsql(
    'sf_data_load', files=('sf_data_load_create_in_virtual.sql',),
)
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=SF_DATA_LOAD_SF_RULES,
    SF_DATA_LOAD_LOOKUPS={
        'b2b-cc-sf-cti': {
            'create': True,
            'required_fields': ['WhoId', 'OwnerId', 'abc'],
            'sf_key': 'ExternalId__c',
            'sf_object': 'Task',
            'sf_org': 'b2b',
            'source_key': 'cc_sf_cti_call_id',
            'record_load_by_bulk': 0,
        },
        'concat_id_contact_and_task': {
            'sf_key': 'DstNumber__c',
            'sf_object': 'Task',
            'sf_org': 'b2b',
            'source_key': 'Phone',
            'update': True,
            'record_load_by_bulk': 0,
        },
        'concat_id_contact_and_task_mobile': {
            'sf_key': 'DstNumber__c',
            'sf_object': 'Task',
            'sf_org': 'b2b',
            'source_key': 'MobilePhone',
            'update': True,
            'record_load_by_bulk': 0,
        },
        'concat_id_manager_and_task': {
            'sf_key': 'SrcNumber__c',
            'sf_object': 'Task',
            'sf_org': 'b2b',
            'source_key': 'Extension',
            'update': True,
            'record_load_by_bulk': 0,
        },
    },
)
async def test_create_in_virtual(patch, stq3_context, pgsql, taxi_config):
    @patch('multi_salesforce.multi_salesforce.BulkObject.create')
    async def _create(record):
        i = 1
        for rec in record:
            rec.update({'sf__Id': str(i)})
            i += 1
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
    new_offsets = [str(x[-2]) for x in data]
    assert new_offsets == offsets

    cursor.execute(
        f"""
            SELECT * FROM sf_data_load.sf_b2b_task""",
    )
    tasks = cursor.fetchall()

    assert tasks
    assert len(tasks[3][0]) == 32
    assert tasks[3][1] == 'CALLIDFROTESTING12345'
    assert tasks[3][2] == '+7928348868282'
    assert tasks[3][3] == '868482'
    assert tasks[3][4] == '0031q00000qKdfEAAS'
    assert tasks[3][5] == '0051q000006GytfAAC'
