import pytest


@pytest.mark.parametrize(
    'situation_id,expected_status,expected_data',
    [
        (
            1,
            200,
            {
                'id': 1,
                'matrix_id': 1,
                'group_id': 1,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'is_system': False,
                'order_type': ['native', 'lavka'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'is_available_before_final_status': False,
            },
        ),
        (
            2,
            200,
            {
                'id': 2,
                'matrix_id': 1,
                'group_id': 2,
                'code': 'medium_delay',
                'title': 'Более 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 99,
                'is_system': False,
                'order_type': ['native', 'lavka'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'is_available_before_final_status': True,
            },
        ),
        (
            5,
            200,
            {
                'id': 5,
                'matrix_id': 5,
                'group_id': 1,
                'code': 'small_delay',
                'title': '<= 15 мин retail',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'is_system': False,
                'order_type': ['retail'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'is_available_before_final_status': False,
            },
        ),
        (
            None,
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'situation_id\' '
                    'in query: None'
                ),
            },
        ),
        (
            10,
            404,
            {
                'code': 'SITUATION_IS_NOT_FOUND',
                'message': 'Situation with id \'10\' is not found',
            },
        ),
    ],
)
async def test_situation_get(
        taxi_eats_compensations_matrix,
        mockserver,
        situation_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/compensation/situation/',
        params={'situation_id': situation_id},
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
