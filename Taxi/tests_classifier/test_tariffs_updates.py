import pytest


@pytest.mark.pgsql('classifier', files=['tariffs.sql'])
async def test_all_tariffs(taxi_classifier):
    response = await taxi_classifier.post(
        '/v1/classifier-tariffs/updates', json={'limit': 100},
    )

    assert response.status_code == 200
    assert response.json() == {
        'cursor': {'id': 6},
        'limit': 100,
        'tariffs': [
            {
                'classifier_id': 'classifier_id_1',
                'is_allowing': True,
                'tariff_id': 'tariff_id_1',
            },
            {
                'classifier_id': 'classifier_id_2',
                'is_allowing': False,
                'tariff_id': 'tariff_id_2',
            },
            {
                'classifier_id': 'classifier_id_3',
                'is_allowing': True,
                'tariff_id': 'tariff_id_3',
            },
            {
                'classifier_id': 'classifier_id_4',
                'is_allowing': False,
                'tariff_id': 'tariff_id_4',
            },
            {
                'classifier_id': 'classifier_id_5',
                'is_allowing': True,
                'tariff_id': 'tariff_id_5',
            },
            {
                'classifier_id': 'classifier_id_6',
                'is_allowing': False,
                'tariff_id': 'tariff_id_6',
            },
        ],
    }


@pytest.mark.pgsql('classifier', files=['tariffs.sql'])
async def test_limit_one(taxi_classifier):
    response = await taxi_classifier.post(
        '/v1/classifier-tariffs/updates', json={'limit': 1},
    )
    assert response.status_code == 200

    r_json = response.json()
    tariffs = r_json['tariffs']
    expected_id = 1

    assert len(tariffs) == 1
    assert tariffs[0]['tariff_id'] == f'tariff_id_{expected_id}'

    cursor = r_json['cursor']

    while len(tariffs) == 1:
        response = await taxi_classifier.post(
            '/v1/classifier-tariffs/updates',
            json={'limit': 1, 'cursor': cursor},
        )

        assert response.status_code == 200
        r_json = response.json()
        tariffs = r_json['tariffs']
        if not tariffs:
            break

        assert len(tariffs) == 1
        expected_id += 1
        assert tariffs[0]['tariff_id'] == f'tariff_id_{expected_id}'
        cursor = r_json['cursor']
