import uuid
from multiprocessing import Event
from unittest import mock

import typing as tp
from kikimr.public.sdk.python.persqueue.grpc_pq_streaming_api import PQStreamingConsumer, ConsumerMessageType

from dmp_suite.logbroker.readers.base import Reader, TargetConfiguration
from dmp_suite.table import LayeredLayout
from dmp_suite.yt import YTTable, Int, YTMeta


class TestTable(YTTable):
    __dynamic__ = True
    __layout__ = LayeredLayout(name='test', layer='test')
    __unique_keys__ = True
    a = Int(sort_key=True)
    b = Int()


timeout = 1


class FutureLike:
    def __init__(self, supplier: tp.Callable):
        self.supplier = supplier

    def result(self, *_, **__):
        return self.supplier()


class MetaLike:
    def __init__(self):
        self.seq_no = str(uuid.uuid4())


class InnerMessageLike:
    def __init__(self, data):
        self.data = data
        self.meta = MetaLike()
        self.offset = 0


class BatchLike:
    def __init__(self, batch: tp.List, topic='TestTopic', partition=0):
        self.message = map(lambda msg: InnerMessageLike(msg), batch)
        self.topic = topic
        self.partition = partition


class DataLike:
    def __init__(self, batches: tp.List[tp.List], **kwargs):
        self.message_batch = map(lambda batch: BatchLike(batch, **kwargs), batches)
        self.cookie = 'OOOH COOOKIE'


class LockReleaseLike:
    def __init__(self, topic='TestTopic', partition=0):
        self.topic = topic
        self.partition = partition


class MessageLike:
    def __init__(self, batches: tp.List[tp.List], is_lock=False, is_release=False, topic='TestTopic', partition=0):
        self.data = DataLike(batches, topic=topic, partition=partition)
        if is_lock:
            self.lock = LockReleaseLike(topic, partition)
        if is_release:
            self.release = LockReleaseLike(topic, partition)

    def HasField(self, field):
        return True


class ResponseLike:
    def __init__(self, message, type):
        self.message = message
        self.type = type
        self.ready_to_read = lambda *args, **kwargs: None


def as_is_decoder(value):
    return value


def nothing_skipper(partition):
    return 0


def get_interrupted_on_empty_supplier(messages):
    def supply():
        if len(messages) == 0:
            raise KeyboardInterrupt('NO MORE MESSAGES!')
        return messages.pop(0)

    return supply


def mock_consumer_interrupt_when_empty(event_batches):
    consumer = mock.MagicMock()
    consumer.next_event = lambda: FutureLike(
        get_interrupted_on_empty_supplier(event_batches))
    consumer.commit = lambda *args: None
    return tp.cast(PQStreamingConsumer, consumer)


def mock_targets():
    table_meta = YTMeta(TestTable)
    return TargetConfiguration(
        table_meta.serializer(**{'a': 'a'}),
        lambda *args: None,
        lambda l: l
    )


def get_reader(consumer, targets, decoder, timeout):
    return Reader(
        consumer, timeout, targets, decoder
    )


def get_default_mocked_reader(logbroker_responses):
    return get_reader(
        mock_consumer_interrupt_when_empty(logbroker_responses),
        [mock_targets()],
        as_is_decoder,
        timeout
    )


def get_consumer_data_message(data: tp.List[tp.List]):
    msg = MessageLike(data)
    type = ConsumerMessageType.MSG_DATA
    return ResponseLike(msg, type)


def get_consumer_msg(data, message_type, **kwargs):
    return ResponseLike(
        MessageLike(data,
                    message_type == ConsumerMessageType.MSG_LOCK,
                    message_type == ConsumerMessageType.MSG_RELEASE,
                    **kwargs),
        message_type
    )


class TestTerminations:

    def test_exit_on_stop_event(self):
        batches = [
            [{'a': 1, 'b': {2}}]
        ]
        reader = get_default_mocked_reader(batches)
        stop_event = Event()
        stop_event.set()
        res = list(reader.run(nothing_skipper, 1, stop_event))
        assert len(res) == 0
        assert len(batches) == 1  # nothing was taken

    def test_exit_on_keyboard_interrupt(self):
        logbroker_responses = [
            get_consumer_data_message([[{'a': 1, 'b': 2}]])
        ]
        reader = get_default_mocked_reader(logbroker_responses)
        res = list(reader.run(nothing_skipper, 1, Event()))
        assert len(res) == 1
        assert len(logbroker_responses) == 0  # no exceptions, gentle exit on KeyboardInterrupt - see get_batch_supplier

    def test_exit_on_all_locked_released(self):
        logbroker_responses = [
            get_consumer_msg([[]], ConsumerMessageType.MSG_LOCK, topic='TT', partition=0),
            get_consumer_msg([[]], ConsumerMessageType.MSG_LOCK, topic='TT', partition=1),
            get_consumer_msg([[]], ConsumerMessageType.MSG_RELEASE, topic='TT', partition=1),
            get_consumer_msg([[{'a': 1}]], ConsumerMessageType.MSG_DATA, topic='TT', partition=0),
            get_consumer_msg([[]], ConsumerMessageType.MSG_LOCK, topic='TT', partition=2),
            get_consumer_msg([[]], ConsumerMessageType.MSG_RELEASE, topic='TT', partition=0),
            get_consumer_msg([[]], ConsumerMessageType.MSG_RELEASE, topic='TT', partition=2)
        ]
        reader = get_default_mocked_reader(logbroker_responses)
        res = list(reader.run(nothing_skipper, 1, Event()))
        assert len(res) == 1
        assert res[0] == {'TT/0': 0}  # offset 0 was put for topic TT and partition 0
        assert len(logbroker_responses) == 0  # no exceptions, gentle exit on KeyboardInterrupt - see get_batch_supplier
