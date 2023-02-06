import pytest


@pytest.mark.now('2020-08-12T00:00:00+0000')
@pytest.mark.pgsql(
    'classifier',
    files=[
        'tariffs.sql',
        'classifiers.sql',
        'rules.sql',
        'cars_first_order_date.sql',
    ],
)
@pytest.mark.parametrize(
    'query_params',
    [{'classifier_id': 'classifier_id_1'}, {'zone_id': 'moscow'}],
)
@pytest.mark.parametrize(
    ['request_body', 'expected_response'],
    [
        (
            {
                'brand_model': 'Pagani Zonda',
                'age': 2,
                'car_number': '111AA750',
                'price': 3000,
                'required_classes': ['vip', 'econom', 'comfort'],
            },
            {
                'tariffs_reject_reasons': [
                    {
                        'reasons': ['TARIFF_NOT_ALLOWING'],
                        'tariff_id': 'econom',
                    },
                    {
                        'reasons': [
                            'BRAND_MODEL',
                            'MANUFACTURE_YEAR',
                            'PRICE',
                            'VEHICLE_BEFORE',
                        ],
                        'tariff_id': 'vip',
                    },
                    {
                        'reasons': ['TARIFF_NOT_ALLOWING'],
                        'tariff_id': 'comfort',
                    },
                ],
            },
        ),
        (
            {
                'brand_model': 'Pagani Zonda',
                'age': 5,
                'car_number': 'EEEEEE',
                'price': 4000000,
                'required_classes': ['vip'],
            },
            {
                'tariffs_reject_reasons': [
                    {'reasons': ['MANUFACTURE_YEAR'], 'tariff_id': 'vip'},
                ],
            },
        ),
        (
            {
                'brand_model': 'Unknown model',
                'age': 50,
                'price': 1500,
                'car_number': 'EEEEEE',
                'required_classes': ['vip', 'econom', 'comfort', 'express'],
            },
            {
                'tariffs_reject_reasons': [
                    {'reasons': [], 'tariff_id': 'express'},
                    {'reasons': ['PRICE'], 'tariff_id': 'econom'},
                    {'reasons': ['TARIFF_NOT_ALLOWING'], 'tariff_id': 'vip'},
                    {
                        'reasons': ['TARIFF_NOT_ALLOWING'],
                        'tariff_id': 'comfort',
                    },
                ],
            },
        ),
        (
            {
                'brand_model': 'Mercedes McLaren SLR',
                'age': 5,
                'car_number': 'EEEEEE',
                'price': 700,
                'required_classes': ['vip', 'comfort', 'express'],
            },
            {
                'tariffs_reject_reasons': [
                    {'reasons': [], 'tariff_id': 'express'},
                    {'reasons': ['MANUFACTURE_YEAR'], 'tariff_id': 'vip'},
                    {
                        'reasons': [
                            'BRAND_MODEL',
                            'MANUFACTURE_YEAR',
                            'PRICE',
                        ],
                        'tariff_id': 'comfort',
                    },
                ],
            },
        ),
        (
            {
                'brand_model': 'Mercedes McLaren SLR',
                'age': 50,
                'price': 10000000,
                'car_number': 'EEEEEE',
                'required_classes': ['comfort'],
            },
            {
                'tariffs_reject_reasons': [
                    {'reasons': ['BRAND_MODEL'], 'tariff_id': 'comfort'},
                ],
            },
        ),
        (
            {
                'brand_model': 'Unknown model',
                'age': 50,
                'price': 500000,
                'car_number': 'EEEEEE',
                'required_classes': ['vip', 'econom', 'comfort', 'express'],
            },
            {
                'tariffs_reject_reasons': [
                    {'reasons': [], 'tariff_id': 'express'},
                    {
                        'reasons': ['TARIFF_NOT_ALLOWING'],
                        'tariff_id': 'econom',
                    },
                    {'reasons': ['TARIFF_NOT_ALLOWING'], 'tariff_id': 'vip'},
                    {
                        'reasons': ['TARIFF_NOT_ALLOWING'],
                        'tariff_id': 'comfort',
                    },
                ],
            },
        ),
        (
            {
                'brand_model': 'BMW X6',
                'age': 50,
                'car_number': 'EEEEEE',
                'price': 10150,
                'required_classes': ['uberselect'],
            },
            {
                'tariffs_reject_reasons': [
                    {'reasons': [], 'tariff_id': 'uberselect'},
                ],
            },
        ),
        (
            {
                'brand_model': 'BMW X6',
                'age': 50,
                'price': 2000000,
                'car_number': 'EEEEEE',
                'required_classes': ['uberselect'],
            },
            {
                'tariffs_reject_reasons': [
                    {'reasons': ['BRAND_MODEL'], 'tariff_id': 'uberselect'},
                ],
            },
        ),
    ],
)
async def test_classify_car(
        taxi_classifier, query_params, request_body, expected_response,
):
    response = await taxi_classifier.post(
        '/v1/vehicle-classification-reject-reason',
        json=request_body,
        params=query_params,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()
    assert _sort_reason(response_json) == expected_response


def _sort_reason(response_json):
    for entry in response_json['tariffs_reject_reasons']:
        entry['reasons'].sort()
    return response_json


async def test_code_404(taxi_classifier):
    # case 1
    response = await taxi_classifier.post(
        '/v1/vehicle-classification-reject-reason',
        json={
            'brand_model': 'Audi TT',
            'age': 12,
            'price': 1000000,
            'car_number': 'EEEEEE',
            'required_classes': ['vip'],
        },
        params={'classifier_id': 'unknown_classifier_id'},
    )

    assert response.status_code == 404, response.text

    assert response.json() == {
        'code': 'classifier_not_found',
        'message': 'Classifier unknown_classifier_id not found',
    }

    # case 2
    response = await taxi_classifier.post(
        '/v1/vehicle-classification-reject-reason',
        json={
            'brand_model': 'Audi TT',
            'age': 12,
            'price': 1000000,
            'car_number': 'EEEEEE',
            'required_classes': ['vip'],
        },
        params={'classifier_id': 'classifier_id_1', 'zone_id': 'moscow'},
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'invalid_parameters',
        'message': 'Exactly one parameter must be setted',
    }

    # case 3
    response = await taxi_classifier.post(
        '/v1/vehicle-classification-reject-reason',
        json={
            'brand_model': 'Audi TT',
            'age': 12,
            'price': 1000000,
            'car_number': 'EEEEEE',
            'required_classes': ['vip'],
        },
        params={'zone_id': 'unknown_zone_id'},
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'zone_not_found',
        'message': 'Zone unknown_zone_id not found',
    }
