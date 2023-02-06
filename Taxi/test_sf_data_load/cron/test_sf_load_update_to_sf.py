# pylint: disable=redefined-outer-name
import pytest

from sf_data_load.generated.cron import run_cron
from sf_data_load.stq import sf_load_object
from test_sf_data_load import conftest

SF_DATA_LOAD_SF_RULES = conftest.SF_DATA_LOAD_SF_RULES
SF_DATA_LOAD_LOOKUPS = conftest.SF_DATA_LOAD_LOOKUPS


@pytest.mark.pgsql('sf_data_load', files=('sf_data_load_update_to_sf.sql',))
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=SF_DATA_LOAD_SF_RULES,
    SF_DATA_LOAD_LOOKUPS=SF_DATA_LOAD_LOOKUPS,
)
async def test_update_to_sf(patch, stq3_context, pgsql):
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

    assert not data
    cursor.execute(
        f"""
            SELECT * FROM sf_data_load.sf_b2b_task
        """,
    )
    tasks = cursor.fetchall()
    assert tasks == [
        ('1', 'CALLIDFROTESTING12345', '+7928348868282', '868482', None, None),
    ]


@pytest.mark.pgsql('sf_data_load', files=('sf_update_empty_fields.sql',))
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=SF_DATA_LOAD_SF_RULES,
    SF_DATA_LOAD_LOOKUPS={
        'b2b-cc-sf-cti': {
            'create': True,
            'update': True,
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
async def test_update_to_sf_empty_field(patch, stq3_context, pgsql):
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

    assert not data
    cursor.execute(
        f"""
                SELECT * FROM sf_data_load.sf_b2b_task
            """,
    )
    tasks = cursor.fetchall()
    assert tasks == [
        (
            'aaaaaaaaaaaaaaaaaaaaaaaaaa',
            'CALLIDFROTESTING12345',
            '+7928348868282',
            None,
            '0031q00000qKdfEAAS',
            '0051q000006GytfAAC',
        ),
    ]


@pytest.mark.pgsql('sf_data_load', files=('sf_data_load_update_in_sf.sql',))
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=SF_DATA_LOAD_SF_RULES,
    SF_DATA_LOAD_LOOKUPS={
        'b2b-cc-sf-cti': {
            'update': True,
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
async def test_update_in_sf(patch, stq3_context, pgsql):
    @patch('multi_salesforce.multi_salesforce.BulkObject.update')
    async def _create(record):
        record[0].update({'sf__Id': 'aaaaaaaaaaaaaaa'})
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

    assert not data
    cursor.execute('SELECT * FROM sf_data_load.sf_b2b_task')
    task_data = cursor.fetchall()
    assert task_data == [
        (
            'aaaaaaaaaaaaaaa',
            'CALLIDFROTESTING12345',
            '+7928348868282',
            '868482',
            '0031q00000qKdfEAAS',
            '0051q000006GytfAAC',
        ),
    ]
