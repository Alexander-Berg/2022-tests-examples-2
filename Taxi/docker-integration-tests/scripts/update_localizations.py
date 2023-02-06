#!/usr/bin/env python
# -*- coding: utf-8 -*
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import copy
import json
import os
import typing

import requests
import yaml

DEFAULT_LANGUAGE = 'ru'
LOCALES_SUPPORTED = ['ru', 'en', 'hy', 'ka', 'kk', 'uk', 'az']
LOCALIZATION_PREFIX = 'localization_'
TANKER_HOST = 'https://tanker-api.yandex-team.ru'
TANKER_TIMEOUT = 15


TANKER_KEYSETS_FILE = os.path.join('scripts', 'tanker_keysets.json')

DB_DATA_DIR = os.path.join('volumes', 'bootstrap_db', 'db_data')
INTERNAL_SCHEMAS_DIR = os.path.join('schemas', 'mongo')
EXTERNAL_SCHEMAS_DIR = os.path.join('..', 'schemas', 'schemas', 'mongo')


# disabling https warnings
# pylint: disable=no-member
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.SecurityWarning,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--new_only', default=False, action='store_true')
    parser.add_argument('--update-schemas', default=False, action='store_true')

    return parser.parse_args(argv)


def load_tanker_keysets() -> typing.Dict:
    tanker_keysets = {}
    with open(TANKER_KEYSETS_FILE, 'r') as _file:
        tanker_keysets = json.load(_file)
    return tanker_keysets


def _format_plural_keys(translation_data):
    def _strip_literal_part(form_number):
        return form_number[4:]

    translations_language = {}
    for key, value in translation_data.items():
        if key.startswith('form'):
            translations_language[int(_strip_literal_part(key))] = value
    return translations_language


def fetch_keyset(
        keyset_id, project_id='taxi', unapproved=True, branch_id='master',
):
    locales_supported = LOCALES_SUPPORTED
    languages = ','.join(locales_supported)
    parameters = {
        'project-id': project_id,
        'keyset-id': keyset_id,
        'language': languages,
        'branch-id': branch_id,
    }
    if unapproved:
        parameters['status'] = 'unapproved'
    response = _request('keysets/tjson', parameters)
    return response


def load_translations(tanker_data, keyset, tanker_keysets):
    result = {}
    keyset_name = tanker_keysets[keyset]
    if isinstance(keyset_name, dict):
        keyset_name = keyset_name['keyset']
    for key, value in tanker_data['keysets'][keyset_name]['keys'].items():
        translations = {}
        for language, translation_data in value['translations'].items():
            if value['info']['is_plural']:
                translations[language] = _format_plural_keys(translation_data)
            else:
                translations[language] = translation_data['form']
        result[key] = translations
    return result


def _request(location, parameters):
    url = '{}/{}/'.format(TANKER_HOST, location)
    response = requests.get(
        url,
        params=parameters,
        verify=False,  # to avoid cert problem in requests package
        timeout=TANKER_TIMEOUT,
    )
    return response.json()


def get_translations(keyset, tanker_keysets):
    tanker_data = None
    keyset_info = tanker_keysets[keyset]
    if isinstance(keyset_info, dict):
        tanker_data = fetch_keyset(
            keyset_info['keyset'], **keyset_info['fetch_args'],
        )
    else:
        tanker_data = fetch_keyset(keyset_info)
    translations = load_translations(tanker_data, keyset, tanker_keysets)
    return translations


def get_localization_item(key, values, default_language):
    localization_item = {'_id': key, 'values': []}

    for language, value in sorted(values.items()):
        conditions = {}
        if language != default_language:
            conditions['locale'] = {'language': language}
        if isinstance(value, dict):
            for form, real_value in value.items():
                item_conditions = copy.deepcopy(conditions)
                item_conditions['form'] = form
                localization_item['values'].append(
                    {'conditions': item_conditions, 'value': real_value},
                )
        else:
            localization_item['values'].append(
                {'conditions': conditions, 'value': value},
            )
    return localization_item


def get_keyset(keyset, tanker_keysets):
    translations = get_translations(keyset, tanker_keysets)
    for key, values in sorted(translations.items()):
        localization_item = get_localization_item(
            key=key, values=values, default_language=DEFAULT_LANGUAGE,
        )
        yield localization_item


def get_json_data_filename(collection_name):
    return os.path.join(DB_DATA_DIR, 'db_' + collection_name + '.json')


def data_already_exists(collection_name):
    filename = get_json_data_filename(collection_name)

    return os.path.isfile(filename)


def get_data_to_load(args, tanker_keysets):
    result = {}
    for keyset in tanker_keysets:
        collection_name = LOCALIZATION_PREFIX + keyset
        if args.new_only and data_already_exists(collection_name):
            print(f'Skipping {keyset} because it already exists')
            continue

        print('Downloading', keyset)
        result[collection_name] = list(get_keyset(keyset, tanker_keysets))
    return result


def save_data(data):
    for collection_name, docs in data.items():
        json_data = json.dumps(
            docs,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            separators=(',', ': '),
        )
        filename = get_json_data_filename(collection_name)
        with open(filename, 'wb') as file_:
            file_.write(json_data.encode('utf-8'))
            file_.write(b'\n')


def save_schemas(tanker_keysets: typing.Dict) -> None:
    for key, value in tanker_keysets.items():
        filename = LOCALIZATION_PREFIX + key + '.yaml'
        filepath = os.path.join(INTERNAL_SCHEMAS_DIR, filename)
        if os.path.isfile(filepath):
            continue

        project_id = 'taxi'
        if isinstance(value, dict):
            fetch_args = value.get('fetch_args', None)
            if fetch_args:
                _project_id = fetch_args.get('project_id', None)
                if _project_id:
                    project_id = _project_id

        content = {
            'settings': {
                'collection': f'localization.{project_id}.{key}',
                'connection': 'localizations',
                'database': 'localizations',
            },
        }

        print(f'Save localizations schema: {filename}')
        save_yaml(filepath, content)

        filepath = os.path.join(EXTERNAL_SCHEMAS_DIR, filename)
        if os.path.isfile(filepath):
            continue

        save_yaml(filepath, content)


def save_yaml(filepath: str, content: typing.Dict) -> None:
    with open(filepath, 'w+') as file_:
        yaml.dump(
            content,
            file_,
            indent=4,
            sort_keys=True,
            default_flow_style=False,
        )


def load_localizations(args):
    tanker_keysets = load_tanker_keysets()
    data_to_load = get_data_to_load(args, tanker_keysets)
    print('Save localizations', data_to_load.keys())
    save_data(data_to_load)
    if args.update_schemas:
        save_schemas(tanker_keysets)


def main(argv=None):
    args = parse_args(argv)
    load_localizations(args)


if __name__ == '__main__':
    main()
