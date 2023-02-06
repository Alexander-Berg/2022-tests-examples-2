import collections
import inspect
import logging

import pytest

from sf_data_load.utils import constants

logger = logging.getLogger(__name__)


def yt_reducer(key, rows):
    ans = collections.defaultdict(lambda: 0)

    for row in rows:
        ans['overdue_clean_debt'] += row['overdue_clean_debt'] or 0
        ans['debt00'] += row['debt00'] or 0
        ans['act_sum'] += row['act_sum'] or 0
        ans['invoice_payments_sum'] += row['invoice_payments_sum'] or 0
        ans['debt6090'] += row['debt6090'] or 0
        ans['debtover90'] += row['debtover90'] or 0

        if 'invoice' not in ans:
            ans['contract_create_dt'] = row['contract_create_dt']
            ans['finish_dt'] = row['finish_dt']
            ans['invoice'] = row['invoice']
            ans['contract_id'] = key['contract_id']

    yield dict(ans)


async def test_reducer_identical():
    from sf_data_load.crontasks.custom import get_yt_corp_contracts_and_debts

    assert inspect.getsource(
        get_yt_corp_contracts_and_debts.yt_reducer,
    ) == inspect.getsource(yt_reducer), '_reducer in tests != _reducer in cron'


@pytest.mark.yt(static_table_data=['yt_corp_contracts_and_debts_info.yaml'])
async def test_reduce(yt_apply, cron_context):
    ctx = cron_context
    yt = ctx.yt_wrapper.hahn  # pylint: disable=C0103

    table_path = yt.TablePath(
        '//home/taxi-dwh/import/yandex-balance/corporate_contracts_and_debts',
    )

    tmp_path = constants.YT_HOME + 'tmp'
    with yt.TempTable(tmp_path) as agg_tab, yt.TempTable(tmp_path) as sort_t:
        await yt.run_sort(
            source_table=table_path,
            destination_table=sort_t,
            sort_by=['contract_id'],
        )
        await yt.run_reduce(
            yt_reducer,
            source_table=sort_t,
            destination_table=agg_tab,
            reduce_by=['contract_id'],
        )
        output = list(await yt.read_table(agg_tab))

    assert output == [
        {
            'overdue_clean_debt': 74.0,
            'debt00': 28.0,
            'act_sum': 0,
            'invoice_payments_sum': 52.0,
            'debt6090': 34.0,
            'debtover90': 42.0,
            'contract_create_dt': '8',
            'finish_dt': '23',
            'invoice': '24',
            'contract_id': 9,
        },
        {
            'overdue_clean_debt': 37.0,
            'debt00': 14.0,
            'act_sum': 0,
            'invoice_payments_sum': 26.0,
            'debt6090': 17.0,
            'debtover90': 21.0,
            'contract_create_dt': '8',
            'finish_dt': '23',
            'invoice': '24',
            'contract_id': 12312,
        },
    ]
