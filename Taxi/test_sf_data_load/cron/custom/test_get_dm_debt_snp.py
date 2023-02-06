# pylint: disable=redefined-outer-name
# pylint: disable=W0212
import datetime
import logging

import pytest

from sf_data_load.generated.cron import run_cron

logger = logging.getLogger(__name__)


@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'B2BDmDebtSnp',
            'source_field': 'corp_contract_id',
            'sf_api_name': 'CorpContractId',
            'lookup_alias': 'dm_debt',
            'load_period': 1,
        },
        {
            'source': 'B2BDmDebtSnp',
            'source_field': 'utc_business_dt',
            'sf_api_name': 'UtcBusinessDt__c',
            'lookup_alias': 'dm_debt',
            'load_period': 1,
        },
        {
            'source': 'B2BDmDebtSnp',
            'source_field': 'invoice_id',
            'sf_api_name': 'InvoiceId',
            'lookup_alias': 'dm_debt',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'dm_debt': {
            'sf_org': 'b2b',
            'sf_object': 'Debt',
            'source_key': 'corp_contract_id',
        },
    },
)
@pytest.mark.yt(static_table_data=['yt_dm_debt_info.yaml'])
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.now((datetime.datetime(2022, 7, 12)).strftime('%Y-%m-%d'))
async def test_get_dm_debt_snp(patch, cron_context, pgsql):
    yt = cron_context.yt_wrapper.hahn  # pylint: disable=C0103

    @patch(
        'sf_data_load.generated.cron.yt_wrapper.plugin.AsyncYTClient.run_map',
    )
    async def _run_map(mapper, source_table, destination_table, **args):
        new_data = []
        for i in map(list, map(mapper, await yt.read_table(source_table))):
            if i:
                new_data.append(i[0])
        await yt.write_table(destination_table, new_data)

    path = '//home/taxi-dwh/cdm/b2b/dm_debt_snp/dm_debt_snp'
    assert await yt.exists(path)

    await run_cron.main(
        ['sf_data_load.crontasks.custom.get_dm_debt_snp', '-t', '0'],
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
        (
            'B2BDmDebtSnp',
            'corp_contract_id',
            'CorpContractId',
            'dm_debt',
            '333885/19',
        ),
        (
            'B2BDmDebtSnp',
            'corp_contract_id',
            'CorpContractId',
            'dm_debt',
            '333886/19',
        ),
        (
            'B2BDmDebtSnp',
            'corp_contract_id',
            'CorpContractId',
            'dm_debt',
            '333884/19',
        ),
        ('B2BDmDebtSnp', 'invoice_id', 'InvoiceId', 'dm_debt', '99908879'),
        ('B2BDmDebtSnp', 'invoice_id', 'InvoiceId', 'dm_debt', '99908877'),
        ('B2BDmDebtSnp', 'invoice_id', 'InvoiceId', 'dm_debt', '99908878'),
        (
            'B2BDmDebtSnp',
            'utc_business_dt',
            'UtcBusinessDt__c',
            'dm_debt',
            '2022-07-11',
        ),
        (
            'B2BDmDebtSnp',
            'utc_business_dt',
            'UtcBusinessDt__c',
            'dm_debt',
            '2022-07-11',
        ),
        (
            'B2BDmDebtSnp',
            'utc_business_dt',
            'UtcBusinessDt__c',
            'dm_debt',
            '2022-07-11',
        ),
    ]
