import pytest


RETURN_REASONS = [
    'replace_return',
    'loss_return',
    'vacation_return',
    'dismiss_return',
]
GIVE_OUT_REASON = [
    'first_give_out',
    'change_give_out',
    'loss_give_out',
    'vacation_give_out',
    'additional_give_out',
]


def _build_request_data(
        place_id,
        courier_id,
        type_id,
        size_id,
        count,
        reason,
        comment=None,
        depremization=None,
        number=None,
        no_balance=None,
):
    data = {
        'data': {
            'attributes': {
                'positions': [
                    {
                        'type_id': type_id,
                        'size_id': size_id,
                        'used': False,
                        'count': count,
                    },
                ],
                'reason': reason,
                'comment': comment,
            },
            'relationships': {
                'place': {'data': {'id': place_id}},
                'courier': {'data': {'id': courier_id}},
            },
        },
    }
    if no_balance is not None:
        data['data']['attributes']['no_balance'] = no_balance
    if depremization is not None:
        data['data']['attributes']['positions'][0][
            'depremization_sum'
        ] = depremization
    if number:
        data['data']['attributes']['positions'][0]['number'] = number
    return data


@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=[
        'add_regions.sql',
        'add_work_statuses.sql',
        'add_project_types.sql',
        'add_uniform_types.sql',
        'add_places.sql',
        'add_courier.sql',
        'add_users.sql',
        'add_courier_uniforms.sql',
        'add_place_uniforms.sql',
    ],
)
@pytest.mark.parametrize(
    'response_code,place_id,courier_id,user_id,type_id,size_id,count,reason,'
    'optional_params',
    [
        (201, 1, 1, '1', 1, 1, 1, 'first_give_out', {'number': '111112'}),
        (422, 1, 2, '1', 1, 1, 1, 'first_give_out', {'number': '111112'}),
        (404, 10, 1, '1', 1, 1, 1, 'first_give_out', {}),
        (404, 1, 10, '1', 1, 1, 1, 'first_give_out', {}),
        (404, 1, 1, '10', 1, 1, 1, 'first_give_out', {}),
        (404, 1, 1, '1', 10, 1, 1, 'first_give_out', {}),
        (404, 1, 1, '1', 1, 10, 1, 'first_give_out', {}),
        (422, 1, 1, '1', 1, 1, 111, 'first_give_out', {}),
        (201, 1, 1, '1', 1, 1, 1, 'replace_return', {'no_balance': False}),
        (201, 1, 1, '1', 1, 1, 1, 'replace_return', {'depremization': 123}),
        (201, 1, 1, '1', 1, 1, 1, 'replace_return', {'depremization': 0}),
        (422, 1, 1, '1', 3, 1, 1, 'first_give_out', {}),
        (422, 1, 1, '1', 2, 1, 1, 'change_give_out', {}),
        (422, 1, 1, '1', 3, 1, 1, 'first_give_out', {}),
        (422, 1, 1, '1', 2, 1, 1, 'replace_return', {'depremization': 123}),
        (201, 1, 1, '1', 3, 1, 1, 'first_give_out', {'number': '111112'}),
        (
            201,
            1,
            1,
            '1',
            3,
            1,
            1,
            'first_give_out',
            {'number': '111112', 'comment': 'test comment'},
        ),
        (
            201,
            1,
            1,
            '1',
            3,
            1,
            1,
            'replace_return',
            {'number': '111112', 'no_balance': False},
        ),
        (201, 1, 1, '1', 3, 1, 1, 'loss_return', {'number': '111112'}),
        (201, 1, 1, '1', 3, 1, 1, 'replace_return', {'no_balance': True}),
    ],
)
async def test_uniform_courier_relocation(
        taxi_eats_couriers_equipment,
        response_code,
        place_id,
        courier_id,
        user_id,
        type_id,
        size_id,
        count,
        reason,
        optional_params,
        pgsql,
):
    cursor = pgsql['outsource-lavka-transport'].cursor()
    used_value = False
    if reason in RETURN_REASONS:
        used_value = True
    cursor.execute(
        f'SELECT count from place_uniforms'
        f' where type_id={type_id} and place_id={place_id} and '
        f'used={used_value};',
    )
    result = list(row for row in cursor)
    start_place_uniforms_count = result[0][0] if result else 0

    create_response = await taxi_eats_couriers_equipment.post(
        '/v1.0/uniform/courier-relocation',
        json=_build_request_data(
            place_id,
            courier_id,
            type_id,
            size_id,
            count,
            reason,
            **optional_params,
        ),
        headers={'X-Eats-SUP-UserId': user_id},
    )
    assert create_response.status_code == response_code, create_response.text
    if response_code == 201:
        cursor.execute(
            'SELECT place_id,courier_id,reason,comment from '
            'uniform_courier_relocations;',
        )
        result = list(row for row in cursor)
        assert result == [
            (
                courier_id,
                courier_id,
                reason,
                optional_params.get('comment', ''),
            ),
        ]

        cursor.execute(
            f'SELECT type_id,place_id,used,count,size_id from place_uniforms'
            f' where type_id={type_id} and place_id={place_id} and '
            f'used={used_value};',
        )
        result = list(row for row in cursor)
        if reason in GIVE_OUT_REASON:
            assert result == [(type_id, place_id, False, 0, size_id)]
        elif reason == 'loss_return' or optional_params.get('no_balance'):
            assert result == []
        else:
            assert result == [
                (
                    type_id,
                    place_id,
                    True,
                    start_place_uniforms_count + count,
                    size_id,
                ),
            ]

        cursor.execute(
            f'SELECT type_id,courier_id,used,count,size_id,number from '
            f'courier_uniforms where courier_id={courier_id} and'
            f' type_id={type_id};',
        )
        result = list(row for row in cursor)
        if reason in GIVE_OUT_REASON:
            assert result == [
                (
                    type_id,
                    courier_id,
                    False,
                    2,
                    size_id,
                    optional_params.get('number'),
                ),
            ]
        else:
            assert result == [(type_id, courier_id, False, 0, size_id, None)]

        cursor.execute(
            'SELECT diff, depremization, number '
            'from uniform_courier_relocation_courier_uniform;',
        )
        result = list(row for row in cursor)
        if reason in GIVE_OUT_REASON:
            assert result == [(1, None, optional_params.get('number'))]
        else:
            assert result == [
                (
                    -1,
                    None
                    if optional_params.get('depremization') == 0
                    else optional_params.get('depremization'),
                    optional_params.get('number'),
                ),
            ]


@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=[
        'add_regions.sql',
        'add_work_statuses.sql',
        'add_project_types.sql',
        'add_uniform_types.sql',
        'add_places.sql',
        'add_courier.sql',
        'add_users.sql',
        'add_courier_uniforms.sql',
        'add_place_uniforms.sql',
    ],
)
async def test_ucr_bag_conflict(taxi_eats_couriers_equipment):
    response = await taxi_eats_couriers_equipment.post(
        '/v1.0/uniform/courier-relocation',
        json=_build_request_data(
            1, 1, 1, 1, 1, 'first_give_out', None, None, 'test_number_123',
        ),
        headers={'X-Eats-SUP-UserId': '1'},
    )
    assert response.status_code == 409, response.text
    assert response.json() == {
        'errors': [
            {
                'detail': 'Позиция с этим номером уже выдана другому курьеру',
                'source': {'pointer': 'data/attributes/positions/0/number'},
                'title': 'Unique violation',
            },
        ],
    }
