# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

import pytest

from classifier_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
def classifier_request(mockserver):
    @mockserver.json_handler('/classifier/v1/classifier-tariffs/updates')
    def _mock_tariffs_updates(request):
        response = {'tariffs': [], 'limit': 100}
        return response

    @mockserver.json_handler('/classifier/v1/classification-rules/updates')
    def _mock_classification_rules_updates(request):
        response = {'classification_rules': [], 'limit': 100}
        return response


@pytest.fixture(autouse=True)
def cars_catalog_request(mockserver):
    @mockserver.json_handler('/cars-catalog/api/v1/cars/get_brand_models')
    def _mock_brand_models(request):
        assert request.method == 'GET'
        data = {
            'items': [
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'BMW',
                        'raw_model': 'X2',
                        'normalized_mark_code': 'BMW',
                        'normalized_model_code': 'X2',
                        'corrected_model': 'BMW X2',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'BMW',
                        'raw_model': 'X5',
                        'normalized_mark_code': 'BMW',
                        'normalized_model_code': 'X5',
                        'corrected_model': 'BMW X5',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'Audi',
                        'raw_model': 'A5',
                        'normalized_mark_code': 'AUDI',
                        'normalized_model_code': 'A5',
                        'corrected_model': 'Audi A5',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'Газель',
                        'raw_model': 'Next',
                        'normalized_mark_code': 'Газель',
                        'normalized_model_code': 'Next',
                        'corrected_model': 'Газель Next',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'Kia',
                        'raw_model': 'Rio',
                        'normalized_mark_code': 'Kia',
                        'normalized_model_code': 'Rio',
                        'corrected_model': 'Kia Rio',
                    },
                },
            ],
        }
        return mockserver.make_response(response=json.dumps(data))

    @mockserver.json_handler(
        '/cars-catalog/cars-catalog/v1/autocomplete-models',
    )
    def _mock_autocomplete_models(request):
        request_brand = request.query['brand']
        if request_brand == 'BMW':
            return {'brand': 'BMW', 'models': ['X2', 'X3', 'X6', 'X7']}
        if request_brand == 'Audi':
            return {
                'brand': 'Audi',
                'models': ['A7', 'TT', 'A6', 'A6 allroad'],
            }
        if request_brand == 'LADA (ВАЗ)':
            return {
                'brand': 'LADA (ВАЗ)',
                'models': ['Калина', 'Кококо', 'Гранта'],
            }
        if request_brand == 'ГАЗ':
            return {
                'brand': 'ГАЗ',
                'models': ['Ннива', 'ннн', 'НИВА', 'Грузовой', 'гг'],
            }
        print('Unexpected brand in autocomplete models: ', request_brand)
        return {'brand': request_brand, 'models': []}

    @mockserver.json_handler(
        '/cars-catalog/cars-catalog/v1/autocomplete-brands',
    )
    def _mock_autocomplete_brands(request):
        return {'brands': ['BMW', 'Audi', 'LADA (ВАЗ)', 'ГАЗ']}

    @mockserver.json_handler('/cars-catalog/api/v1/cars/get_prices')
    def _mock_prices(request):
        assert request.method == 'GET'
        data = {
            'items': [
                {
                    'revision': 0,
                    'data': {
                        'normalized_mark_code': 'BMW',
                        'normalized_model_code': 'X2',
                        'car_year': 2018,
                        'car_age': 1,
                        'car_price': 4624647,
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'normalized_mark_code': 'BMW',
                        'normalized_model_code': 'X5',
                        'car_year': 2018,
                        'car_age': 1,
                        'car_price': 4624647,
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'normalized_mark_code': 'AUDI',
                        'normalized_model_code': 'A5',
                        'car_year': 2018,
                        'car_age': 1,
                        'car_price': 4624647,
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'normalized_mark_code': 'Газель',
                        'normalized_model_code': 'Next',
                        'car_year': 2015,
                        'car_age': 5,
                        'car_price': 463647,
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'normalized_mark_code': 'Kia',
                        'normalized_model_code': 'Rio',
                        'car_year': 2017,
                        'car_age': 3,
                        'car_price': 663647,
                    },
                },
            ],
        }
        return mockserver.make_response(response=json.dumps(data))
