import pytest


@pytest.mark.pgsql('classifier')
async def test_empty_exceptions_v2(taxi_classifier):
    response = await taxi_classifier.post(
        '/v2/classifier-exceptions/updates', json={'limit': 100},
    )

    assert response.status_code == 200
    assert response.json() == {'classifier_exceptions_V2': [], 'limit': 100}


@pytest.mark.pgsql('classifier', files=['exceptions_v2.sql'])
async def test_all_exceptions_v2(taxi_classifier):
    response = await taxi_classifier.post(
        '/v2/classifier-exceptions/updates', json={'limit': 3},
    )

    assert response.status_code == 200
    assert response.json() == {
        'classifier_exceptions_V2': [
            {
                'id': '1111',
                'car_number': 'number_1',
                'ended_at': '2019-12-27T00:00:00+00:00',
                'started_at': '2019-11-20T00:00:00+00:00',
                'tariffs': ['econom', 'vip'],
                'zones': ['moscow', 'spb'],
                'is_deleted': False,
                'updated_at': '2021-12-19T00:00:00+00:00',
            },
            {
                'id': '2222',
                'car_number': 'number_2',
                'started_at': '2020-08-16T00:00:00+00:00',
                'tariffs': ['econom', 'vip'],
                'zones': [],
                'is_deleted': False,
                'updated_at': '2021-12-20T00:00:00+00:00',
            },
            {
                'id': '3333',
                'car_number': 'number_3',
                'tariffs': [],
                'zones': [],
                'is_deleted': False,
                'updated_at': '2021-12-21T00:00:00+00:00',
            },
        ],
        'limit': 3,
        'cursor': {'id': '3333', 'updated_at': '2021-12-21T00:00:00+00:00'},
    }


@pytest.mark.pgsql('classifier', files=['exceptions_second_insert_v2.sql'])
async def test_new_exceptions_v2(taxi_classifier):
    response = await taxi_classifier.post(
        '/v2/classifier-exceptions/updates', json={'limit': 2},
    )
    assert response.status_code == 200
    assert response.json() == {
        'classifier_exceptions_V2': [
            {
                'id': '4444',
                'car_number': 'number_4',
                'ended_at': '2019-12-27T00:00:00+00:00',
                'started_at': '2019-11-20T00:00:00+00:00',
                'tariffs': ['econom', 'vip'],
                'zones': ['moscow', 'spb'],
                'is_deleted': False,
                'updated_at': '2021-12-23T00:00:00+00:00',
            },
        ],
        'limit': 2,
    }


@pytest.mark.pgsql('classifier', files=['exceptions_v2_many_inserts.sql'])
async def test_cursor_v2(taxi_classifier):
    responses = []
    response = await taxi_classifier.post(
        '/v2/classifier-exceptions/updates', json={'limit': 2},
    )
    assert response.status_code == 200
    responses.append(response.json())

    for i in range(3):
        cursor = responses[i]['cursor']
        response = await taxi_classifier.post(
            '/v2/classifier-exceptions/updates',
            json={'limit': 2, 'cursor': cursor},
        )
        assert response.status_code == 200
        responses.append(response.json())

    for i in range(3):
        assert responses[i] == {
            'classifier_exceptions_V2': [
                {
                    'id': f'{1111 + i * 2}',
                    'car_number': f'number_{1 + i * 2}',
                    'ended_at': '2019-12-27T00:00:00+00:00',
                    'started_at': '2019-11-20T00:00:00+00:00',
                    'tariffs': ['econom', 'vip'],
                    'zones': ['moscow', 'spb'],
                    'is_deleted': False,
                    'updated_at': '2021-12-19T00:00:00+00:00',
                },
                {
                    'id': f'{1111 + i * 2 + 1}',
                    'car_number': f'number_{1 + i * 2 + 1}',
                    'ended_at': '2019-12-27T00:00:00+00:00',
                    'started_at': '2019-11-20T00:00:00+00:00',
                    'tariffs': ['econom', 'vip'],
                    'zones': ['moscow', 'spb'],
                    'is_deleted': False,
                    'updated_at': '2021-12-19T00:00:00+00:00',
                },
            ],
            'limit': 2,
            'cursor': {
                'id': f'{1111 + 2 * i + 1}',
                'updated_at': '2021-12-19T00:00:00+00:00',
            },
        }
    assert responses[3] == {
        'classifier_exceptions_V2': [
            {
                'id': '1117',
                'car_number': 'number_7',
                'ended_at': '2019-12-27T00:00:00+00:00',
                'started_at': '2019-11-20T00:00:00+00:00',
                'tariffs': ['econom', 'vip'],
                'zones': ['moscow', 'spb'],
                'is_deleted': False,
                'updated_at': '2021-12-19T00:00:00+00:00',
            },
            {
                'id': '1118',
                'car_number': 'number_8',
                'ended_at': '2019-12-27T00:00:00+00:00',
                'started_at': '2019-11-20T00:00:00+00:00',
                'tariffs': ['econom', 'vip'],
                'zones': ['moscow', 'spb'],
                'is_deleted': False,
                'updated_at': '2021-12-19T00:00:00+00:00',
            },
        ],
        'limit': 2,
    }
