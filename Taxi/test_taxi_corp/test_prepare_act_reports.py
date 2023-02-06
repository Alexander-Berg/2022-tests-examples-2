import datetime

import pytest

from taxi_corp import cron_run

NEW_DATE = datetime.datetime(year=2021, month=5, day=10)
OLD_DATE = datetime.datetime(year=2020, month=12, day=10)


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.parametrize(
    ['act_date', 'used_fields'],
    [
        pytest.param(
            '2021-04',
            {'absent': 'promo_sum_wo_nds', 'present': 'promo_value_wo_nds'},
            marks=pytest.mark.now(NEW_DATE.isoformat()),
            id='prepare report with new promo column',
        ),
        pytest.param(
            '2020-11',
            {'absent': 'promo_value_wo_nds', 'present': 'promo_sum_wo_nds'},
            marks=pytest.mark.now(OLD_DATE.isoformat()),
            id='prepare report with old promo column',
        ),
    ],
)
async def test_prepare_act_reports(
        db, patch, load, load_json, act_date, used_fields,
):
    @patch('taxi.settings.get_environment')
    def _get_environment():
        return 'production'

    @patch('taxi_corp.internal.yql_manager.YqlManager.run_query')
    async def _run_query(query, title, query_parameters=None, **kwargs):
        assert query_parameters is None
        if title == 'prepare_raw_act_report':
            assert used_fields['present'] in query
            assert used_fields['absent'] not in query
            expected_query = (
                load('prepare-2021-11.yql')
                .replace(used_fields['absent'], used_fields['present'])
                .replace('2021-11', act_date)
            )
            assert query == expected_query
            assert ' amount,' not in query  # CORPDEV-3080
        elif title == 'check_act_reports':
            expected_query = load('check-2021-11.yql').replace(
                '2021-11', act_date,
            )
            assert query == expected_query
        elif title == 'get_missing_orders_from_act':
            expected_query = load('missing-orders-2021-11.yql').replace(
                '2021-11', act_date,
            )
            assert query == expected_query
            return load_json('yql-missing-orders.json')

    @patch('yt.wrapper.YtClient.read_table')
    def _read_table(*args):
        table_path_str = str(args[0])
        if 'corp_contracts' in table_path_str:
            return load_json('yt_corp_contracts.json')
        return load_json('yt_discrepancies.json')

    await cron_run.main(['taxi_corp.stuff.prepare_act_reports', '-t', '0'])
    docs = await db.corp_detailed_acts.find().to_list(None)
    expected_docs = {
        doc['contract_eid']: doc
        for doc in load_json('expected_corp_detailed_acts.json')
    }
    assert len(docs) == len(expected_docs)
    for doc in docs:
        expected_doc = expected_docs[doc['contract_eid']]
        doc.pop('updated')
        doc.pop('_id')
        assert doc.pop('act_date') == act_date
        assert doc.pop('created') == datetime.datetime.utcnow()
        assert doc == expected_doc
