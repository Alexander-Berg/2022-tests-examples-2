#!/usr/bin/env python
# -*- coding: utf-8 -*
from __future__ import print_function
from __future__ import unicode_literals

import bootstrap_schemas


def read_defaults(schemas):
    default_config_values = {}
    for (
            config_name,
            config_schema,
    ) in schemas.iteritems():  # pylint: disable=E1101
        if config_name in bootstrap_schemas.IGNORED:
            print(
                'Ignore `{}` for reason `{}`'.format(
                    config_name, bootstrap_schemas.IGNORED[config_name],
                ),
            )
            continue
        default_config_values[config_name] = {'v': config_schema['default']}
    print('Successfully read default config values')
    return default_config_values


def read_meta(schemas):
    meta = dict()
    for name, schema in schemas.items():
        if 'group' not in schema:
            print(name, 'not has group')
            continue
        meta[schema['group']] = {
            'updated': '1970-01-01T00:00:00+00:00',
            'hash': 'master',
        }
    return meta


def update_from_current(docs, current_docs):
    for item in current_docs:
        if item['_id'] not in docs:
            print('Document `{}` not found in stored'.format(item['_id']))
        docs[item['_id']] = item
    print('Successfully fill current values')


def transform_to_docs(docs):
    result = []
    for key, value in docs.items():
        item = {'_id': key}
        item.update(value)
        result.append(item)
    print('Successfully transform values to docs')
    return result


def process_config_values(data):
    print('run process_config_values')
    config_values = read_defaults(bootstrap_schemas.SCHEMAS)
    update_from_current(config_values, data)
    docs = transform_to_docs(config_values)
    return docs


def process_meta(data):
    print('run process_meta')
    meta = read_meta(bootstrap_schemas.SCHEMAS)
    update_from_current(meta, data)
    docs = transform_to_docs(meta)
    return docs


def process_schemas(data):
    print('run process_schemas')
    schemas = {
        key: fields
        for (
            key,
            fields,
        ) in bootstrap_schemas.SCHEMAS.iteritems()  # pylint: disable=E1101
        if key not in bootstrap_schemas.IGNORED
    }
    update_from_current(schemas, data)
    docs = transform_to_docs(schemas)
    return docs


def process_schemas_definitions(data):
    print('run process_schemas_definitions')
    definitions = {
        key: fields
        for (
            key,
            fields,
        ) in bootstrap_schemas.DEFINITIONS.iteritems()  # pylint: disable=E1101
        if key not in bootstrap_schemas.IGNORED_DEFINITIONS
    }
    update_from_current(definitions, data)
    docs = transform_to_docs(definitions)
    return docs
