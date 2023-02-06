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
            'source': 'B2BCorpContracts',
            'source_field': 'contract_id',
            'sf_api_name': 'ContractId',
            'lookup_alias': 'contracts',
            'load_period': 1,
        },
        {
            'source': 'B2BCorpContracts',
            'source_field': 'balance',
            'sf_api_name': 'Balance__c',
            'lookup_alias': 'contracts',
            'load_period': 1,
        },
        {
            'source': 'B2BCorpContracts',
            'source_field': 'limit',
            'sf_api_name': 'Limit__c',
            'lookup_alias': 'contracts',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'contracts': {
            'sf_org': 'b2b',
            'sf_object': 'Contract',
            'source_key': 'contract_id',
        },
    },
)
@pytest.mark.yt(dyn_table_data=['yt_corp_contracts_info.yaml'])
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.now((datetime.datetime(1998, 6, 21)).strftime('%Y-%m-%d'))
async def test_get_corp_contracts(patch, cron_context, pgsql):
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

    path = '//home/taxi/unittests/replica/mongo/struct/corp/corp_contracts'

    assert await yt.exists(path)
    await yt.unmount_table(path, sync=True)
    await yt.mount_table(path, sync=True)

    await run_cron.main(
        ['sf_data_load.crontasks.custom.get_corp_contracts', '-t', '0'],
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
        ('B2BCorpContracts', 'balance', 'Balance__c', 'contracts', '123.34'),
        ('B2BCorpContracts', 'balance', 'Balance__c', 'contracts', '123.34'),
        (
            'B2BCorpContracts',
            'contract_id',
            'ContractId',
            'contracts',
            '12312',
        ),
        (
            'B2BCorpContracts',
            'contract_id',
            'ContractId',
            'contracts',
            '12316',
        ),
        ('B2BCorpContracts', 'limit', 'Limit__c', 'contracts', '123.45'),
        ('B2BCorpContracts', 'limit', 'Limit__c', 'contracts', '123.45'),
    ]
