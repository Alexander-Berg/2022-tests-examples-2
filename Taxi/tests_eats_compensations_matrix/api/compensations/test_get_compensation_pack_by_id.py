import pytest


@pytest.mark.parametrize(
    'pack_id, code, expected',
    [
        (
            3,
            200,
            {
                'pack': {
                    'id': 3,
                    'compensations': [
                        {
                            'id': 10,
                            'type': 'refund',
                            'is_full_refund': False,
                            'notification': 'order.compensation.refund',
                        },
                        {
                            'id': 13,
                            'description': 'test',
                            'type': 'tipsRefund',
                            'rate': 10.0,
                            'is_full_refund': True,
                            'max_value': 1000,
                            'min_value': 200,
                            'notification': 'order.compensation.tips_refund',
                        },
                    ],
                },
            },
        ),
        (4, 404, {'code': '404', 'message': 'Pack not found'}),
    ],
)
async def test_get_compensation_pack_by_id(
        taxi_eats_compensations_matrix, mockserver, pack_id, code, expected,
):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/api/compensation/get_pack_by_id',
        params={'pack_id': pack_id},
    )

    assert response.status_code == code
    assert response.json() == expected
