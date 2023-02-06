#!/usr/bin/env python
# -*- coding: utf-8 -*
from __future__ import print_function
from __future__ import unicode_literals

import json
import os

import yaml


PATH_TO_SCHEMAS = '/taxi/schemas/configs/declarations'
PATH_TO_DEFINITIONS = '/taxi/schemas/configs/definitions'

# this configs newer updated from config_schemas
MESSAGE_BROKEN_KEY_TYPE = 'broken keys - use integer instead of string'
# problem to insert in d-i-t, but update on config_schemas works
MESSAGE_ILLEGAL_SYMB_IN_KEY = 'key must not contain \'.\''
MESSAGE_ILLEGAL_SYMB_IN_KEY_2 = 'key must not contain \'$\''
IGNORED = {
    'ADMIN_IMAGE_SIZE_HINT_TO_SCREEN_INFO': MESSAGE_BROKEN_KEY_TYPE,
    'APPLICATION_DETECTION_RULES_NEW': MESSAGE_ILLEGAL_SYMB_IN_KEY_2,
    'EDITABLE_REQUIREMENTS_BY_ZONE': MESSAGE_ILLEGAL_SYMB_IN_KEY,
    'DISPATCH_SETTINGS_FALLBACK_VALUE': MESSAGE_BROKEN_KEY_TYPE,
    'DRIVER_MONEY_ORDER_TEMPLATE': MESSAGE_ILLEGAL_SYMB_IN_KEY,
    'FORM_SUBMIT_TIMEOUT_SETTINGS': MESSAGE_ILLEGAL_SYMB_IN_KEY,
    'MAPPER_FOS_FORMS_FIELDS': MESSAGE_BROKEN_KEY_TYPE,
    'NEWDRIVER_REQUESTS_SUBJECT_MAPPER': MESSAGE_ILLEGAL_SYMB_IN_KEY,
    'USERSTATS_CLIENT_QOS': MESSAGE_ILLEGAL_SYMB_IN_KEY,
}
IGNORED_DEFINITIONS = dict()  # type: dict


def read_schemas():
    schemas_by_name = {}
    for root, _, files in os.walk(PATH_TO_SCHEMAS):
        for file in files:
            path = os.path.join(root, file)
            if not os.path.isfile(path) or not file.endswith('.yaml'):
                continue

            config_name = file.replace('.yaml', '')
            config_schema = {}
            with open(path) as f_descriptor:
                config_schema = yaml.load(f_descriptor, yaml.CSafeLoader)
                for key in {'schema', 'validators'}:
                    if key not in config_schema:
                        continue
                    config_schema[key] = json.dumps(config_schema[key])
                config_schema['group'] = decl_group_extractor(path)
                schemas_by_name[config_name] = config_schema
    print('Successfully read config schemas')
    return schemas_by_name


def read_definitions():
    store = {}
    for root, _, files in os.walk(PATH_TO_DEFINITIONS):
        for file in files:
            path = os.path.join(root, file)
            if not os.path.isfile(path) or not file.endswith('.yaml'):
                continue

            def_name = file.replace('.yaml', '')

            definition = {}
            with open(path) as f_descriptor:
                definition = yaml.load(f_descriptor, yaml.CSafeLoader)
                full_def_name = '%s/%s' % (def_group_extractor(path), def_name)
                raw_definition = json.dumps(definition)
                store['/' + full_def_name] = {'schema': raw_definition}
                store[full_def_name] = {'schema': raw_definition}
    print('Successfully read config schemas definitions')
    return store


def decl_group_extractor(path):
    return group_extractor(PATH_TO_SCHEMAS, path, True)


def def_group_extractor(path):
    return group_extractor(PATH_TO_DEFINITIONS, path, False)


def group_extractor(base, path, replace_slash):
    path_parts = path.split(base)
    if len(path_parts) != 2:
        raise ValueError('Path not contain path to base')

    group = os.path.dirname(path_parts[1]).strip('/')
    if replace_slash:
        group = group.replace('/', '.')
    return group


SCHEMAS = read_schemas()
DEFINITIONS = read_definitions()
