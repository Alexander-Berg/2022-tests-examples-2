import pytest


@pytest.mark.parametrize(
    'reason_id, code, expected',
    [
        (
            1,
            200,
            {
                'matrix_code': 'v.1.0',
                'reason': {
                    'code': 'place.unable_to_call',
                    'group': {'code': 'place', 'id': 1, 'name': 'Ресторан'},
                    'id': 1,
                    'matrix_version_code': 'v.1.0',
                },
                'group': {'code': 'place', 'id': 1, 'name': 'Ресторан'},
            },
        ),
        (2, 400, {'code': '404', 'message': 'Reason is not found'}),
        (3, 400, {'code': '404', 'message': 'Reason is not found'}),
    ],
)
async def test_get_reason_by_id(
        taxi_eats_compensations_matrix, mockserver, reason_id, code, expected,
):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/api/cancel/get_reason_by_id',
        params={'reason_id': reason_id},
    )

    assert response.status_code == code
    assert response.json() == expected
