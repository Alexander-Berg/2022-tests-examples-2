# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=import-only-modules
import asyncio

from geobus_tools.geobus import geobus_publisher_extender  # noqa: F401 C5521
from geopipeline_tools.geopipeline import (  # noqa: F401 C5521
    geopipeline_config,
)  # noqa: F401 C5521
import pytest
from yaga_plugins import *  # noqa: F403 F401


# pylint: disable=redefined-outer-name
@pytest.fixture
@pytest.mark.experiments3(filename='yaga_adjust_type.json')
async def taxi_yaga_simple(
        taxi_yaga,
        geobus_publisher_extender,  # noqa: F811
        geopipeline_config,  # noqa: F811
        redis_store,  # noqa: F811
):
    class TaxiYagaAdv:
        YAGA_TEST_INPUT_CHANNEL = 'test$pp-test-positions$@0'
        YAGA_TEST_OUTPUT_CHANNEL = 'channel:test:adjusted'
        YAGA_TEST_PREDICT_CHANNEL = 'channel:test:predicted'

        base = None
        redis_listener_adjusted = None
        redis_listener_predicted = None

        def __init__(self, service):
            self.service = service

        async def init(self):
            self.base = await geopipeline_config(
                geobus_publisher_extender(self.service),
            )
            print('set config from taxi_yaga_simple')
            self.redis_listener_adjusted = redis_store.pubsub()
            self.redis_listener_predicted = redis_store.pubsub()

            self._subscribe(
                self.redis_listener_adjusted, self.YAGA_TEST_OUTPUT_CHANNEL,
            )
            self._subscribe(
                self.redis_listener_predicted, self.YAGA_TEST_PREDICT_CHANNEL,
            )

            await self.base.update_service_config('pipeline_config_base.json')
            await self._read_all(self.redis_listener_adjusted)

        def send_message(self, message):
            redis_store.publish(self.YAGA_TEST_INPUT_CHANNEL, message)

        def get_adjust_message(self, max_tries=30, retry_message=None):
            # wait while yaga-dispatcher pass messages to output channel
            for _ in range(max_tries):
                message = self.redis_listener_adjusted.get_message(timeout=0.2)
                if message is not None and message['type'] == 'message':
                    return message
                print(message)
            return None

        def get_predicted_message(self, max_tries=30, retry_message=None):
            # wait while yaga-dispatcher pass messages to output channel
            for _ in range(max_tries):
                message = self.redis_listener_predicted.get_message(
                    timeout=0.2,
                )
                if message is not None and message['type'] == 'message':
                    return message
                if retry_message is not None:
                    redis_store.publish(
                        self.YAGA_TEST_PREDICT_CHANNEL, retry_message,
                    )
            return None

        async def _read_all(self, listener):
            # Get all messages from channel
            for _ in range(3):
                while listener.get_message() is not None:
                    print('**********')
                await asyncio.sleep(0.1)

        async def clear_adjusted_channel(self):
            await self._read_all(self.redis_listener_adjusted)

        async def clear_predicted_channel(self):
            await self._read_all(self.redis_listener_predicted)

        def _subscribe(self, listener, channel, try_count=30):
            for _ in range(try_count):
                listener.subscribe(channel)
                message = listener.get_message(timeout=0.2)
                if message is not None and message['type'] == 'subscribe':
                    return
            # failed to subscribe
            assert False

        def __getattr__(self, attr):
            if attr in self.__dict__:
                return getattr(self, attr)
            return getattr(self.service, attr)

    obj = TaxiYagaAdv(taxi_yaga)
    await obj.init()
    return obj


# pylint: disable=redefined-outer-name
@pytest.fixture
@pytest.mark.experiments3(filename='yaga_adjust_type.json')
async def taxi_yaga_adv(taxi_yaga, geopipeline_config):  # noqa: F811
    return await geopipeline_config(taxi_yaga)
