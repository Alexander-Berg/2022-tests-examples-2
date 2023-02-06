# pylint: disable=import-error,invalid-name,useless-object-inheritance
# pylint: disable=undefined-variable,unused-variable,too-many-lines
# pylint: disable=no-name-in-module
# flake8: noqa F501 F401 F841 F821
import pytest
import asyncio
from typing import Dict

import redis as redisdb
import json


class ListenerWraper:
    def __init__(self, listener, channel=None) -> None:
        self.listener = listener
        self.channel = channel

    async def clean(self):
        print('cleaning listener')
        for _ in range(3):
            while self.listener.get_message() is not None:
                print(f'{self.channel}: **********')
            await asyncio.sleep(0.1)

    def get_message(self, max_tries=30):
        for _ in range(max_tries):
            message = self.listener.get_message(timeout=0.2)
            if message is not None and message['type'] == 'message':
                return message
        return None


class PublisherWraper:
    def __init__(self, redis_store, channel) -> None:
        self.redis_store = redis_store
        self.channel = channel

    def publish(self, message):
        self.redis_store.publish(self.channel, message)


class GeobusRedisHolder:
    try_count = 30

    def __init__(self) -> None:
        self.publishers: Dict[str, PublisherWraper] = {}
        self.listeners: Dict[str, ListenerWraper] = {}
        self.redis_store = None

    def set_redis_store(self, redis_store):
        if self.redis_store is None:
            self.redis_store = redis_store

    async def get_listener(self, channel):
        if channel in self.listeners.keys():
            return self.listeners[channel]

        print(f'creating listener for channle {channel}')
        for _ in range(self.try_count):
            listener = self.redis_store.pubsub()
            listener.subscribe(channel)
            message = listener.get_message(timeout=0.2)
            if message is not None and message['type'] == 'subscribe':
                new_listener = ListenerWraper(listener, channel)
                await new_listener.clean()
                self.listeners[channel] = new_listener
                return new_listener

        assert False, f'Wasn\'t able to create listener for channel {channel}'

    async def get_publisher(self, channel):
        if channel in self.listeners.keys():
            return self.listeners[channel]

        print(f'creating publisher for channle {channel}')
        new_publisher = PublisherWraper(self.redis_store, channel)
        self.publishers[channel] = new_publisher
        return new_publisher

    async def clear_listeners(self):
        print(f'clearing listeners')
        for listener in self.listeners.values():
            await listener.clean()


class GeobusRedisGetter:
    def __init__(
            self, geobus_redis_holder, redis_store,
    ):  # pylint: disable=W0621
        self.geobus_redis_holder = geobus_redis_holder
        self.geobus_redis_holder.set_redis_store(redis_store)

    async def init(self):
        print(f'init GeobusRedisGetter')
        await self.geobus_redis_holder.clear_listeners()

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self.geobus_redis_holder, attr)


@pytest.fixture(scope='session')
def geobus_redis_holder():
    return GeobusRedisHolder()


@pytest.fixture
async def geobus_redis_getter(
        geobus_redis_holder, redis_store,
):  # pylint: disable=W0621
    obj = GeobusRedisGetter(geobus_redis_holder, redis_store)
    await obj.init()
    return obj


def _json_object_hook(dct):
    if '$json' in dct:
        return json.dumps(dct['$json'])
    return dct
