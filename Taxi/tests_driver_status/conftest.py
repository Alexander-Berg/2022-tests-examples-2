# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

import pytest

from driver_status_plugins import *  # noqa: F403 F401

import tests_driver_status.fallback_queue as fallback_queue


@pytest.fixture(name='processing_lb')
async def _processing_lb(taxi_driver_status, testpoint):
    class SendMessageFixture:
        @staticmethod
        async def push(event, timepoint):
            @testpoint('logbroker_commit')
            def commit(cookie):
                assert cookie == 'test_cookie'

            data = {
                'consumer': 'order-events',
                'topic': '/taxi/processing/testing/order-events',
                'cookie': 'test_cookie',
            }
            event['updated'] = timepoint
            data['data'] = json.dumps(event)
            response = await taxi_driver_status.post(
                'tests/logbroker/messages', data=json.dumps(data),
            )
            assert response.status_code == 200
            await commit.wait_call()

    return SendMessageFixture()


@pytest.fixture(autouse=True)
async def _driver_status_fallback_queue_cleaner(
        taxi_driver_status, redis_store,
):
    fallback_queue.clear(redis_store, fallback_queue.STATUS_EVENT_QUEUE)
    fallback_queue.clear(redis_store, fallback_queue.MASTER_ORDER_QUEUE)
    await taxi_driver_status.run_periodic_task('fallback-queues-size-check')
