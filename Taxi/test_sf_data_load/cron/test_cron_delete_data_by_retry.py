# pylint: disable=redefined-outer-name
import datetime

import pytest

from sf_data_load.generated.cron import run_cron
from test_sf_data_load import conftest

SF_DATA_LOAD_SF_RULES = conftest.SF_DATA_LOAD_SF_RULES
SF_DATA_LOAD_LOOKUPS = conftest.SF_DATA_LOAD_LOOKUPS


@pytest.mark.pgsql(
    'sf_data_load', files=('sf_data_load_delete_data_by_retry.sql',),
)
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=SF_DATA_LOAD_SF_RULES,
    SF_DATA_LOAD_LOOKUPS=SF_DATA_LOAD_LOOKUPS,
)
@pytest.mark.now((datetime.datetime(2022, 6, 17)).strftime('%Y-%m-%d'))
async def test_delete_data_by_retry(pgsql):
    cursor = pgsql['sf_data_load'].cursor()
    cursor.execute('SELECT * FROM sf_data_load.loading_fields')
    data = cursor.fetchall()
    await run_cron.main(
        ['sf_data_load.crontasks.delete_data_by_retry', '-t', '0'],
    )
    cursor.execute('SELECT * FROM sf_data_load.loading_fields')
    data = cursor.fetchall()
    offsets = [x[-2] for x in data]
    cnt = [x[-3] for x in data]
    assert offsets == [3, 4, 5]
    assert cnt == [0, 2, 9]
    cursor.execute('SELECT * FROM sf_data_load.load_to_yt ORDER BY value')
    data = cursor.fetchall()
    assert data == [
        (
            'failed',
            'b2b',
            'Task',
            '{"DstNumber__c": "a", "ExternalId__c": "a"}',
            datetime.datetime(2022, 6, 17, 0, 0),
        ),
    ]
