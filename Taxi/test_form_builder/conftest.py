# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
from typing import Dict
from typing import List

import pytest

import form_builder.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'form_builder.generated.service.pytest_plugins',
    'form_builder.generated.service.geobase.pytest_plugin',
]


@pytest.fixture
def mockserver_personal(mockserver):
    item_id = 'A'
    phone_item_val = 'A'

    @mockserver.handler('/personal/v1/identifications/bulk_store')
    def _identifications_bulk_store(request):
        result = []
        nonlocal item_id
        for item in request.json['items']:
            result.append({'id': item_id, 'value': item['value']})
            item_id = chr(ord(item_id) + 1)
        return mockserver.make_response(json={'items': result})

    @mockserver.handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        result = []
        nonlocal phone_item_val
        for item in request.json['items']:
            result.append({'id': item['id'], 'value': phone_item_val})
            phone_item_val = chr(ord(phone_item_val) + 1)
        return mockserver.make_response(json={'items': result})


class _PersonalCache:
    def __init__(self, value_key: str = 'value'):
        self._value = 'A'
        self._identifier = 1
        self._cache: List[Dict] = []
        self._value_key = value_key

    def retrieve(self, item_id):
        value = self._find_by('id', item_id)
        if value:
            return value
        self._value = chr(ord(self._value) + 1)
        return self.store_with_id(self._value, item_id)

    def store(self, value):
        _value = self._find_by(self._value_key, value)
        if _value:
            return _value
        self._identifier += 1
        return self.store_with_id(value, self._personal_id)

    def store_with_id(self, value, id_):
        item = {'id': id_, self._value_key: value}
        self._cache.append(item)
        return item

    def _find_by(self, field, value):
        for item in self._cache:
            if item[field] == value:
                return item
        return None

    @property
    def _personal_id(self):
        return f'personal_id_{self._identifier}'


def _make_cached_personal_mock_for_type(mockserver, type_: str):
    _cache = _PersonalCache()

    @mockserver.handler(f'/personal/v1/{type_}/bulk_store')
    def _identifications_bulk_store(request):
        result = []
        for item in request.json['items']:
            result.append(_cache.store(item['value']))
        return mockserver.make_response(json={'items': result})

    @mockserver.handler(f'/personal/v1/{type_}/bulk_retrieve')
    def _identifications_bulk_retrieve(request):
        result = []
        for item in request.json['items']:
            result.append(_cache.retrieve(item['id']))
        return mockserver.make_response(json={'items': result})

    @mockserver.handler(f'/personal/v1/{type_}/store')
    def _phones_single_store(request):
        return mockserver.make_response(
            json=_cache.store(request.json['value']),
        )

    @mockserver.handler(f'/personal/v1/{type_}/retrieve')
    def _phones_single_retrieve(request):
        return mockserver.make_response(
            json=_cache.retrieve(request.json['id']),
        )

    return _cache


@pytest.fixture
def cached_personal_mock(mockserver):
    return {
        'phones': _make_cached_personal_mock_for_type(mockserver, 'phones'),
        'identifications': _make_cached_personal_mock_for_type(
            mockserver, 'identifications',
        ),
        'driver_licenses': _make_cached_personal_mock_for_type(
            mockserver, 'driver_licenses',
        ),
    }


@pytest.fixture
def territories_mock(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    def _handler(request):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'lang': 'ru',
                    'phone_code': '7',
                    'national_access_code': '8',
                    'phone_min_length': 11,
                    'phone_max_length': 12,
                },
                {
                    '_id': 'blr',
                    'lang': 'ru',
                    'phone_code': '375',
                    'national_access_code': '80',
                    'phone_min_length': 12,
                    'phone_max_length': 12,
                },
            ],
        }


@pytest.fixture(name='mock_cars_catalog')
def _mock_cars_catalog(relative_load_json, mockserver, mock_cars_catalog):
    all_brands = relative_load_json('all_brands.json')
    bmw_models = relative_load_json('bmw_models.json')

    @mock_cars_catalog('/cars-catalog/v1/autocomplete-brands')
    def _brands_handler(request):
        query = request.query['text_query']
        return {
            'brands': [x for x in all_brands if x.lower().startswith(query)],
        }

    @mock_cars_catalog('/cars-catalog/v1/autocomplete-models')
    def _models_handler(request):
        model_query = request.query['text_query']
        brand = request.query['brand']
        if brand not in all_brands:
            return mockserver.make_response(
                json={
                    'code': 404,
                    'message': f'brand `{brand}` was not found',
                },
                status=404,
            )
        return {
            'brand': brand,
            'models': [
                x for x in bmw_models if x.lower().startswith(model_query)
            ],
        }
