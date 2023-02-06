#!/usr/bin/env python
# -*- coding: utf-8 -*

from __future__ import print_function
from __future__ import unicode_literals

import codecs
import datetime
import os
import re

from bson import json_util
import pymongo

import mongo_schema
import bootstrap_configs_admin

JSONS_SEARCH_RE = r'db_(.*)\.json'
PATHS_TO_INPUT_JSONS = [
    '/taxi/bootstrap_db/db_data/',
]
SPECIAL_FILE_NAMES = {
    'config': bootstrap_configs_admin.process_config_values,
    'uconfigs_meta': bootstrap_configs_admin.process_meta,
    'uconfigs_schemas': bootstrap_configs_admin.process_schemas,
    'uconfigs_schemas_definitions': (
        bootstrap_configs_admin.process_schemas_definitions
    ),
}
DB_SETTINGS_PATH = '/taxi/schemas/mongo'
YAML_TYPE_TO_PYMONGO_SPECIFIER = {
    'ascending': pymongo.ASCENDING,
    'descending': pymongo.DESCENDING,
    '2d': pymongo.GEO2D,
    '2dsphere': pymongo.GEOSPHERE,
    'hashed': pymongo.HASHED,
    'text': pymongo.TEXT,
}


def json_loads(text, *args, **kwargs):
    """Helper function that wraps `json.loads`.

    Automatically passes the object_hook for BSON type conversion.
    """
    if 'now' in kwargs:
        now = kwargs.pop('now')
    else:
        now = datetime.datetime.utcnow()

    def object_hook(dct):
        if '$dateDiff' in dct:
            seconds = int(dct['$dateDiff'])
            return now + datetime.timedelta(seconds=seconds)
        return json_util.object_hook(dct)
    kwargs['object_hook'] = object_hook
    return json_util.json.loads(text, *args, **kwargs)


def search_collection_files(path, pattern):
    result = {}
    if not os.path.exists(path):
        print('WARNING: path does not exists', path)
        return {}
    for file_name in os.listdir(path):
        match = re.match(pattern, file_name)
        if match is not None:
            collection_name = match.group(1)
            full_path = os.path.join(path, file_name)
            result[collection_name] = full_path
    return result


def build_migration_list(paths, pattern):
    search_results = []
    for path in paths:
        search_results.append(search_collection_files(path, pattern))
    result = {}
    for search_result in reversed(search_results):
        for collection_name, full_path in search_result.iteritems():
            result[collection_name] = full_path
    return result


def get_data_from_json_files(paths, pattern):
    migration_list = build_migration_list(paths, pattern)
    result = {}
    for collection_name, full_path in migration_list.iteritems():
        print('Loading {} collection from {}'.format(
            collection_name, full_path))
        with codecs.open(full_path, encoding='utf-8') as fp:
            content = fp.read()
            data = json_loads(content)
            result[collection_name] = data
    return result


def upload_data(connection, db_settings, data):
    # Uploads the data to mongo
    # The data is the dict from collection_name to iterable of docs
    for collection_name, docs in data.items():
        settings = db_settings[collection_name]['settings']
        database = getattr(connection, settings['database'])
        collection = getattr(database, settings['collection'])
        collection.remove({})
        if collection_name in SPECIAL_FILE_NAMES:
            print('Fill special `{}`'.format(collection_name))
            docs = SPECIAL_FILE_NAMES[collection_name](docs)
        try:
            if docs:
                collection.insert_many(docs)
        except pymongo.errors.BulkWriteError as e:
            raise Exception(
                'Error: Can not write to collection "{}": {}'.format(
                    collection_name, e),
            )


def get_pymongo_connection():
    return pymongo.MongoClient(
        host='mongodb://mongo.taxi.yandex:27017/',
        socketTimeoutMS=60000,
        connectTimeoutMS=10000,
        waitQueueTimeoutMS=10000,
    )


def shard_collection(collection, sharding):
    db_admin = collection.database.client.admin
    try:
        db_admin.command(
            'enablesharding', collection.database.name,
        )
    except pymongo.errors.OperationFailure as exc:
        if exc.code != 23:
            raise
    kwargs = _get_kwargs_for_shard_func(sharding)
    if not _is_collection_sharded(collection):
        db_admin.command('shardcollection', collection.full_name, **kwargs)


def ensure_indexes(connection, db_settings):
    for alias, value in db_settings.items():
        database = getattr(connection, value['settings']['database'])
        collection = database.create_collection(
            value['settings']['collection'],
        )
        indexes = value.get('indexes', [])
        for index in indexes:
            arg, kwargs = _get_args_for_ensure_func(index)
            collection.ensure_index(arg, **kwargs)

        index_information = collection.index_information()
        assert len(index_information) == len(indexes) + 1

        sharding = value.get('sharding')
        if sharding:
            shard_collection(collection, sharding)


def ensure_stq_indexes(connection, db_settings):
    stq_config_settings = db_settings['stq_config']['settings']

    stq_config_db = getattr(connection, stq_config_settings['database'])
    stq_config = getattr(stq_config_db, stq_config_settings['collection'])

    indexes = ('e', 'x', 'f')

    for stq in stq_config.find():
        for shard_settings in stq['shards']:
            shard_db = getattr(connection, shard_settings['database'])
            collection = shard_settings['collection']
            try:
                shard_db.create_collection(collection)
            except pymongo.errors.CollectionInvalid:
                pass
            shard = getattr(shard_db, collection)

            for index in indexes:
                shard.ensure_index(index, background=True)

            assert len(shard.index_information()) == len(indexes) + 1


def _get_args_for_ensure_func(index):
    kwargs = {}
    for key, value in index.items():
        if key == 'key':
            if isinstance(value, str):
                arg = index['key']
            elif isinstance(value, list):
                arg = [
                    (obj['name'], YAML_TYPE_TO_PYMONGO_SPECIFIER[obj['type']])
                    for obj in value
                ]
        else:
            kwargs[key] = value
    return arg, kwargs


def _get_kwargs_for_shard_func(sharding):
    kwargs = {}
    for key, value in sharding.items():
        if key == 'key':
            if isinstance(value, str):
                sharding_key = {value: 1}
            elif isinstance(value, list):
                sharding_key = {}
                for obj in value:
                    sharding_key[obj['name']] = (
                        YAML_TYPE_TO_PYMONGO_SPECIFIER[obj['type']]
                    )
            else:
                raise ValueError('Cannot handle sharding key: %r' % (value,))
            kwargs['key'] = sharding_key
        else:
            kwargs[key] = value
    return kwargs


def _is_collection_sharded(collection):
    collstats = collection.database.command('collstats', collection.name)
    return collstats.get('sharded')


def init():
    connection = get_pymongo_connection()
    db_settings = mongo_schema.MongoSchema(DB_SETTINGS_PATH)
    ensure_indexes(connection, db_settings)
    data_to_load = get_data_from_json_files(
        PATHS_TO_INPUT_JSONS, JSONS_SEARCH_RE,
    )
    upload_data(connection, db_settings, data_to_load)
    ensure_stq_indexes(connection, db_settings)
