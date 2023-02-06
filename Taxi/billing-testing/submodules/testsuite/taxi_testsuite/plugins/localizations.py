import datetime

import dateutil.parser
import pytest
import pytz

from testsuite._internal import fixture_types

EPOCH = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=pytz.UTC)


class LocalizationsReplicaMock:
    def __init__(self):
        self.last_update_map = {}
        self.keyset_json_map = {}
        self.data_map = {}

    def is_up_to_data(self, keyset_name, last_update_str):
        if keyset_name in self.last_update_map:
            last_update = dateutil.parser.isoparse(last_update_str)
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


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'translations: per-test translations config',
    )


@pytest.fixture
def localizations(
        request,
        search_path: fixture_types.SearchPathFixture,
        load_json: fixture_types.LoadJsonFixture,
):
    localizations = LocalizationsReplicaMock()

    for path in reversed(list(search_path('localizations', directory=True))):
        for file_path in path.glob('*.json'):
            if file_path.is_file():
                localizations.parse_db_style_json(
                    load_json(file_path), file_path.stem,
                )

    for marker in request.node.iter_markers('translations'):
        localizations.parse_marker(marker)

    localizations.convert_data_to_json()
    return localizations
