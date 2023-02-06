import pytest


@pytest.fixture(autouse=True)
def cars_catalog(mockserver):
    @mockserver.json_handler('/cars-catalog/api/v1/cars/get_prices')
    def mock_cars_catalog_prices(request):
        return {
            'items': [
                {
                    'revision': 2,
                    'data': {
                        'normalized_mark_code': 'TOYOTA',
                        'normalized_model_code': 'CAMRY',
                        'car_year': 2013,
                        'car_age': 6,
                        'car_price': 1000000.123,
                    },
                },
                {
                    'revision': 3,
                    'data': {
                        'normalized_mark_code': 'TOYOTA',
                        'normalized_model_code': 'COROLLA',
                        'car_year': 2012,
                        'car_age': 2012,
                        'car_price': 400000.0,
                    },
                },
                {
                    'revision': 4,
                    'data': {
                        'normalized_mark_code': 'SKODA',
                        'normalized_model_code': 'RAPID',
                        'car_year': 2015,
                        'car_age': 2015,
                        'car_price': 624647.0,
                    },
                },
                {
                    'revision': 5,
                    'data': {
                        'normalized_mark_code': 'RENAULT',
                        'normalized_model_code': 'LOGAN',
                        'car_year': 2012,
                        'car_age': 2012,
                        'car_price': 300000.0,
                    },
                },
                {
                    'revision': 6,
                    'data': {
                        'normalized_mark_code': 'NISSAN',
                        'normalized_model_code': 'PRESAGE',
                        'car_year': 2004,
                        'car_age': 2004,
                        'car_price': 336333.0,
                    },
                },
                {
                    'revision': 7,
                    'data': {
                        'normalized_mark_code': 'RENAULT',
                        'normalized_model_code': 'LOGAN',
                        'car_year': 2016,
                        'car_age': 2016,
                        'car_price': 350000.0,
                    },
                },
                {
                    'revision': 8,
                    'data': {
                        'normalized_mark_code': 'SKODA',
                        'normalized_model_code': 'OCTAVIA',
                        'car_year': 2017,
                        'car_age': 2017,
                        'car_price': 1438000.0,
                    },
                },
                {
                    'revision': 9,
                    'data': {
                        'normalized_mark_code': 'SKODA',
                        'normalized_model_code': 'RAPID',
                        'car_year': 2017,
                        'car_age': 2017,
                        'car_price': 1438000.0,
                    },
                },
            ],
        }

    @mockserver.json_handler('/cars-catalog/api/v1/cars/get_brand_models')
    def mock_cars_catalog_brand_models(request):
        return {
            'items': [
                {
                    'revision': 2,
                    'data': {
                        'raw_brand': 'Toyota',
                        'raw_model': 'Camry',
                        'normalized_mark_code': 'TOYOTA',
                        'normalized_model_code': 'CAMRY',
                    },
                },
                {
                    'revision': 3,
                    'data': {
                        'raw_brand': 'Tayota',
                        'raw_model': 'Carola',
                        'normalized_mark_code': 'TOYOTA',
                        'normalized_model_code': 'COROLLA',
                        'corrected_model': 'Toyota Corolla',
                    },
                },
                {
                    'revision': 4,
                    'data': {
                        'raw_brand': 'Skoda',
                        'raw_model': 'Rapid',
                        'normalized_mark_code': 'SKODA',
                        'normalized_model_code': 'RAPID',
                        'corrected_model': 'Skoda Rapid',
                    },
                },
                {
                    'revision': 5,
                    'data': {
                        'raw_brand': 'Renault',
                        'raw_model': 'Logan',
                        'normalized_mark_code': 'RENAULT',
                        'normalized_model_code': 'LOGAN',
                        'corrected_model': 'Renault Logan',
                    },
                },
                {
                    'revision': 6,
                    'data': {
                        'raw_brand': 'Nissan',
                        'raw_model': 'Presage',
                        'normalized_mark_code': 'NISSAN',
                        'normalized_model_code': 'PRESAGE',
                        'corrected_model': 'Nissan Presage',
                    },
                },
                {
                    'revision': 7,
                    'data': {
                        'raw_brand': 'Skoda',
                        'raw_model': 'Octavia',
                        'normalized_mark_code': 'SKODA',
                        'normalized_model_code': 'OCTAVIA',
                        'corrected_model': 'Skoda Octavia',
                    },
                },
            ],
        }

    @mockserver.json_handler('/cars-catalog/api/v1/cars/get_colors')
    def mock_cars_catalog_colors(request):
        return {
            'items': [
                {
                    'revision': 2,
                    'data': {
                        'raw_color': 'Бронза',
                        'normalized_color': 'бронза',
                        'color_code': 'AAAEA0',
                    },
                },
                {
                    'revision': 3,
                    'data': {
                        'raw_color': 'серебристый',
                        'normalized_color': 'серебристый',
                        'color_code': 'ABCDEF',
                    },
                },
                {
                    'revision': 4,
                    'data': {
                        'raw_color': 'желтый',
                        'normalized_color': 'желтый',
                        'color_code': 'FFD600',
                    },
                },
                {
                    'revision': 5,
                    'data': {
                        'raw_color': 'белый',
                        'normalized_color': 'белый',
                        'color_code': 'ABCDE0',
                    },
                },
                {
                    'revision': 6,
                    'data': {
                        'raw_color': 'фиолетовый',
                        'normalized_color': 'фиолетовый',
                        'color_code': '4A2197',
                    },
                },
            ],
        }
