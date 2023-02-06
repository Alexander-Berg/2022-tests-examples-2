import pytest


ROUTE = '/v1/driver-for-city'


@pytest.mark.now('2020-08-05T00:00:00+0300')
@pytest.mark.parametrize(
    ['driver_license', 'expected_code', 'expected_answer'],
    [
        ('123', 404, {}),
        (
            '456789',
            200,
            {
                'created_dttm': '2020-09-11T15:00:00+03:00',
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
        ('12AA444333', 404, {}),
        (
            '14KK222888',
            200,
            {
                'created_dttm': '2020-09-14T15:00:00+03:00',
                'driver_license': '14KK222888',
                'is_rent': False,
                'name': 'Ivan',
            },
        ),
        ('FREEDRIVER', 404, {}),
    ],
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'hiring-candidates', 'dst': 'personal'}],
)
@pytest.mark.usefixtures('personal', 'mock_data_markup_perform')
async def test_driver_for_city(
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
