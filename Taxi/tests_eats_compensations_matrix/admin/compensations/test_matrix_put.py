import pytest


@pytest.mark.parametrize(
    'matrix_id,input_data,expected_status,expected_data',
    [
        (
            2,
            {'version_code': 'v.5.0'},
            200,
            {
                'author': 'nevladov',
                'id': 2,
                'parent_version_code': 'v.1.0',
                'published': False,
                'version_code': 'v.5.0',
            },
        ),
        (
            None,
            {},
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'matrix_id\' in query: None'
                ),
            },
        ),
        (
            None,
            {'version_code': 'v.5.0'},
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'matrix_id\' in query: None'
                ),
            },
        ),
        (
            2,
            {},
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
            2,
            {'version_code': 'v.1.0'},
            409,
            {
                'code': 'VERSION_CODE_IS_ALREADY_EXIST',
                'message': (
                    'Matrix with version code \'v.1.0\' is already exist'
                ),
            },
        ),
        (
            1,
            {'version_code': 'v.5.0'},
            409,
            {
                'code': 'MATRIX_IS_ALREADY_APPROVED',
                'message': (
                    'Matrix with id \'1\' is not editable cause it is '
                    'already approved'
                ),
            },
        ),
        (
            5,
            {'version_code': 'v.5.0'},
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'5\' is not found',
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
        'eats-compensations-matrix/v1/admin/compensation/matrix/',
        params={'matrix_id': matrix_id},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
