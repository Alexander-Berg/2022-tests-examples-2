import pytest


async def test_tests(taxi_persey_labs):
    response = await taxi_persey_labs.get('/internal/v1/tests')
    # Status code must be checked for every request
    assert response.status_code == 200
    assert response.json()['tests'] == [
        {
            'id': 'covid_slow',
            'name': 'Медленный тест COVID',
            'price': {
                'logistics_rub': '1000',
                'test_rub': '3000',
                'sampling_rub': '123',
            },
            'days_to_ready': 3,
            'test_systems': [
                {
                    'name': 'Монетка',
                    'qualities': ['Точность тестирования: 50%'],
                },
            ],
        },
        {
            'id': 'covid_fast',
            'name': 'Быстрый тест COVID',
            'price': {'logistics_rub': '1000', 'test_rub': '2000'},
            'days_to_ready': 1,
            'test_systems': [
                {
                    'name': 'ДНК-тестирование',
                    'qualities': ['Точность тестирования: 90%'],
                },
            ],
        },
    ]


@pytest.mark.config(
    PERSEY_LABS_TESTS={
        'covid_fast': {
            'name': 'Быстрый тест COVID',
            'price': {'test_rub': '1', 'logistics_rub': '2'},
            'detailed_price': {
                'leid_1': {
                    '__default__': {
                        'test_rub': '3',
                        'logistics_rub': '4',
                        'sampling_rub': '5',
                    },
                    '123': {
                        'test_rub': '6',
                        'logistics_rub': '7',
                        'sampling_rub': '8',
                    },
                    '456': {'test_rub': '9', 'logistics_rub': '10'},
                },
                'leid_2': {
                    '__default__': {'test_rub': '11', 'logistics_rub': '12'},
                },
            },
            'days_to_ready': 1,
            'test_systems': [
                {
                    'name': 'ДНК-тестирование',
                    'qualities': ['Точность тестирования: 90%'],
                },
            ],
        },
        'covid_slow': {
            'name': 'Медленный тест COVID',
            'price': {
                'test_rub': '13',
                'logistics_rub': '14',
                'sampling_rub': '15',
            },
            'days_to_ready': 3,
            'test_systems': [
                {
                    'name': 'Монетка',
                    'qualities': ['Точность тестирования: 50%'],
                },
            ],
        },
    },
)
@pytest.mark.parametrize(
    'query, expected_status_code, expected_response',
    [
        (
            'id=covid_fast&lab_entity_id=leid_1&locality_id=123',
            200,
            {'test_rub': '6', 'logistics_rub': '7', 'sampling_rub': '8'},
        ),
        ('id=covid_medium&lab_entity_id=leid_1&locality_id=123', 400, None),
        (
            'id=covid_fast&lab_entity_id=leid_1&locality_id=666',
            200,
            {'test_rub': '3', 'logistics_rub': '4', 'sampling_rub': '5'},
        ),
        (
            'id=covid_fast&lab_entity_id=leid_3&locality_id=123',
            200,
            {'test_rub': '1', 'logistics_rub': '2'},
        ),
        (
            'id=covid_slow&lab_entity_id=leid_3&locality_id=123',
            200,
            {'test_rub': '13', 'logistics_rub': '14', 'sampling_rub': '15'},
        ),
    ],
)
async def test_tests_price(
        taxi_persey_labs, query, expected_status_code, expected_response,
):
    response = await taxi_persey_labs.get(f'/internal/v1/tests/price/?{query}')

    assert response.status_code == expected_status_code

    if response.status_code == 200:
        assert response.json() == expected_response
    else:
        assert response.json() == {
            'code': 'TEST_NOT_FOUND',
            'message': 'Test id not found in config',
        }
