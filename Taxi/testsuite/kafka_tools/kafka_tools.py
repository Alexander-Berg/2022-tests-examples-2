# pylint: disable=import-error

import logging
import os

from confluent_kafka import Producer
import pytest


def _callback(err, msg):
    if err is not None:
        logging.error(f'Failed to deliver message: {str(msg)}: {str(err)}')
    else:
        logging.info(f'Message produced: {str(msg)}')


@pytest.fixture(name='kafka_producer')
def kafka_producer(testpoint):
    class Wrapper:
        def __init__(self, base):
            self.base = base
            conf = {'bootstrap.servers': os.getenv('KAFKA_RECIPE_BROKER_LIST')}
            self.producer = Producer(conf)

        async def produce(
                self,
                topic,
                key,
                value,
                callback=_callback,
                expect_error=False,
                on_error=None,
        ):
            @testpoint('kafka_processing_messages_tp')
            def processing_messages_func(data):
                pass

            @testpoint('kafka_error_processing_messages_tp')
            def error_processing_messages_func(data):
                if on_error is not None:
                    on_error(data)

            await self.base.enable_testpoints()

            self.producer.produce(
                topic, value=value, key=key, on_delivery=callback,
            )
            self.producer.flush()
            if expect_error:
                await error_processing_messages_func.wait_call()
            else:
                await processing_messages_func.wait_call()

    def create_extender(service_fixture):
        return Wrapper(service_fixture)

    return create_extender
