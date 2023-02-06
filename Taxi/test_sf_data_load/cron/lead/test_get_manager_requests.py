# pylint: disable=redefined-outer-name
import pytest

from sf_data_load.generated.cron import run_cron


@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'B2BManagerRequests',
            'source_field': 'company_tin',
            'sf_api_name': 'Tin__c',
            'lookup_alias': 'managers',
            'load_period': 1,
        },
        {
            'source': 'B2BManagerRequests',
            'source_field': 'company_cio',
            'sf_api_name': 'Cio__c',
            'lookup_alias': 'managers',
            'load_period': 1,
        },
        {
            'source': 'B2BManagerRequests',
            'source_field': 'enterprise_name_full',
            'sf_api_name': 'Name',
            'lookup_alias': 'managers',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'managers': {
            'sf_org': 'b2b',
            'sf_object': 'Lead',
            'source_key': 'company_tin',
        },
    },
)
async def test_get_manager_requests(mock_manager_request, pgsql):
    await run_cron.main(
        ['sf_data_load.crontasks.lead.get_manager_requests', '-t', '0'],
    )

    cursor = pgsql['sf_data_load'].cursor()

    query = """
            SELECT
                source_class_name,
                source_field,
                sf_api_field_name,
                lookup_alias,
                data_value
            FROM sf_data_load.loading_fields
            WHERE
                source_key
            IN
                ('500100732259', '102500352', '102500351', '1503009020')
            ORDER BY source_field;
        """

    cursor.execute(query)
    data = cursor.fetchall()

    assert data == [
        ('B2BManagerRequests', 'company_cio', 'Cio__c', 'managers', None),
        ('B2BManagerRequests', 'company_cio', 'Cio__c', 'managers', None),
        ('B2BManagerRequests', 'company_cio', 'Cio__c', 'managers', None),
        (
            'B2BManagerRequests',
            'company_cio',
            'Cio__c',
            'managers',
            'r1_company_cio',
        ),
        (
            'B2BManagerRequests',
            'company_tin',
            'Tin__c',
            'managers',
            '500100732259',
        ),
        (
            'B2BManagerRequests',
            'company_tin',
            'Tin__c',
            'managers',
            '1503009020',
        ),
        (
            'B2BManagerRequests',
            'company_tin',
            'Tin__c',
            'managers',
            '102500351',
        ),
        (
            'B2BManagerRequests',
            'company_tin',
            'Tin__c',
            'managers',
            '102500352',
        ),
        (
            'B2BManagerRequests',
            'enterprise_name_full',
            'Name',
            'managers',
            'r3_5',
        ),
        (
            'B2BManagerRequests',
            'enterprise_name_full',
            'Name',
            'managers',
            'r4_5',
        ),
        (
            'B2BManagerRequests',
            'enterprise_name_full',
            'Name',
            'managers',
            'r1_enterprise_name_full',
        ),
        (
            'B2BManagerRequests',
            'enterprise_name_full',
            'Name',
            'managers',
            'r2_5',
        ),
    ]
