import json

import pytest


@pytest.fixture
def logbroker_helper():
    """Calling this helper with your service fixture will return a handler
       that can post messages to logbroker for that service
    """

    class Helper:
        def __init__(self, service_fixture):
            self.service_fixture = service_fixture

        async def send(
                self,
                consumer,
                data,
                topic=None,
                cookie=None,
                source_id=None,
                seq_no=None,
        ):
            """ send specified data (bytes or string) to specified consumer"""
            if topic is None:
                topic = 'some_topic'
            if cookie is None:
                cookie = 'some_cookie'
            response = await self.service_fixture.post(
                '/tests/logbroker/messages',
                data=json.dumps(
                    {
                        'consumer': consumer,
                        'data': data,
                        'cookie': cookie,
                        'topic': topic,
                        'source_id': source_id,
                        'seq_no': seq_no,
                    },
                ),
            )
            assert response.status_code == 200
            return response

        async def send_json(self, consumer, data, topic=None, cookie=None):
            """send data as json"""
            return await self.send(consumer, json.dumps(data), topic, cookie)

    def create_helper(service_fixture):
        return Helper(service_fixture)

    return create_helper
