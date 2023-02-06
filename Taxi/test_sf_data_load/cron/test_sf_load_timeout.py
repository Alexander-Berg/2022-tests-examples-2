# pylint: disable=redefined-outer-name
import datetime

import pytest

from sf_data_load.generated.cron import run_cron
from sf_data_load.stq import sf_load_object
from test_sf_data_load import conftest

SF_DATA_LOAD_SF_RULES = conftest.SF_DATA_LOAD_SF_RULES
SF_DATA_LOAD_LOOKUPS = conftest.SF_DATA_LOAD_LOOKUPS


@pytest.mark.pgsql('sf_data_load', files=('sf_data_load_create_in_sf.sql',))
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=SF_DATA_LOAD_SF_RULES,
    SF_DATA_LOAD_LOOKUPS={
        'b2b-cc-sf-cti': {
            'create': True,
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
@pytest.mark.now((datetime.datetime(2022, 6, 17)).strftime('%Y-%m-%d'))
async def test_create_in_sf_timeout(
        patch, stq3_context, pgsql, mock_salesforce_timeout,
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

    assert data == [
        (
            'B2BCallsFromSfCti',
            'external_phone',
            'DstNumber__c',
            'b2b-cc-sf-cti',
            'CALLIDFROTESTING12345',
            '+7928348868282',
            1,
            1,
            None,
        ),
        (
            'B2BCallsFromSfCti',
            'manager_number',
            'SrcNumber__c',
            'b2b-cc-sf-cti',
            'CALLIDFROTESTING12345',
            '868482',
            1,
            2,
            None,
        ),
        (
            'B2BCallsFromSfCti',
            'cc_sf_cti_call_id',
            'ExternalId__c',
            'b2b-cc-sf-cti',
            'CALLIDFROTESTING12345',
            'CALLIDFROTESTING12345',
            1,
            3,
            None,
        ),
    ]


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
async def test_update_in_sf_timeout(
        patch, stq3_context, pgsql, mock_salesforce_timeout,
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

    assert data == [
        (
            'B2BCallsFromSfCti',
            'external_phone',
            'DstNumber__c',
            'b2b-cc-sf-cti',
            'CALLIDFROTESTING12345',
            '+7928348868282',
            2,
            1,
            None,
        ),
        (
            'B2BCallsFromSfCti',
            'manager_number',
            'SrcNumber__c',
            'b2b-cc-sf-cti',
            'CALLIDFROTESTING12345',
            '868482',
            2,
            2,
            None,
        ),
        (
            'B2BCallsFromSfCti',
            'cc_sf_cti_call_id',
            'ExternalId__c',
            'b2b-cc-sf-cti',
            'CALLIDFROTESTING12345',
            'CALLIDFROTESTING12345',
            2,
            3,
            None,
        ),
    ]
