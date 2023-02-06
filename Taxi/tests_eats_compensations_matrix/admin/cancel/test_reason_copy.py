import pytest


@pytest.mark.parametrize(
    'reason_id,expected_status,expected_data',
    [
        (
            1,
            200,
            {
                'allowed_callers': ['operator'],
                'allowed_countries': ['ru'],
                'code': 'place.unable_to_call',
                'group_id': 1,
                'id': 7,
                'matrix_id': 1,
                'name': 'Невозможно дозвониться до ресторана',
                'order_delivery_type': [],
                'order_type': ['shop', 'pharmacy', 'bk_logist'],
                'payment_type': ['cash'],
                'priority': 105,
                'type': 'unknown',
            },
        ),
        (2, 200, None),
        (
            3,
            409,
            {
                'code': 'MATRIX_IS_ALREADY_APPROVED',
                'message': (
                    'Matrix with id \'2\' is not editable cause it is '
                    'already approved'
                ),
            },
        ),
        (
            4,
            404,
            {
                'code': 'REASON_IS_NOT_FOUND',
                'message': 'Reason with id \'4\' is not found',
            },
        ),
        (
            10,
            404,
            {
                'code': 'REASON_IS_NOT_FOUND',
                'message': 'Reason with id \'10\' is not found',
            },
        ),
    ],
)
async def test_reason_copy(
        taxi_eats_compensations_matrix,
        pgsql,
        reason_id,
        expected_status,
        expected_data,
):
    def count(reason_id):
        pg_cursor = pgsql['eats_compensations_matrix'].cursor()
        pg_cursor.execute(
            f'SELECT reaction_id '
            f'FROM eats_compensations_matrix.order_cancel_reasons_reactions '
            f'WHERE reason_id = %s AND deleted_at IS NULL;',
            (reason_id,),
        )
        reactions_ids = pg_cursor.fetchall()
        return len(reactions_ids)

    count_before = count(reason_id)
    response = await taxi_eats_compensations_matrix.post(
        'eats-compensations-matrix/v1/admin/cancel/reason/copy/',
        params={'reason_id': reason_id},
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        new_reason_id = data['id']
        assert new_reason_id != reason_id
        count_after = count(new_reason_id)
        assert count_before == count_after
        data.pop('created_at')
        data.pop('updated_at')
    if expected_data is not None:
        assert data == expected_data
