import pytest

from test_hiring_candidates import conftest


FILE = 'requests.json'
ROUTE = '/v1/commercial-driver'


@pytest.mark.now('2020-08-05T00:00:00+03:00')
@pytest.mark.parametrize(
    ['case', 'request_name'],
    [
        ('valid', 'license_non_existent'),
        ('valid', 'license_blacklisted'),
        ('valid', 'license_from_communications'),
        ('valid', 'license_from_mongo'),
        ('valid', 'license_from_candidates'),
        ('valid', 'phone_non_existent'),
        ('valid', 'blacklisted'),
        ('valid', 'from_communications'),
        ('valid', 'from_mongo'),
        ('valid', 'from_candidates'),
        ('invalid', 'no_attributes'),
        ('invalid', 'no_valid_attributes'),
    ],
)
@pytest.mark.config(HIRING_CANDIDATES_COMMERCIAL_ENABLE_MONGO=True)
@conftest.main_configuration
async def test_commercial_driver(
        taxi_hiring_candidates_web, load_json, case, request_name,
):
    test_data = load_json(FILE)
    tasks = test_data[case][request_name]
    for task in tasks:
        params = task['request']['params']
        response_task = task['response']
        response = await taxi_hiring_candidates_web.get(ROUTE, params=params)
        assert response.status == response_task['status']
        data = await response.json()
        assert data == response_task['body']


@pytest.mark.now('2020-08-05T00:00:00+0300')
@pytest.mark.parametrize(
    ['driver_license', 'expected_code', 'expected_answer'],
    [
        ('123', 404, {}),
        (
            '456789',
            200,
            {
                'created_dttm': '2020-08-01T00:00:00+03:00',
                'driver_license': '456789',
                'is_rent': True,
                'name': 'Ivan',
            },
        ),
        (
            '0123',
            200,
            {
                'created_dttm': '2020-08-01T00:00:00+03:00',
                'driver_license': '0123',
                'is_rent': False,
                'name': 'Vasya',
            },
        ),
        (
            '12AA444333',
            200,
            {
                'created_dttm': '2020-08-01T00:00:00+03:00',
                'driver_license': '12AA444333',
                'is_rent': False,
                'name': 'Kirill',
            },
        ),
        ('14KK222888', 404, {}),
        (
            '14KK222999',
            200,
            {
                'created_dttm': '2020-09-14T16:00:00+03:00',
                'driver_license': '14KK222999',
                'is_rent': False,
                'name': 'Kirk',
            },
        ),
    ],
)
@pytest.mark.config(HIRING_CANDIDATES_COMMERCIAL_ENABLE_MONGO=False)
@conftest.main_configuration
async def test_commercial_driver_no_mongo(
        taxi_hiring_candidates_web,
        driver_license,
        expected_code,
        expected_answer,
):
    response = await taxi_hiring_candidates_web.get(
        ROUTE, params={'driver_license': driver_license},
    )
    assert response.status == expected_code
    if expected_code == 200:
        data = await response.json()
        assert data['phone']
        data.pop('phone')
        assert data == expected_answer
