from contextlib import contextmanager
from datetime import datetime

import pytest

from context.metadata import metadata_storage

GET_PROCESS_UUID_BY_HOST = '''
    SELECT process_uuid FROM gptransfer.process
    WHERE host LIKE %(prefix)s;
'''

DROP_STATUS = '''
    DELETE FROM gptransfer.process
    WHERE process_uuid = %(process_uuid)s;    
'''

DROP_STATUS_LOG = '''
    DELETE FROM gptransfer.process_log
    WHERE process_uuid = %(process_uuid)s;     
'''


@contextmanager
def cleaning_up_statuses(prefix):
    try:
        yield
    finally:
        with metadata_storage.storage_engine.connect() as pgaas_conn:
            query = (
                GET_PROCESS_UUID_BY_HOST,
                dict(prefix="{}%".format(prefix))
            )
            for row in pgaas_conn.execute_and_get_result(query):
                query = (
                    DROP_STATUS,
                    dict(process_uuid=row[0])
                )
                pgaas_conn.execute(query)
                query = (
                    DROP_STATUS_LOG,
                    dict(process_uuid=row[0])
                )
                pgaas_conn.execute(query)


@pytest.fixture
def prefix():
    return str(int(
        (datetime.now() - datetime.utcfromtimestamp(0)).total_seconds()))


@pytest.mark.slow
def test_create_process_uuid(prefix):
    with cleaning_up_statuses(prefix):
        process_uuid = metadata_storage.create_process_uuid(
            'test', 'test', 'test', '{}.test'.format(prefix), 'action')
        assert process_uuid

        process_uuid2 = metadata_storage.create_process_uuid(
            'test2', 'test2', 'test', '{}.test'.format(prefix), 'action')
        assert process_uuid2
        assert process_uuid != process_uuid2


@pytest.mark.slow
def test_send_status_to_pgaas(prefix):
    with cleaning_up_statuses(prefix):
        process_uuid = metadata_storage.create_process_uuid(
            'test', 'test', 'test', '{}.test'.format(prefix), 'action')

        metadata_storage.add_process_log(process_uuid, 'test')
        status = metadata_storage.get_last_process_log(process_uuid)

        assert 'test' == status.log_text
        assert not status.progress_pcnt

        metadata_storage.add_process_log(
            process_uuid, 'test2', progress_pcnt=10, rows_processed=100)
        status = metadata_storage.get_last_process_log(process_uuid)
        assert 'test2' == status.log_text
        assert 10 == status.progress_pcnt
        assert 100 == status.rows_processed

        metadata_storage.add_process_log(
            process_uuid, 'test3')
        status = metadata_storage.get_last_process_log(process_uuid)
        assert 'test3' == status.log_text
        assert 10 == status.progress_pcnt
        assert 100 == status.rows_processed


@pytest.mark.slow
def test_get_process_owner(prefix):
    with cleaning_up_statuses(prefix):
        process_uuid = metadata_storage.create_process_uuid(
            'test', 'test', 'test', '{}.test'.format(prefix), 'action')

        metadata_storage.add_process_log(process_uuid, 'test')
        process_owner = metadata_storage.get_process_owner(process_uuid)

        assert 'test' == process_owner
