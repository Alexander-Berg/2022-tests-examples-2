import datetime
import glob
import os

import pytest
import pytz

EPOCH = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=pytz.UTC)


class LocalizationsReplicaMock:
    def __init__(self):
        self.last_update_map = {}
        self.keyset_json_map = {}
        self.data_map = {}

    def is_up_to_data(self, keyset_name, last_update_str):
        if keyset_name in self.last_update_map:
            last_update = datetime.datetime.strptime(
                last_update_str, '%Y-%m-%dT%H:%M:%S.%f%z',
            )
            return self.last_update_map[keyset_name] <= last_update
        return False

    def get_keyset(self, keyset_name):
        if keyset_name in self.keyset_json_map:
            return self.keyset_json_map[keyset_name]
        return None

    def convert_data_to_json(self):
        for keyset_name, keys in self.data_map.items():
            keys_json = []
            for key_name, locales in keys.items():
                values_json = []
                for locale, forms in locales.items():
                    for form, value in forms.items():
                        values_json.append(
                            {
                                'value': value,
                                'conditions': {
                                    'form': form,
                                    'locale': {'language': locale},
                                },
                            },
                        )

                keys_json.append({'key_id': key_name, 'values': values_json})

            last_update = self.last_update_map.get(keyset_name, EPOCH)
            self.keyset_json_map[keyset_name] = {
                'last_update': last_update.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
                'keyset_name': keyset_name,
                'keys': keys_json,
            }

    def parse_marker(self, marker):
        last_update = datetime.datetime.utcnow()
        last_update = last_update.replace(tzinfo=pytz.UTC)
        for keyset_name, keys in marker.kwargs.items():
            if keyset_name not in self.data_map:
                self.data_map[keyset_name] = {}
            for key_name, values in keys.items():
                if key_name not in self.data_map[keyset_name]:
                    self.data_map[keyset_name][key_name] = {}
                for locale, form_text in values.items():
                    if locale not in self.data_map[keyset_name][key_name]:
                        self.data_map[keyset_name][key_name][locale] = {}
                    if isinstance(form_text, list):
                        forms_and_texts = list(enumerate(form_text, start=1))
                    else:
                        forms_and_texts = [(1, form_text)]
                    for form, text in forms_and_texts:
                        self.data_map[keyset_name][key_name][locale][
                            form
                        ] = text
            self.last_update_map[keyset_name] = last_update

    def parse_db_style_json(self, json, keyset_name):
        last_update = datetime.datetime.utcnow()
        last_update = last_update.replace(tzinfo=pytz.UTC)
        self.data_map.setdefault(keyset_name, {})
        for key in json:
            key_name = key['_id']
            self.data_map[keyset_name].setdefault(key_name, {})
            for value in key['values']:
                locale = 'ru'
                if 'locale' in value['conditions']:
                    locale = value['conditions']['locale']['language']
                form = 1
                if 'form' in value['conditions']:
                    form = value['conditions']['form']

                self.data_map[keyset_name][key_name].setdefault(locale, {})
                self.data_map[keyset_name][key_name][locale][form] = value[
                    'value'
                ]

        self.last_update_map[keyset_name] = last_update


@pytest.fixture
def localizations(request, search_path, load_json):
    localizations = LocalizationsReplicaMock()

    for path in reversed(list(search_path('localizations', True))):
        for file_path in glob.glob(os.path.join(path, '*.json')):
            if os.path.isfile(file_path):
                file_name = os.path.basename(file_path)
                keyset_name, _ = os.path.splitext(file_name)
                localizations.parse_db_style_json(
                    load_json(file_path), keyset_name,
                )

    if request.node.get_marker('translations'):
        for marker in request.node.get_marker('translations'):
            localizations.parse_marker(marker)

    localizations.convert_data_to_json()

    return localizations
