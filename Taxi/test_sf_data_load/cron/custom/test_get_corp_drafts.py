# pylint: disable=redefined-outer-name
import pytest

from sf_data_load.generated.cron import run_cron


@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'B2BCorpDrafts',
            'source_field': 'company_cio',
            'sf_api_name': 'Cio__c',
            'lookup_alias': 'corp_drafts',
            'load_period': 1,
        },
        {
            'source': 'B2BCorpDrafts',
            'source_field': 'company_tin',
            'sf_api_name': 'Tin__c',
            'lookup_alias': 'corp_drafts',
            'load_period': 1,
        },
        {
            'source': 'B2BCorpDrafts',
            'source_field': 'company_name',
            'sf_api_name': 'Name',
            'lookup_alias': 'corp_drafts',
            'load_period': 1,
        },
        {
            'source': 'B2BCorpDrafts',
            'source_field': 'email',
            'sf_api_name': 'Email',
            'lookup_alias': 'corp_drafts',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'corp_drafts': {
            'sf_org': 'b2b',
            'sf_object': 'Account',
            'source_key': 'company_tin',
        },
    },
)
async def test_get_corp_drafts(mock_corp_drafts, pgsql):
    await run_cron.main(
        ['sf_data_load.crontasks.custom.get_corp_drafts', '-t', '0'],
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
                ORDER BY source_field;
            """

    cursor.execute(query)
    data = cursor.fetchall()
    assert data == [
        ('B2BCorpDrafts', 'company_cio', 'Cio__c', 'corp_drafts', '770501001'),
        ('B2BCorpDrafts', 'company_name', 'Name', 'corp_drafts', 'name'),
        (
            'B2BCorpDrafts',
            'company_tin',
            'Tin__c',
            'corp_drafts',
            '500100732259',
        ),
        (
            'B2BCorpDrafts',
            'email',
            'Email',
            'corp_drafts',
            'example@yandex.ru',
        ),
    ]
