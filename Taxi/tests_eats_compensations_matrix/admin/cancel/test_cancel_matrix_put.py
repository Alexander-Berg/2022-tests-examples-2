import pytest


@pytest.mark.parametrize(
    'matrix_id, input_data,expected_status,expected_data',
    [
        (
            1,
            {'version_code': 'cancel_v.10.0'},
            200,
            {
                'author': 'nevladov',
                'id': 1,
                'published': False,
                'version_code': 'cancel_v.10.0',
            },
        ),
        (
            None,
            None,
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'matrix_id\' ' 'in query: None'
                ),
            },
        ),
        (
            None,
            {'version_code': 'cancel_v.10.0'},
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'matrix_id\' ' 'in query: None'
                ),
            },
        ),
        (
            1,
            None,
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 1, path \'\': '
                    'missing required field \'version_code\''
                ),
            },
        ),
        (
            1,
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
            1,
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
        (
            2,
            {'version_code': 'cancel_v.10.0'},
            409,
            {
                'code': 'MATRIX_IS_ALREADY_APPROVED',
                'message': (
                    'Matrix with id \'2\' is not editable cause '
                    'it is already approved'
                ),
            },
        ),
        (
            10,
            {'version_code': 'cancel_v.10.0'},
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'10\' is not found',
            },
        ),
        (
            4,
            {'version_code': 'cancel_v.10.0'},
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'4\' is not found',
            },
        ),
    ],
)
async def test_matrix_put(
        taxi_eats_compensations_matrix,
        mockserver,
        matrix_id,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.put(
        'eats-compensations-matrix/v1/admin/cancel/matrix/',
        json=input_data,
        params={'matrix_id': matrix_id},
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
