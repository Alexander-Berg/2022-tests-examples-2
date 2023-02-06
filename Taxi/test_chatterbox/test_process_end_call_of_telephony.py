# pylint: disable=no-member, invalid-name, no-self-use, protected-access
# pylint: disable=redefined-outer-name
import concurrent.futures
import datetime
import json

import pytest

from chatterbox import constants
from chatterbox.internal import logbroker

NOW = datetime.datetime(2019, 7, 25, 10)

sent = []


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ('task_id', 'actions', 'expected_message_service'),
    [
        (
            '666cae5cb2682a976914c2a1',
            ['close'],
            {'timeout': 5, 'type': 'HANGUP'},
        ),
        (
            '777cae5cb2682a976914c2a1',
            ['close'],
            {'timeout': 5, 'type': 'CSAT', 'file': 'second_ask'},
        ),
        ('666cae5cb2682a976914c2a1', ['forward'], None),
    ],
)
@pytest.mark.config(
    CHATTERBOX_CONDITIONAL_CSAT_TELEPHONY={
        'conditions': {'line': {'#in': ['telephony_with_csat']}},
        'fields': {},
        'tags': [],
        'types': [],
        'audio_filename_csat': 'second_ask',
    },
)
async def test_process_end_call_of_telephony(
        cbox, task_id, actions, expected_message_service, monkeypatch,
):
    class _DummyApi:
        def start(self):
            future = concurrent.futures.Future()
            future.set_result('start result')
            return future

        def create_retrying_producer(self, *args, **kwargs):
            return _DummyProducer()

    async def _create_api(*args, **kwargs):
        return _DummyApi

    message_written = []

    class _DummyProducer:
        def start(self):
            future = concurrent.futures.Future()
            future.set_result(_DummyFutureResult)
            return future

        def __init__(self):
            self._to_send = []

        def stop(self):
            pass

        def write(self, seq_no, message):
            message_written.append(message)
            future = concurrent.futures.Future()
            self._to_send.append((future, message))
            _message = json.loads(message)
            _message.pop('id')
            assert _message == {
                'contactPoint': {
                    'id': 'contact_point_id',
                    'channel': constants.TELEPHONY_CHANNEL,
                    'provider': constants.TELEPHONY_PROVIDER,
                },
                'service': expected_message_service,
                'to': {'id': 'call_id'},
            }
            for fut, msg in self._to_send:
                fut.set_result(_DummyFutureResult)
                sent.append(msg)
            self._to_send = []

            return future

    class _DummyFutureResult:
        @staticmethod
        def HasField(field):
            return True

        class init:
            max_seq_no = 0

    monkeypatch.setattr(
        logbroker.LogbrokerAsyncWrapper, '_create_api', _create_api,
    )

    response = await cbox.post(
        f'/v1/tasks/{task_id}/process_end_call_of_telephony',
        data={'actions': actions},
    )
    assert response.status == 200

    if expected_message_service:
        assert len(message_written) == 1
    else:
        assert not message_written
