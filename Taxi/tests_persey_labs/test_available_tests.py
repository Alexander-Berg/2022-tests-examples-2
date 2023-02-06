import pytest

URL = '/internal/v1/available-tests'


@pytest.mark.config(PERSEY_LABS_LOCALITY_BY_ZONE={'Moscow': 213, 'SPb': 2})
@pytest.mark.parametrize(
    'position, expected_tests',
    [
        (
            [37.624516, 55.682996],
            [
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
            ],
        ),
        (
            [30.31, 59.94],
            [
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
            ],
        ),
        ([38.016252, 55.746110], []),
    ],
)
async def test_internal_available_tests(
        taxi_persey_labs,
        position,
        fill_labs,
        expected_tests,
        mockserver,
        load_json,
):
    fill_labs.load_lab_entities(load_json('labs.json'))

    request = {'position': position}
    response = await taxi_persey_labs.post(URL, request)
    # Status code must be checked for every request
    assert response.status_code == 200
    assert response.json()['tests'] == expected_tests
