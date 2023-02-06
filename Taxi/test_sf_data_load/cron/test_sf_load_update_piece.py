# pylint: disable=redefined-outer-name
import pytest

from sf_data_load.generated.cron import run_cron
from sf_data_load.stq import sf_load_object
from test_sf_data_load import conftest

SF_DATA_LOAD_SF_RULES = conftest.SF_DATA_LOAD_SF_RULES


@pytest.mark.pgsql('sf_data_load', files=('sf_data_load_update_in_sf.sql',))
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=SF_DATA_LOAD_SF_RULES,
    SF_DATA_LOAD_LOOKUPS={
        'b2b-cc-sf-cti': {
            'update': True,
            'required_fields': ['WhoId', 'OwnerId'],
            'sf_key': 'ExternalId__c',
            'sf_object': 'Task',
            'sf_org': 'b2b',
            'source_key': 'cc_sf_cti_call_id',
        },
        'concat_id_contact_and_task': {
            'sf_key': 'DstNumber__c',
            'sf_object': 'Task',
            'sf_org': 'b2b',
            'source_key': 'Phone',
            'update': True,
        },
        'concat_id_contact_and_task_mobile': {
            'sf_key': 'DstNumber__c',
            'sf_object': 'Task',
            'sf_org': 'b2b',
            'source_key': 'MobilePhone',
            'update': True,
        },
        'concat_id_manager_and_task': {
            'sf_key': 'SrcNumber__c',
            'sf_object': 'Task',
            'sf_org': 'b2b',
            'source_key': 'Extension',
            'update': True,
        },
    },
)
async def test_update_in_sf_piece_successful(
        patch, stq3_context, pgsql, salesforce,
):
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


@pytest.mark.pgsql('sf_data_load', files=('sf_data_load_update_in_sf.sql',))
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=SF_DATA_LOAD_SF_RULES,
    SF_DATA_LOAD_LOOKUPS={
        'b2b-cc-sf-cti': {
            'update': True,
            'required_fields': ['WhoId', 'OwnerId'],
            'sf_key': 'ExternalId__c',
            'sf_object': 'Task',
            'sf_org': 'b2b',
            'source_key': 'cc_sf_cti_call_id',
        },
        'concat_id_contact_and_task': {
            'sf_key': 'DstNumber__c',
            'sf_object': 'Task',
            'sf_org': 'b2b',
            'source_key': 'Phone',
            'update': True,
        },
        'concat_id_contact_and_task_mobile': {
            'sf_key': 'DstNumber__c',
            'sf_object': 'Task',
            'sf_org': 'b2b',
            'source_key': 'MobilePhone',
            'update': True,
        },
        'concat_id_manager_and_task': {
            'sf_key': 'SrcNumber__c',
            'sf_object': 'Task',
            'sf_org': 'b2b',
            'source_key': 'Extension',
            'update': True,
        },
    },
)
async def test_update_in_sf_piece_failed(
        patch, stq3_context, pgsql, mock_salesforce_failed,
):
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
    new_offsets = [str(x[-2]) for x in data]
    assert offsets == new_offsets
