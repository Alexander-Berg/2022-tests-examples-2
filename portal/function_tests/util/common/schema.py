# -*- coding: utf-8 -*-
import json
import logging
import os
import re

import allure
import pytest
from jsonschema import Draft4Validator, RefResolver
import yatest

logger = logging.getLogger(__name__)


def get_schema_validator(schema_path):
    schema_path = yatest.common.runtime.work_path(os.path.join('schema', schema_path))
    schema = json.load(open(schema_path))
    path = os.path.realpath(schema_path)
    resolver = RefResolver(base_uri='file://' + path, referrer=schema)
    return Draft4Validator(schema, resolver=resolver)


def get_app_version_name(app_version):
    int_app_version = int(app_version)
    major = int_app_version // 1000000
    minor = (int_app_version % 1000000) / 10000
    fix = (int_app_version % 10000) / 100

    return '{}.{}{}'.format(major, minor, fix)


# app_platform это директории в function_tests/schema/android || ios. Пример 3.2.1
def parse_app_platform_name(app_platform):
    app_platform = re.match(r'^(?P<major>[0-9]+)\.(?P<minor>[0-9]+)(\.(?P<fix>[0-9]+))?$', app_platform)

    if not app_platform:
        return None

    major = app_platform.group('major')
    minor = app_platform.group('minor')
    fix = app_platform.group('fix')

    if not fix:
        fix = '0'

    if len(minor) == 1:
        minor = minor+'0'

    return (int(major), int(minor), int(fix))


# app_version версия типа 3020100
def parse_app_version_name(app_version):
    int_app_version = int(app_version)
    major = int_app_version // 1000000
    minor = (int_app_version % 1000000) // 1000
    fix = int_app_version % 1000
    return (major, minor, fix)


def get_api_search_schema_version(app_platform, app_version):
    if app_platform == 'iphone':
        app_platform = 'ios'
    versions = os.listdir('schema/{}/'.format(app_platform))
    app_versions = []
    for v in versions:
        if not parse_app_platform_name(v):
            continue

        if (parse_app_platform_name(v) <= parse_app_version_name(app_version)):
            app_versions.append(v)

    return max(app_versions)


def get_api_search_2_validator(app_platform, app_version, block):
    if app_platform == 'iphone':
        app_platform = 'ios'

    if block == 'collections':
        if (app_platform == 'android' and app_version >= 6010001) \
                or (app_platform == 'ios' and app_version >= 3000000):
            block = 'gallery'
        else:
            block = 'afisha'

    if block in ['edadeal', 'stream']:
        block = 'gallery'

    api_schema_version = get_api_search_schema_version(app_platform, app_version)
    return get_schema_validator('schema/{}/{}/api/search/2/{}/{}-block.json'.format(app_platform,
                                                                                    api_schema_version,
                                                                                    block, block))


def get_api_search_2_validator_top_level(app_platform, app_version, block):
    if app_platform == 'iphone':
        app_platform = 'ios'

    api_schema_version = get_app_version_name(app_version)
    return get_schema_validator('schema/{}/{}/api/search/2/{}.json'.format(app_platform, api_schema_version, block))


def _format_error(error):
    return '[%s]' % ']['.join(repr(index) for index in error.path) + ': \n' + \
           error.message.decode('unicode_escape')  # .encode('raw_unicode_escape').decode('utf-8')


def _format_error_and_filter_subschemas(error):
    items = []

    # Порядковые номера подсхем для каждого из типов блоков, которые нужно опустить в выводе отладочного сообщения.
    block_subschema_indices = set()

    for suberror in error.context:
        path = list(suberror.absolute_schema_path)
        # По абсолютному пути ошибки схемы определеяем _под_схему блока, который пытались сматчить с содержимым.
        if path[:4] == ['properties', 'block', 'items', 'anyOf'] and path[-1] == 'enum':
            block_subschema_indices.add(path[4])

    for suberror in sorted(error.context, key=lambda e: e.absolute_schema_path):
        path = list(suberror.absolute_schema_path)
        if path[4] not in block_subschema_indices:
            items.append("{}: {}".format(list(suberror.absolute_path), suberror.message))

    return "\n".join(items)


@allure.step('Validate schema')
def validate_schema(data, validator, formatter=_format_error):
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

    if len(errors) > 0:
        error_info = '\n\n'.join([formatter(error) for error in errors])
        allure.attach('Validation errors', error_info)
        logger.error('Validation errors:\n' + error_info)
        pytest.fail('Found {} json-schema validation errors'.format(len(errors)))


def validate_schema_by_service(data, service):
    if data is None:
        msg = 'Empty data'
        pytest.fail(msg)
    validator = get_schema_validator('schema/{service}/{service}-response.json'.format(service=service))
    validate_schema(data, validator)


def validate_schema_by_block(data, block_name, content='touch'):
    if data is None:
        msg = 'Empty data'
        pytest.fail(msg)
    path = 'schema/cleanvars/{block_name}/{content}/{block_name}.json'.format(
        block_name=block_name,
        content=content)
    validator = get_schema_validator(path)
    validate_schema(data, validator)
