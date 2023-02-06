#!/usr/bin/env python
# -*- coding: utf-8 -*

import importlib
import os
import re
import sys

import redis


REDIS_HOST = 'redis.taxi.yandex'
REDIS_PORT = 6379

PATHS_TO_SCRIPTS = ['/taxi/bootstrap_db/redis/']

PYS_SEARCH_RE = r'(db_.+)\.py'
IFACE_FUN = 'populate_data'


def get_redis_connection():
    return redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


def fetch_modules():
    modules = []

    for path in PATHS_TO_SCRIPTS:
        if not os.path.exists(path):
            raise Exception('Path "{}" does not exist'.format(path))

        sys.path.append(path)

        for file_name in os.listdir(path):
            match = re.match(PYS_SEARCH_RE, file_name)

            if match is not None:
                module_name = match.group(1)

                print('Importing module {}'.format(module_name))
                module = importlib.import_module(module_name)

                if hasattr(module, IFACE_FUN):
                    modules.append(module)
                else:
                    raise Exception(
                        '{} has no {} function'.format(module_name, IFACE_FUN),
                    )

    return modules


def populate_data(connection, modules):
    for module in modules:
        module.populate_data(connection)


def init():
    connection = get_redis_connection()
    modules = fetch_modules()
    populate_data(connection, modules)
