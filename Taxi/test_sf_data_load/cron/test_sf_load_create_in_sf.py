# pylint: disable=redefined-outer-name
import datetime

import pytest

from sf_data_load.generated.cron import run_cron
from sf_data_load.stq import sf_load_object
from test_sf_data_load import conftest

SF_DATA_LOAD_SF_RULES = conftest.SF_DATA_LOAD_SF_RULES
SF_DATA_LOAD_LOOKUPS = conftest.SF_DATA_LOAD_LOOKUPS


@pytest.mark.pgsql('sf_data_load', files=('sf_data_load_create_in_sf.sql',))
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=SF_DATA_LOAD_SF_RULES,
    SF_DATA_LOAD_LOOKUPS=SF_DATA_LOAD_LOOKUPS,
    SF_DATA_LOAD_SETTINGS={'size_bulk': 5000},
)
@pytest.mark.now((datetime.datetime(2022, 6, 17)).strftime('%Y-%m-%d'))
async def test_create_in_sf(patch, stq3_context, pgsql):
    @patch('multi_salesforce.multi_salesforce.BulkObject.create')
    async def _create(record):
        i = 1
        for rec in record:
            rec.update({'sf__Id': str(i)})
            i += 1
        return {'successful': record, 'failed': []}

    @patch('sf_data_load.generated.service.stq_client.plugin.QueueClient.call')
    async def _call(**kwargs):
        await sf_load_object.task(
            stq3_context,
            kwargs['kwargs']['lookup_alias'],
            kwargs['kwargs']['tuple_fields'],
        )

    cursor = pgsql['sf_data_load'].cursor()
    cursor.execute('SELECT * FROM sf_data_load.loading_fields')
    data = cursor.fetchall()
    offsets = [str(x[-2]) for x in data]

    await run_cron.main(['sf_data_load.crontasks.sf_load', '-t', '0'])

    cursor.execute(
        f"""
        SELECT * FROM sf_data_load.loading_fields
        WHERE id IN ({', '.join(offsets)})""",
    )
    data = cursor.fetchall()

    assert not data

    cursor.execute(
        f"""
            SELECT * FROM sf_data_load.load_to_yt""",
    )
    data = cursor.fetchall()
    assert data == [
        (
            '1',
            'b2b',
            'Task',
            '{\'DstNumber__c\': \'+7928348868282\', '
            '\'SrcNumber__c\': \'868482\', '
            '\'ExternalId__c\': \'CALLIDFROTESTING12345\', '
            '\'WhoId\': \'0031q00000qKdfEAAS\', '
            '\'OwnerId\': \'0051q000006GytfAAC\', '
            '\'Offset__c\': 1}',
            datetime.datetime(2022, 6, 17, 0, 0),
        ),
    ]

    cursor.execute('SELECT * FROM sf_data_load.sf_b2b_task')
    task_data = cursor.fetchall()
    assert task_data == [
        ('11111111', None, None, None, None, None),
        ('22222222', None, None, None, None, None),
        ('333333333', None, None, None, None, None),
        (
            '1',
            'CALLIDFROTESTING12345',
            '+7928348868282',
            '868482',
            '0031q00000qKdfEAAS',
            '0051q000006GytfAAC',
        ),
    ]
