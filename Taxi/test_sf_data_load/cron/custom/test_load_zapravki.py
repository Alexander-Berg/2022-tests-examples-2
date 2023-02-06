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
            'source': 'B2BLoadZapravki',
            'source_field': 'refuelings_id',
            'sf_api_name': 'Refuelings_Id__c',
            'lookup_alias': 'load_zapravki',
            'load_period': 1,
        },
        {
            'source': 'B2BLoadZapravki',
            'source_field': 'inn',
            'sf_api_name': 'INN__c',
            'lookup_alias': 'load_zapravki',
            'load_period': 1,
        },
        {
            'source': 'B2BLoadZapravki',
            'source_field': 'const#Yandex Refuelings',
            'sf_api_name': 'Origin',
            'lookup_alias': 'load_zapravki',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'load_zapravki': {
            'sf_org': 'b2b',
            'sf_object': 'Case',
            'source_key': 'refuelings_id',
        },
    },
)
@pytest.mark.yt(static_table_data=['yt_zapravki_corp_client.yaml'])
@pytest.mark.pgsql(
    'sf_data_load', files=('sf_data_load_last_sync_custom_process.sql',),
)
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.now((datetime.datetime(2022, 6, 29)).strftime('%Y-%m-%d'))
async def test_load_zapravki(patch, cron_context, pgsql):
    yt = cron_context.yt_wrapper.hahn  # pylint: disable=C0103
    path = '//home/zapravki/production/export/b2bgo/corp_clients'

    assert await yt.exists(path)
    await run_cron.main(
        ['sf_data_load.crontasks.custom.load_zapravki', '-t', '0'],
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
            'B2BLoadZapravki',
            'const#Yandex Refuelings',
            'Origin',
            'load_zapravki',
            'Yandex Refuelings',
        ),
        ('B2BLoadZapravki', 'inn', 'INN__c', 'load_zapravki', 'inn 2'),
        (
            'B2BLoadZapravki',
            'refuelings_id',
            'Refuelings_Id__c',
            'load_zapravki',
            'id 2',
        ),
    ]
