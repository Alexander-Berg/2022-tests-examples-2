import pytest


def make_input_data(group_id, extra_fields=None):
    data = {
        'group_id': group_id,
        'code': 'small_delay',
        'title': '<= 15 мин',
        'violation_level': 'low',
        'responsible': 'company',
        'need_confirmation': False,
        'priority': 100,
        'is_system': False,
        'order_type': ['lavka', 'pharmacy'],
        'order_delivery_type': ['our_delivery'],
    }

    if extra_fields is not None:
        for key, value in extra_fields.items():
            data[key] = value
    return data


@pytest.mark.parametrize(
    'matrix_id,input_data,expected_status,expected_data',
    [
        (
            2,
            make_input_data(1),
            200,
            {
                'id': 6,
                'matrix_id': 2,
                'group_id': 1,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'is_system': False,
                'order_type': ['lavka', 'pharmacy'],
                'order_delivery_type': ['our_delivery'],
                'is_available_before_final_status': False,
            },
        ),
        (
            2,
            make_input_data(
                1, extra_fields={'is_available_before_final_status': False},
            ),
            200,
            {
                'id': 6,
                'matrix_id': 2,
                'group_id': 1,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'is_system': False,
                'order_type': ['lavka', 'pharmacy'],
                'order_delivery_type': ['our_delivery'],
                'is_available_before_final_status': False,
            },
        ),
        (
            2,
            make_input_data(
                1, extra_fields={'is_available_before_final_status': True},
            ),
            200,
            {
                'id': 6,
                'matrix_id': 2,
                'group_id': 1,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'is_system': False,
                'order_type': ['lavka', 'pharmacy'],
                'order_delivery_type': ['our_delivery'],
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
                    'invalid int32_t value of \'matrix_id\' in query: None'
                ),
            },
        ),
        (
            None,
            make_input_data(1),
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
                    'missing required field \'group_id\''
                ),
            },
        ),
        (
            2,
            {
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'order_type': ['lavka', 'pharmacy'],
                'order_delivery_type': ['our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 254, path \'\': '
                    'missing required field \'group_id\''
                ),
            },
        ),
        (
            2,
            {
                'group_id': 1,
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'order_type': ['lavka', 'pharmacy'],
                'order_delivery_type': ['our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 246, path \'\': '
                    'missing required field \'code\''
                ),
            },
        ),
        (
            2,
            {
                'group_id': 1,
                'code': 'small_delay',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'order_type': ['lavka', 'pharmacy'],
                'order_delivery_type': ['our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 232, path \'\': '
                    'missing required field \'title\''
                ),
            },
        ),
        (
            2,
            {
                'group_id': 1,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'order_type': ['lavka', 'pharmacy'],
                'order_delivery_type': ['our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 243, path \'\': '
                    'missing required field \'violation_level\''
                ),
            },
        ),
        (
            2,
            {
                'group_id': 1,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'need_confirmation': False,
                'priority': 100,
                'order_type': ['lavka', 'pharmacy'],
                'order_delivery_type': ['our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 243, path \'\': '
                    'missing required field \'responsible\''
                ),
            },
        ),
        (
            2,
            {
                'group_id': 1,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'priority': 100,
                'order_type': ['lavka', 'pharmacy'],
                'order_delivery_type': ['our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 241, path \'\': '
                    'missing required field \'need_confirmation\''
                ),
            },
        ),
        (
            2,
            {
                'group_id': 1,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'order_type': ['lavka', 'pharmacy'],
                'order_delivery_type': ['our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 252, path \'\': '
                    'missing required field \'priority\''
                ),
            },
        ),
        (
            2,
            {
                'group_id': 1,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'order_delivery_type': ['our_delivery'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 232, path \'\': '
                    'missing required field \'order_type\''
                ),
            },
        ),
        (
            2,
            {
                'group_id': 1,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 100,
                'order_type': ['lavka', 'pharmacy'],
                'is_system': False,
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 228, path \'\': '
                    'missing required field \'order_delivery_type\''
                ),
            },
        ),
        (
            1,
            make_input_data(1),
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
            10,
            make_input_data(1),
            404,
            {
                'code': 'MATRIX_OR_GROUP_IS_NOT_FOUND',
                'message': 'Related matrix or group is not found',
            },
        ),
        (
            2,
            make_input_data(10),
            404,
            {
                'code': 'MATRIX_OR_GROUP_IS_NOT_FOUND',
                'message': 'Related matrix or group is not found',
            },
        ),
    ],
)
async def test_situation_post(
        taxi_eats_compensations_matrix,
        mockserver,
        matrix_id,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.post(
        '/eats-compensations-matrix/v1/admin/compensation/situation/',
        params={'matrix_id': matrix_id},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
