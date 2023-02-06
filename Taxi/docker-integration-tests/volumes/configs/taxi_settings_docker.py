import logging

# pylint: disable=import-error, wildcard-import
from taxi.conf import settings
from taxi_settings import *  # noqa: F403, F401

LOG_LEVEL = logging.DEBUG


MCROUTER_HOSTS = ['memcached.taxi.yandex:11211']
MEMCACHED_HOSTS = MCROUTER_HOSTS
FAKE_RIDE_TIME = 10
TIME_BEFORE_CLEAR = 30

STQ_ALLOW_DEFAULT_SETTINGS = True

settings.STQ_NODE_ID = 'default'
settings.STQ_WORKLOAD = {
    settings.STQ_NODE_ID: {
        settings.STQ_LOOKUP_QUEUE: [0],
        settings.STQ_PROCESS_CHANGE_QUEUE: [0],
        settings.STQ_UPDATE_TRANSACTIONS_QUEUE: [0],
        settings.STQ_ANTIFRAUD_PROC_QUEUE: [0],
        settings.STQ_NOTIFY_ON_CHANGE_QUEUE: [0],
    },
}

settings.ORDER_PROC_SHARDS_QUERIES_ENABLED = True
settings.ORDERS_SHARDS_QUERIES_ENABLED = True

for worker in settings.STQ_WORKERS.values():
    worker['instances'] = 1
