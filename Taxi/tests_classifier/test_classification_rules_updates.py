import pytest


@pytest.mark.now('2020-08-12T00:00:00+0000')
@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'rules.sql', 'tariffs.sql'],
)
async def test_all_rules(taxi_classifier):
    response = await taxi_classifier.post(
        '/v1/classification-rules/updates', json={'limit': 6},
    )

    assert response.status_code == 200
    assert response.json() == {
        'classification_rules': [
            {
                'classifier_id': 'classifier_id_1',
                'is_allowing': True,
                'tariff_id': 'tariff_id_1',
            },
            {
                'classifier_id': 'classifier_id_2',
                'is_allowing': True,
                'tariff_id': 'tariff_id_2',
            },
            {
                'classifier_id': 'classifier_id_3',
                'is_allowing': True,
                'tariff_id': 'tariff_id_3',
            },
            {
                'classifier_id': 'classifier_id_4',
                'is_allowing': True,
                'tariff_id': 'tariff_id_4',
            },
            {
                'classifier_id': 'classifier_id_5',
                'is_allowing': True,
                'tariff_id': 'tariff_id_5',
            },
            {
                'brand': 'McLaren',
                'model': 'F1',
                'classifier_id': 'classifier_id_6',
                'ended_at': '2015-01-01T00:00:00+00:00',
                'is_allowing': True,
                'price_from': 3000000,
                'price_to': 6000000,
                'started_at': '2015-01-01T00:00:00+00:00',
                'tariff_id': 'tariff_id_6',
                'vehicle_before': '2015-01-01T00:00:00+00:00',
                'year_from': 1998,
                'year_to': 2025,
            },
        ],
        'cursor': {'id': 6},
        'limit': 6,
    }


@pytest.mark.now('2020-08-12T00:00:00+0000')
@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'rules.sql', 'tariffs.sql'],
)
async def test_limit_one(taxi_classifier):
    response = await taxi_classifier.post(
        '/v1/classification-rules/updates', json={'limit': 1},
    )
    assert response.status_code == 200

    r_json = response.json()
    rules = r_json['classification_rules']
    expected_id = 1

    assert len(rules) == 1
    assert rules[0]['classifier_id'] == f'classifier_id_{expected_id}'

    cursor = r_json['cursor']

    # check only first 6 rules
    # which are not expanded
    for _ in range(5):
        response = await taxi_classifier.post(
            '/v1/classification-rules/updates',
            json={'limit': 1, 'cursor': cursor},
        )

        assert response.status_code == 200
        r_json = response.json()
        rules = r_json['classification_rules']
        if not rules:
            break

        assert len(rules) == 1
        expected_id += 1
        assert rules[0]['classifier_id'] == f'classifier_id_{expected_id}'
        cursor = r_json['cursor']


@pytest.mark.now('2020-08-12T00:00:00+0000')
@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'rules.sql', 'tariffs.sql'],
)
async def test_stared_model_rules(taxi_classifier, load_json):
    response = await taxi_classifier.post(
        '/v1/classification-rules/updates',
        json={'limit': 100, 'cursor': {'id': 6}},
    )

    assert response.status_code == 200
    assert response.json() == load_json('extended_model_rules.json')
