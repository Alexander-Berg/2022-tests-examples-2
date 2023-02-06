# pylint: disable=redefined-outer-name
# pylint: disable=W0212
import datetime
import inspect
import logging

import pytest

from sf_data_load.utils import constants

logger = logging.getLogger(__name__)


class Mapper:
    def __init__(self, date: datetime.datetime):
        self.date = date

    def __call__(self, row):
        row_date_str = row['utc_business_dt']
        row_date = datetime.datetime.strptime(row_date_str, '%Y-%m-%d')
        if row_date.date() == self.date.date():
            yield row


async def test_mapper_identical():
    from sf_data_load.crontasks.custom import get_dm_contract_snp

    assert inspect.getsource(get_dm_contract_snp.Mapper) == inspect.getsource(
        Mapper,
    ), '_mapper in tests != _mapper in cron'


@pytest.mark.yt(static_table_data=['yt_dm_contract_info.yaml'])
@pytest.mark.now((datetime.datetime(2022, 6, 22)).strftime('%Y-%m-%d'))
async def test_map(yt_apply, cron_context):
    ctx = cron_context
    yt = ctx.yt_wrapper.hahn  # pylint: disable=C0103

    path = '//home/taxi-dwh/cdm/b2b/dm_contract_snp/'
    year = str(datetime.datetime.now().year)
    contract_path = yt.TablePath(path + year)

    tmp_path = constants.YT_HOME + 'tmp'
    current_date = datetime.datetime.now() - datetime.timedelta(days=1)

    with yt.TempTable(tmp_path) as agg_tab:
        await yt.run_map(
            Mapper(current_date),
            source_table=contract_path,
            destination_table=agg_tab,
        )
        output = list(await yt.read_table(agg_tab))

    assert output == [
        {
            'utc_business_dt': '2022-06-21',
            'corp_client_id': '116',
            'utc_drive_first_order_dttm': '136',
            'utc_eda_first_order_dttm': '138',
            'utc_lavka_first_order_dttm': '40',
            'utc_logistics_first_success_order_dttm': '42',
            'utc_taxi_first_success_order_dttm': '144',
        },
        {
            'utc_business_dt': '2022-06-21',
            'corp_client_id': '226',
            'utc_drive_first_order_dttm': '236',
            'utc_eda_first_order_dttm': '238',
            'utc_lavka_first_order_dttm': '40',
            'utc_logistics_first_success_order_dttm': '42',
            'utc_taxi_first_success_order_dttm': '244',
        },
    ]
