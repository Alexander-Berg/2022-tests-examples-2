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
            'source': 'B2BDmContractsSnp',
            'source_field': 'corp_client_id',
            'sf_api_name': 'CorpClientId',
            'lookup_alias': 'dm_contract',
            'load_period': 1,
        },
        {
            'source': 'B2BDmContractsSnp',
            'source_field': 'utc_business_dt',
            'sf_api_name': 'UtcBusinessDt__c',
            'lookup_alias': 'dm_contract',
            'load_period': 1,
        },
        {
            'source': 'B2BDmContractsSnp',
            'source_field': 'utc_drive_first_order_dttm',
            'sf_api_name': 'UtcDriveFirstOrderDttm__c',
            'lookup_alias': 'dm_contract',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'dm_contract': {
            'sf_org': 'b2b',
            'sf_object': 'Contract',
            'source_key': 'corp_client_id',
        },
    },
)
@pytest.mark.yt(static_table_data=['yt_dm_contract_info.yaml'])
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.now((datetime.datetime(2022, 6, 22)).strftime('%Y-%m-%d'))
async def test_get_dm_contract_snp(patch, cron_context, pgsql):
    yt = cron_context.yt_wrapper.hahn  # pylint: disable=C0103

    @patch(
        'sf_data_load.generated.cron.yt_wrapper.plugin.AsyncYTClient.run_map',
    )
    async def _run_map(mapper, source_table, destination_table):
        new_data = []
        for i in map(list, map(mapper, await yt.read_table(source_table))):
            if i:
                new_data.append(i[0])
        await yt.write_table(destination_table, new_data)

    path = '//home/taxi-dwh/cdm/b2b/dm_contract_snp/'
    year = str(datetime.datetime.now().year)
    path = path + year

    assert await yt.exists(path)

    await run_cron.main(
        ['sf_data_load.crontasks.custom.get_dm_contract_snp', '-t', '0'],
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
            'B2BDmContractsSnp',
            'corp_client_id',
            'CorpClientId',
            'dm_contract',
            '116',
        ),
        (
            'B2BDmContractsSnp',
            'corp_client_id',
            'CorpClientId',
            'dm_contract',
            '226',
        ),
        (
            'B2BDmContractsSnp',
            'utc_business_dt',
            'UtcBusinessDt__c',
            'dm_contract',
            '2022-06-21',
        ),
        (
            'B2BDmContractsSnp',
            'utc_business_dt',
            'UtcBusinessDt__c',
            'dm_contract',
            '2022-06-21',
        ),
        (
            'B2BDmContractsSnp',
            'utc_drive_first_order_dttm',
            'UtcDriveFirstOrderDttm__c',
            'dm_contract',
            '136',
        ),
        (
            'B2BDmContractsSnp',
            'utc_drive_first_order_dttm',
            'UtcDriveFirstOrderDttm__c',
            'dm_contract',
            '236',
        ),
    ]
