import pytest


@pytest.mark.parametrize(
    'input_data,expected_status,expected_data',
    [
        (
            {'version_code': 'cancel_v.10.0'},
            200,
            {
                'author': 'nevladov',
                'id': 6,
                'published': False,
                'version_code': 'cancel_v.10.0',
            },
        ),
        (
            None,
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 1, path \'\': missing '
                    'required field \'version_code\''
                ),
            },
        ),
        (
            {'version_code': None},
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 21, path \'version_code\': '
                    'string was expected, but null found, '
                    'the latest token was : null'
                ),
            },
        ),
        (
            {'version_code': 100500},
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 23, path \'version_code\': '
                    'string was expected, but integer found, '
                    'the latest token was : 100500'
                ),
            },
        ),
        (
            {'version_code': 'cancel_v.3.0'},
            409,
            {
                'code': 'VERSION_CODE_IS_ALREADY_EXIST',
                'message': (
                    'Matrix with version code \'cancel_v.3.0\' '
                    'is already exist'
                ),
            },
        ),
    ],
)
async def test_matrix_post(
        taxi_eats_compensations_matrix,
        mockserver,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.post(
        'eats-compensations-matrix/v1/admin/cancel/matrix/',
        headers={'X-Yandex-Login': 'nevladov'},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
