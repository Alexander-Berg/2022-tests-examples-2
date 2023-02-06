import pytest


@pytest.mark.now('2020-08-12T21:56:01+0000')
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
                'price': 4000000,
                'car_number': 'EEEEEEE',
                'required_classes': ['vip', 'econom', 'comfort'],
            },
            {'classes': ['vip']},
        ),
        (
            {
                'brand_model': 'Pagani Zonda',
                'age': 1,
                'price': 4000000,
                'car_number': 'EEEEEEE',
                'required_classes': ['vip', 'econom', 'comfort'],
            },
            {'classes': []},
        ),
        (
            {
                'brand_model': 'Pagani Zonda',
                'age': 10,
                'price': 4000000,
                'car_number': 'EEEEEEE',
                'required_classes': ['vip', 'econom', 'comfort'],
            },
            {'classes': ['vip']},
        ),
        (
            {
                'brand_model': 'Pagani Zonda',
                'age': 11,
                'price': 4000000,
                'car_number': 'EEEEEEE',
                'required_classes': ['vip', 'econom', 'comfort'],
            },
            {'classes': []},
        ),
        (
            {
                'brand_model': 'Unknown model',
                'age': 50,
                'price': 1500,
                'car_number': 'EEEEEEE',
                'required_classes': ['vip', 'econom', 'comfort', 'express'],
            },
            {'classes': ['econom', 'express']},
        ),
        (
            {
                'brand_model': 'Mercedes McLaren SLR',
                'age': 50,
                'price': 300000,
                'car_number': 'EEEEEEE',
                'required_classes': ['vip', 'comfort', 'express'],
            },
            {'classes': ['comfort', 'express']},
        ),
        (
            {
                'brand_model': 'Unknown model',
                'age': 50,
                'price': 500000,
                'car_number': 'EEEEEEE',
                'required_classes': ['vip', 'econom', 'comfort', 'express'],
            },
            {'classes': ['express']},
        ),
        (
            {
                'brand_model': 'Unknown model',
                'age': 0,
                'price': 500000,
                'car_number': 'EEEEEEE',
                'required_classes': ['uberselect'],
            },
            {'classes': ['uberselect']},
        ),
        (
            {
                'brand_model': 'Unknown model',
                'age': 2,
                'price': 500000,
                'car_number': 'EEEEEEE',
                'required_classes': ['uberselect'],
            },
            {'classes': []},
        ),
        (
            {
                'brand_model': 'Audi A6',
                'age': 2,
                'price': 500000,
                'car_number': '111AA750',
                'required_classes': ['promo'],
            },
            {'classes': ['promo']},
        ),
        (
            {
                'brand_model': 'Audi A6',
                'age': 2,
                'price': 500000,
                'car_number': 'EEEEEEE',
                'required_classes': ['promo'],
            },
            {'classes': []},
        ),
        (
            {
                'brand_model': 'Audi A6',
                'age': 0,
                'price': 500000,
                'car_number': 'EEEEEEE',
                'required_classes': ['uberselect'],
            },
            {'classes': ['uberselect']},
        ),
    ],
)
async def test_classify_car(
        taxi_classifier, query_params, request_body, expected_response,
):
    response = await taxi_classifier.post(
        '/v1/vehicle-classification', json=request_body, params=query_params,
    )

    assert response.status_code == 200, response.text

    assert sorted(response.json()['classes']) == sorted(
        expected_response['classes'],
    )


@pytest.mark.now('2020-01-12T00:00:00+0000')  # January
@pytest.mark.pgsql(
    'classifier', files=['tariffs.sql', 'classifiers.sql', 'rules.sql'],
)
@pytest.mark.config(CLASSIFIER_CAR_MANUFACTURE_MONTH=1)  # February
async def test_current_month_less_than_manufacture_month(taxi_classifier):
    response = await taxi_classifier.post(
        '/v1/vehicle-classification',
        json={
            'brand_model': 'Pagani Zonda',
            'age': 1,  # Manufacture year is 2018, match the rule
            'price': 4000000,
            'car_number': 'EEEEEEE',
            'required_classes': ['vip'],
        },
        params={'classifier_id': 'classifier_id_1'},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'classes': ['vip']}


async def test_code_404(taxi_classifier):
    # case 1
    response = await taxi_classifier.post(
        '/v1/vehicle-classification',
        json={
            'brand_model': 'Audi TT',
            'age': 12,
            'price': 1000000,
            'car_number': 'EEEEEEE',
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
        '/v1/vehicle-classification',
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
        '/v1/vehicle-classification',
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
