import io
import time

import mock
import pytest

from contextlib import contextmanager

from context.metadata import metadata_storage
from context.settings import settings
from gpfdist.transforms.yt_writer import read_tsv_lines, _write_static_table, PRE_COMMIT_PERCENT, \
    iterator_with_monitoring, MAX_PERCENT_OF_READING
from . test_statuses_storage import cleaning_up_statuses, prefix


@pytest.mark.parametrize('input, expected_result', (
    ('Foo\n', ['Foo']),
    ('Foo\nBar\n', ['Foo', 'Bar']),
    ('1\t2\n11\t"2\n2"\n\t"33\n"\n',
     ['1\t2', '11\t"2\n2"', '\t"33\n"'])
))
def test_read_tsv_lines(input, expected_result):
    stream = io.StringIO(input)
    result = list(read_tsv_lines(stream))
    assert result == expected_result


@contextmanager
def _temp_process_uuid(prefix):
    with cleaning_up_statuses(prefix):
        process_uuid = metadata_storage.create_process_uuid(
            'test', 'test', 'test', '{}.test'.format(prefix), 'gp_to_yt'
        )

        yield process_uuid


def fake_transaction(do_raise):
    @contextmanager
    def ctx():
        yield
        if do_raise:
            raise ValueError('same err')
    return ctx


@pytest.mark.slow
def test_write_static_table_store_current_progress_100():
    # проверяем что при различных ситуациях статусы проставляются корректно
    client = mock.Mock()
    client.Transaction = fake_transaction(do_raise=False)
    with _temp_process_uuid(prefix()) as process_uuid:
        _write_static_table(process_uuid, 0, 0, range(10), client, '')
        # проверим что при отсутствии ошибок прогресс 100
        assert metadata_storage.get_last_process_log(process_uuid).progress_pcnt == 100


@pytest.mark.slow
def test_write_static_table_store_current_progress_99():
    client = mock.Mock()
    client.Transaction = fake_transaction(do_raise=True)
    with _temp_process_uuid(prefix()) as process_uuid:
        with pytest.raises(ValueError):
            _write_static_table(process_uuid, 0, 0, range(10), client, '')

        # проверим что при возникновении ошибок во время транзакции, последний статус остается на прогрессе 99
        assert metadata_storage.get_last_process_log(process_uuid).progress_pcnt == PRE_COMMIT_PERCENT


@pytest.mark.slow
def test_iterator_with_monitoring_store_prcnt_less_then_max():
    rows = list(range(100))

    with _temp_process_uuid(prefix()) as process_uuid:
        rows_with_mon = iterator_with_monitoring(
            rows,
            rows_count_=len(rows),
            process_uuid=process_uuid,
            page=0,
            attempt=0,
            process_owner='',
            log_extra={},
        )
        for i in rows_with_mon:
            if i == 50:  # статус проставляется после возврата, поэтому 50
                # прошли половину, дождемся записи лога и проверим что записался корректный прогресс
                wait_time = settings('GPFDIST.STATUS_TIME_INTERVAL') + 2
                time.sleep(wait_time)
                st = metadata_storage.get_last_process_log(process_uuid)
                expected = MAX_PERCENT_OF_READING / 2.0
                assert st.progress_pcnt == expected

        assert metadata_storage.get_last_process_log(process_uuid).progress_pcnt == MAX_PERCENT_OF_READING

