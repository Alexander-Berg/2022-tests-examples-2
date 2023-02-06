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
import yaml

JSONS_SEARCH_RE = r'db_(.*)\.json'
PATHS_TO_INPUT_JSONS = ['/taxi/atlas/bootstrap_db/db_data/']
SECDIST_PATH = '/etc/yandex/taxi-secdist/atlas.yaml'


def _load_secdist_yaml(path):
    _yaml = None
    try:
        _yaml = yaml.load(open(path, 'r'))
    except (TypeError, yaml.error.MarkedYAMLError):
        pass
    return _yaml


def create_users(connection):

    secdist_yaml = _load_secdist_yaml(SECDIST_PATH)
    user = None
    password = None

    if secdist_yaml is not None:
        atlas_secdist = secdist_yaml['mongodb']['connections']['atlas']
        user = atlas_secdist.get('user')
        password = atlas_secdist.get('password')

    print('Creating user {}, with password {} at atlas'.format(user, password))
    if user is not None and password is not None:
        connection.atlas.add_user(user, password,
                                  roles=[{'role': 'readWrite', 'db': 'atlas'}],
                                  mechanisms=['SCRAM-SHA-1'])


def json_loads(content, *args, **kwargs):
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
    return json_util.json.loads(content, *args, **kwargs)


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


def upload_data(connection, data):
    # Uploads the data to mongo
    # The data is the dict from collection_name to iterable of docs
    db = connection.atlas
    for collection_name, docs in data.items():
        try:
            collection = db[collection_name]
            if docs:
                collection.insert_many(docs)
        except pymongo.errors.BulkWriteError:
            pass


def get_pymongo_connection():
    return pymongo.MongoClient(
        host='mongodb://mongo.atlas.taxi.yandex:27017/',
        socketTimeoutMS=60000,
        connectTimeoutMS=10000,
        waitQueueTimeoutMS=10000,
    )


def main():
    connection = get_pymongo_connection()
    create_users(connection)
    data_to_load = get_data_from_json_files(
        PATHS_TO_INPUT_JSONS,
        JSONS_SEARCH_RE,
    )
    upload_data(connection, data_to_load)


if __name__ == '__main__':
    main()
