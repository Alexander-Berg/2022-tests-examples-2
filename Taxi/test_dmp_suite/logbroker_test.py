from contextlib import contextmanager

import pytest

from dmp_suite import logbroker
from dmp_suite.data_transform import Serializer
from dmp_suite.datetime_utils import utcnow
from dmp_suite.futures_utils import wait_for_first_completed
from dmp_suite.logbroker import LogbrokerConnection
from dmp_suite.logbroker.readers.base import Reader, TargetConfiguration
from dmp_suite.table import Field
from dmp_suite.yt.task.logbroker import get_logbroker_tvm_secret
from init_py_env import settings


@contextmanager
def get_consumer(topic=None):
    connection = LogbrokerConnection(
        host=settings('logbroker.host'),
        port=settings('logbroker.port'),
        timeout=settings('logbroker.timeout'),
        server_tvm_id=settings('logbroker.tvm_client_id'),
    )

    with connection.get_logbroker_api() as api:
        consumer = connection.get_consumer(
            api=api,
            topic=topic or settings('logbroker.connections.logbroker_test.topic'),
            client_id=settings('logbroker.connections.logbroker_test.reader.consumer')
        )
        try:
            yield consumer
        finally:
            consumer.reads_done()


@contextmanager
def get_producer(producer_name='logbroker_test'):
    connection = LogbrokerConnection(
        host=settings('logbroker.host'),
        port=settings('logbroker.port'),
        timeout=settings('logbroker.timeout'),
        server_tvm_id=settings('logbroker.tvm_client_id'),
    )

    with connection.get_logbroker_api() as api:
        _, producer = connection.get_producer(
            api=api,
            source_id=settings(f'logbroker.connections.{producer_name}.writer.source_id'),
            timeout=settings('logbroker.timeout'),
            topic=settings(f'logbroker.connections.{producer_name}.topic'),
        )
        try:
            yield producer
        finally:
            producer.stop()


def write_to_logbroker(producer_name='logbroker_test'):
    with get_producer(producer_name) as producer:
        for i in range(10):
            current_seq_no = logbroker.get_seq_no_from_datetime(utcnow())
            f = producer.write(current_seq_no, i.to_bytes(1, 'big'))
            wait_for_first_completed(f)


@pytest.mark.slow
def test_logbroker_trivial_write_read():
    write_to_logbroker()

    read = []

    target_configurations = [
        TargetConfiguration(
            serializer=Serializer([Field(name='a')], field_extractors={'a': lambda d: d}),
            processor=lambda xs: [read.append(x) for x in xs],
            transform=None,
        )
    ]

    with get_consumer() as consumer:
        reader = Reader(
            consumer=consumer,
            timeout=settings('logbroker.timeout'),
            message_decoder=lambda x: int.from_bytes(x, 'big'),
            infinite=False,
            target_configurations=target_configurations,
        )
        for _ in reader.run(lambda _: None, 1):
            pass

    assert read == [{'a': 0}, {'a': 1}, {'a': 2}, {'a': 3}, {'a': 4}, {'a': 5}, {'a': 6}, {'a': 7}, {'a': 8}, {'a': 9}]


@pytest.mark.slow
def test_logbroker_consumer_connection_error():
    with pytest.raises(ConnectionError):
        with get_consumer(topic='/taxi-dwh/dev/test-logbroker-topic-extra'):
            pass
