# pylint: disable=redefined-outer-name
# pylint: disable=W0212
import logging

import pytest

from sf_data_load.generated.cron import run_cron

logger = logging.getLogger(__name__)


@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'B2BCorpContractsAndDebts',
            'source_field': 'contract_id',
            'sf_api_name': 'ContractId',
            'lookup_alias': 'contracts_and_debts',
            'load_period': 1,
        },
        {
            'source': 'B2BCorpContractsAndDebts',
            'source_field': 'debt_more_than_sixty',
            'sf_api_name': 'DebtMoreThanSixty__c',
            'lookup_alias': 'contracts_and_debts',
            'load_period': 1,
        },
        {
            'source': 'B2BCorpContractsAndDebts',
            'source_field': 'act_sum',
            'sf_api_name': 'ActSum__c',
            'lookup_alias': 'contracts_and_debts',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'contracts_and_debts': {
            'sf_org': 'b2b',
            'sf_object': 'ContractAndDebts',
            'source_key': 'contract_id',
        },
    },
)
@pytest.mark.yt(static_table_data=['yt_corp_contracts_and_debts_info.yaml'])
@pytest.mark.usefixtures('yt_apply')
async def test_get_corp_contracts_and_debts(patch, cron_context, pgsql):
    yt = cron_context.yt_wrapper.hahn  # pylint: disable=C0103

    @patch(
        'sf_data_load.generated.cron.yt_wrapper.'
        'plugin.AsyncYTClient.run_reduce',
    )
    async def _run_reduce(_reduce, source_table, destination_table, reduce_by):
        new_data = dict()

        for row in list(await yt.read_table(source_table)):
            if row['contract_id'] not in new_data:
                ans = dict()
                ans['overdue_clean_debt'] = row['overdue_clean_debt']
                ans['debt00'] = row['debt00']
                ans['act_sum'] = row['act_sum']
                ans['invoice_payments_sum'] = row['invoice_payments_sum']
                ans['debt6090'] = row['debt6090']
                ans['debtover90'] = row['debtover90']
                ans['contract_create_dt'] = row['contract_create_dt']
                ans['finish_dt'] = row['finish_dt']
                ans['invoice'] = row['invoice']
                ans['contract_id'] = row['contract_id']
                key = row['contract_id']
                new_data.update({key: ans})
            else:
                value = new_data[row['contract_id']]
                value['overdue_clean_debt'] += row['overdue_clean_debt'] or 0
                value['debt00'] += row['debt00'] or 0
                value['act_sum'] += row['act_sum'] or 0
                value['invoice_payments_sum'] += (
                    row['invoice_payments_sum'] or 0
                )
                value['debt6090'] += row['debt6090'] or 0
                value['debtover90'] += row['debtover90'] or 0

                if 'invoice' not in value:
                    value['contract_create_dt'] = row['contract_create_dt']
                    value['finish_dt'] = row['finish_dt']
                    value['invoice'] = row['invoice']
                    value['contract_id'] = row['contract_id']
        await yt.write_table(destination_table, list(new_data.values()))

    path = (
        '//home/taxi-dwh/import/yandex-balance/corporate_contracts_and_debts'
    )

    assert await yt.exists(path)

    await run_cron.main(
        [
            'sf_data_load.crontasks.custom.get_yt_corp_contracts_and_debts',
            '-t',
            '0',
        ],
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
            'B2BCorpContractsAndDebts',
            'act_sum',
            'ActSum__c',
            'contracts_and_debts',
            '0.0',
        ),
        (
            'B2BCorpContractsAndDebts',
            'act_sum',
            'ActSum__c',
            'contracts_and_debts',
            '0.0',
        ),
        (
            'B2BCorpContractsAndDebts',
            'contract_id',
            'ContractId',
            'contracts_and_debts',
            '9',
        ),
        (
            'B2BCorpContractsAndDebts',
            'contract_id',
            'ContractId',
            'contracts_and_debts',
            '12312',
        ),
        (
            'B2BCorpContractsAndDebts',
            'debt_more_than_sixty',
            'DebtMoreThanSixty__c',
            'contracts_and_debts',
            '76.0',
        ),
        (
            'B2BCorpContractsAndDebts',
            'debt_more_than_sixty',
            'DebtMoreThanSixty__c',
            'contracts_and_debts',
            '38.0',
        ),
    ]
