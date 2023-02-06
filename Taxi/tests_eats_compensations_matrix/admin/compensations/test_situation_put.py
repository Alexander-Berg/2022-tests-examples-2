import pytest


def make_input_data(extra_fields=None):
    data = {
        'group_id': 2,
        'code': 'small_delay',
        'title': '<= 15 мин',
        'violation_level': 'low',
        'responsible': 'company',
        'need_confirmation': False,
        'priority': 100,
        'is_system': False,
        'order_type': ['native', 'lavka'],
        'order_delivery_type': ['marketplace', 'our_delivery'],
    }
    if extra_fields is not None:
        for key, value in extra_fields.items():
            data[key] = value
    return data


@pytest.mark.parametrize(
    'situation_id,input_data,expected_status,expected_data',
    [
        (
            1,
            make_input_data(),
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
            3,
            make_input_data(),
            200,
            {
                'id': 3,
                'matrix_id': 2,
                'group_id': 2,
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
            3,
            make_input_data(
                extra_fields={'is_available_before_final_status': False},
            ),
            200,
            {
                'id': 3,
                'matrix_id': 2,
                'group_id': 2,
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
            3,
            make_input_data(
                extra_fields={'is_available_before_final_status': True},
            ),
            200,
            {
                'id': 3,
                'matrix_id': 2,
                'group_id': 2,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'is_system': False,
                'order_type': ['native', 'lavka'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'is_available_before_final_status': True,
            },
        ),
        (
            None,
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
            None,
            make_input_data(),
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
            3,
            None,
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 1, path \'\': '
                    'missing required field \'group_id\''
                ),
            },
        ),
        (
            3,
            {
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'order_type': ['native', 'lavka'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 267, path \'\': '
                    'missing required field \'group_id\''
                ),
            },
        ),
        (
            3,
            {
                'group_id': 2,
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'order_type': ['native', 'lavka'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 259, path \'\': '
                    'missing required field \'code\''
                ),
            },
        ),
        (
            3,
            {
                'group_id': 2,
                'code': 'small_delay',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'order_type': ['native', 'lavka'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 245, path \'\': '
                    'missing required field \'title\''
                ),
            },
        ),
        (
            3,
            {
                'group_id': 2,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'order_type': ['native', 'lavka'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 256, path \'\': '
                    'missing required field \'violation_level\''
                ),
            },
        ),
        (
            3,
            {
                'group_id': 2,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'need_confirmation': False,
                'priority': 100,
                'order_type': ['native', 'lavka'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 256, path \'\': '
                    'missing required field \'responsible\''
                ),
            },
        ),
        (
            3,
            {
                'group_id': 2,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'priority': 100,
                'order_type': ['native', 'lavka'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 254, path \'\': '
                    'missing required field \'need_confirmation\''
                ),
            },
        ),
        (
            3,
            {
                'group_id': 2,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'order_type': ['native', 'lavka'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 265, path \'\': '
                    'missing required field \'priority\''
                ),
            },
        ),
        (
            3,
            {
                'group_id': 2,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 247, path \'\': '
                    'missing required field \'order_type\''
                ),
            },
        ),
        (
            3,
            {
                'group_id': 2,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'order_type': ['native', 'lavka'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 226, path \'\': '
                    'missing required field \'order_delivery_type\''
                ),
            },
        ),
        (
            4,
            make_input_data(),
            409,
            {
                'code': 'SITUATION_IS_SYSTEM',
                'message': (
                    'Situation with id \'4\' is not editable cause it is '
                    'system'
                ),
            },
        ),
        (
            10,
            make_input_data(),
            404,
            {
                'code': 'SITUATION_IS_NOT_FOUND',
                'message': 'Situation with id \'10\' is not found',
            },
        ),
    ],
)
async def test_situation_put(
        taxi_eats_compensations_matrix,
        mockserver,
        situation_id,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.put(
        '/eats-compensations-matrix/v1/admin/compensation/situation/',
        params={'situation_id': situation_id},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
