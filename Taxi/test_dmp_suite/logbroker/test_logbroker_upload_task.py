import argparse
import contextlib
import dataclasses
import json
import operator
import random
import uuid

import pytest
from kikimr.public.sdk.python.persqueue.grpc_pq_streaming_api import DataBatch
from typing import Any, Iterator, List, Optional

from dmp_suite import yt
from dmp_suite.exceptions import UnsupportedTableError
from dmp_suite.logbroker import task
from dmp_suite.task.execution import run_task
from dmp_suite.yt import NotLayeredYtLayout, NotLayeredYtLocation
from init_py_env import settings
from unittest import mock


class MockLogbrokerProducer:
    def __init__(self, max_seq_no=0):
        self.max_no = max_seq_no
        self.written_batches: List[List[DataBatch]] = []

    def write_batch(self, batch: List[DataBatch]):
        for message in batch:
            assert isinstance(message, DataBatch)
            assert isinstance(message.data, bytes)
            assert message.seq_no > self.max_no
            self.max_no = message.seq_no

        self.written_batches.append(batch)

        return mock.MagicMock()

    @property
    def written_messages(self) -> Iterator[bytes]:
        for batch in self.written_batches:
            for message in batch:
                yield message.data


@pytest.fixture()
def mock_producer():
    return MockLogbrokerProducer()


@pytest.fixture(scope='function')
def mock_logbroker(monkeypatch, mock_producer):
    patch = {
        'logbroker': {
            'host': 'localhost',
            'port': 1234,
            'timeout': 1,
            'tvm_client_id': 1,
            'connections': {'test': {'topic': '/test-topic'}},
        },
    }

    @contextlib.contextmanager
    def mock_get_producer(self, timeout):
        yield mock_producer.max_no, mock_producer

    monkeypatch.setattr(
        task.LogbrokerUploadTask, 'get_producer', mock_get_producer,
    )

    with settings.patch(patch):
        yield mock_producer


class MockYtClient:
    @dataclasses.dataclass
    class TablePath:
        table: str
        exact_key: Optional[Any] = None
        start_index: Optional[int] = None
        end_index: Optional[int] = None

        def __len__(self):
            if self.exact_key:
                return 1
            if self.start_index is not None and self.end_index is not None:
                return len(range(self.start_index, self.end_index))

            raise ValueError('unbounded TablePath range')

    def __init__(self, table_data):
        self.table_data = table_data
        self.read_calls = []

    def read_table(
            self, table_path: TablePath, control_attributes=None, format=None,
    ):
        self.read_calls.append(table_path)
        result = self.table_data
        if control_attributes.get('enable_row_index', False):
            assert format.control_attributes_mode == 'row_fields'

            result = [{**row, '@row_index': i} for i, row in enumerate(result)]

        if table_path.exact_key:
            result = [
                row for row in result if table_path.exact_key in row.values()
            ]
        else:
            result = result[
                slice(table_path.start_index, table_path.end_index)
            ]

        return result


@pytest.fixture()
def mock_yt_client(monkeypatch, mock_yt_table_data):

    client = MockYtClient(mock_yt_table_data)
    monkeypatch.setattr(task.LogbrokerUploadTask, 'yt_client', client)
    return client


@pytest.fixture()
def mock_yt_table_data():
    rd = random.Random()
    rd.seed(12345)
    rows = [
        {
            'uid': rd.randint(1234567, 7654321),
            'key': str(uuid.UUID(int=rd.getrandbits(128), version=4)),
            'campaign_id': 'test_campaign',
        }
        for _ in range(123)
    ]
    return sorted(rows, key=operator.itemgetter('key'))


class SourceTable(yt.YTTable):
    __layout__ = NotLayeredYtLayout('//tmp', 'source-test')
    __location_cls__ = NotLayeredYtLocation
    __unique_keys__ = True

    key = yt.String(sort_key=True)
    user_uid = yt.String()
    campaign = yt.String()


@pytest.mark.parametrize(
    'start_index',
    [
        pytest.param(0, id='fresh start'),
        pytest.param(42, id='resume'),
        pytest.param(123, id='nothing to do'),
    ],
)
def test_load_to_logbroker(
        mock_logbroker, mock_yt_client, mock_yt_table_data, start_index,
):
    test_task = task.LogbrokerUploadTask(
        name='test_logbroker_task',
        source=SourceTable,
        source_idempotency_key_field='key',
        target=task.LogbrokerTarget(connection_name='test'),
        logbroker_source_id='source_id',
    )

    start_key = None
    if start_index > 0:
        start_key = mock_yt_table_data[start_index - 1]['key']

    rows_to_load = mock_yt_table_data[start_index:]

    write_chunk_size = 5
    read_chunk_size = 8
    run_task(
        test_task,
        argparse.Namespace(
            start_key=start_key,
            write_chunk_size=write_chunk_size,
            read_chunk_size=read_chunk_size,
        ),
    )

    for batch in mock_logbroker.written_batches:
        assert len(batch) <= write_chunk_size

    for call in mock_yt_client.read_calls:
        assert len(call) <= read_chunk_size

    written_messages = list(mock_logbroker.written_messages)

    assert len(written_messages) == len(rows_to_load)
    for (message, source_row) in zip(written_messages, rows_to_load):
        assert json.loads(message.decode()) == source_row


def test_incorrect_key(mock_logbroker, mock_yt_client, mock_yt_table_data):
    test_task = task.LogbrokerUploadTask(
        name='test_logbroker_task',
        source=SourceTable,
        source_idempotency_key_field='key',
        target=task.LogbrokerTarget(connection_name='test'),
        logbroker_source_id='source_id',
    )

    last_loaded_key = 'some-invalid-value'
    with pytest.raises(ValueError) as e:
        run_task(
            test_task,
            raw_args=argparse.Namespace(
                start_key=last_loaded_key, retry_times=0,
            ),
        )

    e.match(
        '`key` = \'some-invalid-value\' does not exist in the table',
    )


class NoUniqueKeyTable(yt.YTTable):

    idempotency_key = yt.String(sort_key=True)
    user_uid = yt.String()
    campaign = yt.String()


class WrongSortPosition(yt.YTTable):
    __unique_keys__ = True

    idempotency_key = yt.String(sort_key=True, sort_position=1)
    user_uid = yt.String()
    campaign = yt.String(sort_key=True, sort_position=0)


class CompositeSortKey(yt.YTTable):
    __unique_keys__ = True

    idempotency_key = yt.String(sort_key=True, sort_position=0)
    user_uid = yt.String()
    campaign = yt.String(sort_key=True, sort_position=1)


@pytest.mark.parametrize(
    'table,expected_message',
    [
        (NoUniqueKeyTable, '`idempotency_key` field must be unique'),
        (WrongSortPosition, 'composite sort keys are not yet supported'),
        (CompositeSortKey, 'composite sort keys are not yet supported'),
    ],
)
def test_table_validation(table, expected_message):
    with pytest.raises(UnsupportedTableError) as e:
        task.LogbrokerUploadTask(
            name='test_logbroker_task',
            source=table,
            source_idempotency_key_field='idempotency_key',
            target=task.LogbrokerTarget(connection_name='test'),
            logbroker_source_id='source_id',
        )

    e.match(expected_message)
