# pylint: disable=redefined-outer-name
import pytest

from sf_data_load.generated.cron import run_cron
from sf_data_load.stq import sf_unload_object


@pytest.mark.usefixtures('salesforce')
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'db',
            'source_field': 'name',
            'sf_api_name': 'Name',
            'lookup_alias': 'lookup',
            'load_period': 1,
        },
        {
            'source': 'db',
            'source_field': 'name',
            'sf_api_name': 'Phone',
            'lookup_alias': 'lookup',
            'load_period': 1,
        },
        {
            'source': 'sf|b2b|test',
            'source_field': 'Id_temp',
            'sf_api_name': 'WhatId',
            'lookup_alias': 'lookup',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'lookup': {
            'sf_org': 'b2b',
            'sf_object': 'test',
            'source_key': 'BIN__c',
        },
    },
)
async def test_sf_unload(mock_salesforce_auth, pgsql, stq3_context, patch):
    @patch('sf_data_load.generated.service.stq_client.plugin.QueueClient.call')
    async def _call(**kwargs):
        await sf_unload_object.task(
            stq3_context,
            kwargs['kwargs']['org'],
            kwargs['kwargs']['object_name'],
            kwargs['kwargs']['fields'],
        )

    cursor = pgsql['sf_data_load'].cursor()
    query_time = 'SELECT * FROM sf_data_load.last_sync_unload_time'
    cursor.execute(query_time)
    data = cursor.fetchall()
    assert not data

    await run_cron.main(['sf_data_load.crontasks.sf_unload', '-t', '0'])
    cursor.execute(query_time)
    data = cursor.fetchall()
    assert data[0][0] == 'sf_b2b_test'

    query_check_table = """SELECT * FROM
                               INFORMATION_SCHEMA.COLUMNS
                           WHERE
                               table_schema = 'sf_data_load'
                               AND
                               table_name = 'sf_b2b_test'"""
    cursor.execute(query_check_table)
    data = cursor.fetchall()
    assert data

    query_in_table = 'SELECT * FROM sf_data_load.sf_b2b_test'
    cursor.execute(query_in_table)
    data = cursor.fetchall()
    assert data[0][0] == '1'
    assert data[0][1] == 'bin_value'
    assert data[0][2] == 'inn_value'
    assert data[0][3] == 'data_value'

    query_check_table = """SELECT * FROM
                               INFORMATION_SCHEMA.COLUMNS
                           WHERE
                               table_schema = 'sf_data_load'
                               AND
                               table_name = 'not_table'"""
    cursor.execute(query_check_table)
    data = cursor.fetchall()
    assert not data

    cursor.execute('SELECT * FROM sf_data_load.loading_fields')
    data = cursor.fetchall()
    print(data)


@pytest.mark.usefixtures('salesforce')
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'db',
            'source_field': 'name',
            'sf_api_name': 'Name',
            'lookup_alias': 'lookup',
            'load_period': 1,
        },
        {
            'source': 'db',
            'source_field': 'name',
            'sf_api_name': 'Phone',
            'lookup_alias': 'lookup',
            'load_period': 1,
        },
        {
            'source': 'sf|b2b|test',
            'source_field': 'Id_temp',
            'sf_api_name': 'WhatId',
            'lookup_alias': 'lookup',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'lookup': {
            'sf_org': 'b2b',
            'sf_object': 'test',
            'source_key': 'BIN__c',
        },
    },
)
async def test_sf_unload_delete_column(
        mock_salesforce_auth, pgsql, stq3_context, patch,
):
    @patch('sf_data_load.generated.service.stq_client.plugin.QueueClient.call')
    async def _call(**kwargs):
        await sf_unload_object.task(
            stq3_context,
            kwargs['kwargs']['org'],
            kwargs['kwargs']['object_name'],
            kwargs['kwargs']['fields'],
        )

    cursor = pgsql['sf_data_load'].cursor()
    query = f"""
        INSERT INTO sf_data_load.last_sync_unload_time
        (table_name, last_sync, is_active)
        VALUES ('sf_b2b_test', '2022-05-25 12:53:35.000000', False)
    """
    cursor.execute(query)
    query = """DROP TABLE sf_data_load.sf_b2b_test"""
    cursor.execute(query)

    query = """
        CREATE TABLE IF NOT EXISTS
        sf_data_load.sf_b2b_test ("Id" varchar primary key, "A" varchar)
        """
    cursor.execute(query)
    query_get_column = """
        SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS
        WHERE table_schema = 'sf_data_load' AND table_name = 'sf_b2b_test'
    """

    await run_cron.main(['sf_data_load.crontasks.sf_unload', '-t', '0'])

    cursor.execute(query_get_column)
    columns = cursor.fetchall()
    columns = {col[0] for col in columns}
    assert not (
        columns - {'Id', 'WhatId', 'Name', 'Id_temp', 'BIN__c', 'Phone'}
    )


@pytest.mark.usefixtures('salesforce')
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'db',
            'source_field': 'name',
            'sf_api_name': 'Name',
            'lookup_alias': 'lookup',
            'load_period': 1,
        },
        {
            'source': 'db',
            'source_field': 'name',
            'sf_api_name': 'Phone',
            'lookup_alias': 'lookup',
            'load_period': 1,
        },
        {
            'source': 'sf|b2b|test',
            'source_field': 'Id_temp',
            'sf_api_name': 'WhatId',
            'lookup_alias': 'lookup',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'lookup': {
            'sf_org': 'b2b',
            'sf_object': 'test',
            'source_key': 'BIN__c',
        },
    },
)
async def test_sf_unload_update_column_if_time_none(
        mock_salesforce_auth, pgsql, stq3_context, patch,
):
    @patch('sf_data_load.generated.service.stq_client.plugin.QueueClient.call')
    async def _call(**kwargs):
        await sf_unload_object.task(
            stq3_context,
            kwargs['kwargs']['org'],
            kwargs['kwargs']['object_name'],
            kwargs['kwargs']['fields'],
        )

    cursor = pgsql['sf_data_load'].cursor()
    query = """DROP TABLE sf_data_load.sf_b2b_test"""
    cursor.execute(query)

    query = """
        CREATE TABLE IF NOT EXISTS
        sf_data_load.sf_b2b_test ("Id" varchar primary key, "A" varchar)
        """
    cursor.execute(query)
    query_get_column = """
        SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS
        WHERE table_schema = 'sf_data_load' AND table_name = 'sf_b2b_test'
    """

    await run_cron.main(['sf_data_load.crontasks.sf_unload', '-t', '0'])

    cursor.execute(query_get_column)
    columns = cursor.fetchall()
    columns = {col[0] for col in columns}
    assert not (
        columns - {'Id', 'WhatId', 'Name', 'Id_temp', 'BIN__c', 'Phone'}
    )
