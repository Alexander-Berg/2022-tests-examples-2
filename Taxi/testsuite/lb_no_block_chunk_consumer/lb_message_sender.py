import json

import pytest


# example of fixture
@pytest.fixture(name='lb_message_sender')
async def _lb_message_sender(taxi_callcenter_stats, load, testpoint):
    class SendMessageFixture:
        @staticmethod
        async def send(consumer_name, message, raw=False, **kwargs):
            @testpoint('logbroker_commit')
            def commit(cookie):
                assert cookie == 'cookie1'

            if not isinstance(message, list):
                messages = [message]
            else:
                messages = message
            for msg in messages:
                response = await taxi_callcenter_stats.post(
                    'tests/logbroker/messages',
                    data=json.dumps(
                        {
                            'consumer': consumer_name,
                            'data': msg if raw else load(msg),
                            'topic': '/taxi/callcenter/production/qapp-events',
                            'cookie': 'cookie1',
                            **kwargs,
                        },
                    ),
                )
                assert response.status_code == 200

            # flush all other messages from queue
            async with taxi_callcenter_stats.spawn_task('qapp-event-consumer'):
                for _ in messages:
                    await commit.wait_call()

    return SendMessageFixture()
