import pytest


@pytest.mark.pgsql('classifier', files=['exceptions.sql'])
async def test_all_exceptions(taxi_classifier):
    response = await taxi_classifier.post(
        '/v1/classifier-exceptions/updates', json={'limit': 100},
    )

    assert response.status_code == 200
    assert response.json() == {
        'classifier_exceptions': [
            {
                'car_number': 'number_1',
                'ended_at': '2019-12-27T00:00:00+00:00',
                'started_at': '2019-11-20T00:00:00+00:00',
                'tariffs': ['econom', 'vip'],
                'zones': ['moscow', 'spb'],
            },
            {
                'car_number': 'number_2',
                'started_at': '2020-08-16T00:00:00+00:00',
                'tariffs': ['econom', 'vip'],
                'zones': [],
            },
            {'car_number': 'number_3', 'tariffs': [], 'zones': []},
        ],
        'limit': 100,
        'cursor': {'id': 3},
    }


@pytest.mark.pgsql('classifier', files=['exceptions.sql'])
async def test_limit_one(taxi_classifier):
    response = await taxi_classifier.post(
        '/v1/classifier-exceptions/updates', json={'limit': 1},
    )
    assert response.status_code == 200

    r_json = response.json()
    exceptions = r_json['classifier_exceptions']
    expected_id = 1

    assert len(exceptions) == 1
    assert exceptions[0]['car_number'] == f'number_{expected_id}'

    cursor = r_json['cursor']

    while len(exceptions) == 1:
        response = await taxi_classifier.post(
            '/v1/classifier-exceptions/updates',
            json={'limit': 1, 'cursor': cursor},
        )

        assert response.status_code == 200
        r_json = response.json()
        exceptions = r_json['classifier_exceptions']
        if not exceptions:
            break

        assert len(exceptions) == 1
        expected_id += 1
        assert exceptions[0]['car_number'] == f'number_{expected_id}'
        cursor = r_json['cursor']
