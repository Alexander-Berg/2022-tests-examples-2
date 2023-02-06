import pytest


@pytest.mark.parametrize(
    'type_id,expected_status,expected_data',
    [
        (
            1,
            409,
            {
                'code': 'RELATED_LINKS_EXIST',
                'message': (
                    'Unable to delete pack cause some related links exist'
                ),
            },
        ),
        (4, 200, None),
        (
            7,
            404,
            {
                'code': 'COMPENSATION_TYPE_IS_NOT_FOUND',
                'message': 'Compensation type with id \'7\' is not found',
            },
        ),
        (
            None,
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'type_id\' in query: None'
                ),
            },
        ),
    ],
)
async def test_type_delete(
        taxi_eats_compensations_matrix,
        mockserver,
        type_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.delete(
        'eats-compensations-matrix/v1/admin/compensation/type/',
        params={'type_id': type_id},
    )
    assert response.status == expected_status
    if expected_status != 200:
        data = response.json()
        assert data == expected_data
