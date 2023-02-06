import pytest

from sf_data_load.generated.cron import run_cron
from sf_data_load.stq import sf_load_object


@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'B2BSOLeads',
            'source_field': 'region',
            'sf_api_name': 'Region__c',
            'lookup_alias': 'b2b-so-leads',
            'load_period': 1,
        },
        {
            'source': 'B2BSOLeads',
            'source_field': 'product',
            'sf_api_name': 'Product__c',
            'lookup_alias': 'b2b-so-leads',
            'load_period': 1,
        },
        {
            'source': 'B2BSOLeads',
            'source_field': 'origin',
            'sf_api_name': 'Origin',
            'lookup_alias': 'b2b-so-leads',
            'load_period': 1,
        },
        {
            'source': 'B2BSOLeads',
            'source_field': 'const#0123X000000Zzw2QAC',
            'sf_api_name': 'RecordTypeId',
            'lookup_alias': 'b2b-so-leads',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'b2b-so-leads': {
            'sf_org': 'b2b',
            'sf_object': 'Case',
            'source_key': '#auto',
            'create': True,
            'record_load_by_bulk': 0,
        },
    },
)
async def test_b2b_so_lead(taxi_sf_data_load_web, patch, stq3_context, pgsql):
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

    so_lead = {'region': 'RF', 'product': 'Taxi', 'origin': 'testtest'}

    resp = await taxi_sf_data_load_web.post(
        '/v1/forms/b2b/leads/so', json=so_lead,
    )
    assert resp.status == 200

    cursor = pgsql['sf_data_load'].cursor()
    cursor.execute(
        """
        SELECT
            source_class_name,
            source_field,
            sf_api_field_name,
            lookup_alias,
            source_key,
            data_value
        FROM sf_data_load.loading_fields
        WHERE lookup_alias = 'b2b-so-leads'
        ORDER BY source_field
    """,
    )
    assert cursor.fetchall() == [
        (
            'B2BSOLeads',
            'const#0123X000000Zzw2QAC',
            'RecordTypeId',
            'b2b-so-leads',
            '0',
            '0123X000000Zzw2QAC',
        ),
        ('B2BSOLeads', 'origin', 'Origin', 'b2b-so-leads', '0', 'testtest'),
        ('B2BSOLeads', 'product', 'Product__c', 'b2b-so-leads', '0', 'Taxi'),
        ('B2BSOLeads', 'region', 'Region__c', 'b2b-so-leads', '0', 'RF'),
    ]

    await run_cron.main(['sf_data_load.crontasks.sf_load', '-t', '0'])

    cursor.execute(
        """
        SELECT count(*) FROM sf_data_load.loading_fields
        WHERE lookup_alias = 'b2b-so-leads'
    """,
    )
    assert cursor.fetchall()[0][0] == 0
