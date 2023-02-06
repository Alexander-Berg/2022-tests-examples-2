import pytest


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_rules_list(taxi_classifier):
    # classifier_id_1
    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/classification-rules/list',
        params={'classifier_id': 'classifier_id_1'},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'classifier': {
            'classifier_id': 'classifier_id_1',
            'is_allowing': True,
        },
        'tariffs': [
            {
                'classification_rules': [
                    {
                        'brand': 'Pagani',
                        'ended_at': '2020-12-27T00:00:00+00:00',
                        'is_allowing': True,
                        'model': 'Zonda',
                        'price_from': 3000000,
                        'price_to': 6000000,
                        'rule_id': '4',
                        'started_at': '2019-12-27T00:00:00+00:00',
                        'vehicle_before': '2018-01-01T00:00:00+00:00',
                        'year_from': 0,
                        'year_to': 3,
                    },
                    {
                        'brand': 'Audi',
                        'is_allowing': True,
                        'model': 'A8',
                        'rule_id': '3',
                    },
                    {
                        'brand': 'Audi',
                        'is_allowing': True,
                        'model': 'TT',
                        'rule_id': '2',
                    },
                    {
                        'brand': 'BMW',
                        'is_allowing': True,
                        'model': 'X6',
                        'rule_id': '1',
                    },
                ],
                'tariff': {'is_allowing': True, 'tariff_id': 'tariff_id_1'},
            },
        ],
    }

    # classifier_id_2
    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/classification-rules/list',
        params={'classifier_id': 'classifier_id_2'},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'classifier': {
            'classifier_id': 'classifier_id_2',
            'is_allowing': False,
        },
        'tariffs': [
            {
                'classification_rules': [
                    {'rule_id': '5', 'is_allowing': True},
                ],
                'tariff': {'is_allowing': False, 'tariff_id': 'tariff_id_2'},
            },
            {
                'classification_rules': [
                    {'rule_id': '6', 'is_allowing': True, 'brand': 'Audi'},
                ],
                'tariff': {'is_allowing': True, 'tariff_id': 'tariff_id_2_1'},
            },
        ],
    }


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_classifier_not_found(taxi_classifier):
    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/classification-rules/list',
        params={'classifier_id': 'unknown_classifier'},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'classifier_not_found',
        'message': 'Classifier unknown_classifier not found',
    }
