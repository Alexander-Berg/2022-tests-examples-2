# pylint: disable=invalid-name, no-self-use, protected-access
import concurrent.futures

import pytest

from replication.common.logbroker import wrapper


_MESSAGES = [b'msg_pt1_%d' % msg_num for msg_num in range(23)]
_MESSAGES.append(b'last')

_REAL_INFLIGHT = 3


@pytest.mark.parametrize('max_inflight', [100, 5])
async def test_logbroker_async_wrapper(
        replication_ctx, monkeypatch, max_inflight,
):
    assert _REAL_INFLIGHT <= max_inflight
    sent = []

    class _DummyProducer:
        def start(self):
            future = concurrent.futures.Future()
            future.set_result(_DummyFutureResult)
            return future

        def __init__(self):
            self._to_send = []

        def write(self, seq_no, message):
            future = concurrent.futures.Future()
            self._to_send.append((future, message))
            if len(self._to_send) == _REAL_INFLIGHT or message == b'last':
                for fut, msg in self._to_send:
                    fut.set_result(_DummyFutureResult)
                    sent.append(msg)
                self._to_send = []
                assert seq_no == len(sent)

            return future

    class _DummyApi:
        def start(self):
            future = concurrent.futures.Future()
            future.set_result('start result')
            return future

        def create_producer(self, *args, **kwargs):
            return _DummyProducer()

    async def _create_api(*args, **kwargs):
        return _DummyApi

    monkeypatch.setattr(
        wrapper.LogbrokerAsyncWrapper, '_create_api', _create_api,
    )

    logbroker = wrapper.LogbrokerAsyncWrapper(
        replication_ctx.shared_deps.client_tvm, max_inflight=max_inflight,
    )
    await logbroker.write(_MESSAGES, '', b'')
    assert sent == _MESSAGES

    sent = []

    def get_actual_producer() -> wrapper._Producer:
        return logbroker._producer_keeper._producers[('', b'', None)]

    producer = get_actual_producer()
    assert producer.is_alive
    producer.is_alive = False

    await logbroker.write(_MESSAGES, '', b'')
    assert sent == _MESSAGES
    assert get_actual_producer().is_alive


class _DummyFutureResult:
    @staticmethod
    def HasField(field):
        return True

    class init:
        max_seq_no = 0
