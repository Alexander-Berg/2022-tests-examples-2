async def test_reason_reaction_list_get(
        taxi_eats_compensations_matrix, mockserver,
):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/cancel/reason-reaction/list',
        params={'reason_id': 2},
    )
    assert response.status == 200
    data = response.json()
    expected_data = {
        'reasons_reactions': [
            {
                'reason_reaction': {
                    'id': 7,
                    'reason_id': 2,
                    'reaction_id': 1,
                    'minimal_cost': 100.0,
                    'minimal_eater_reliability': 'good',
                    'is_allowed_before_place_confirmed': True,
                    'is_allowed_for_fast_cancellation': True,
                    'is_for_vip_only': True,
                },
                'reaction': {
                    'id': 1,
                    'type': 'order.cancel.reaction.compensation',
                    'payload': {
                        'limit': 100,
                        'limit_currency': 'RUB',
                        'rate': 15,
                    },
                    'created_at': '2020-06-23T08:00:00+00:00',
                    'updated_at': '2020-06-23T08:00:00+00:00',
                    'label': 'Промокод 15%',
                },
            },
            {
                'reason_reaction': {
                    'id': 8,
                    'reason_id': 2,
                    'reaction_id': 1,
                    'minimal_cost': 100.0,
                    'minimal_eater_reliability': 'good',
                    'is_allowed_before_place_confirmed': False,
                    'is_allowed_for_fast_cancellation': False,
                    'is_for_vip_only': False,
                },
                'reaction': {
                    'id': 1,
                    'type': 'order.cancel.reaction.compensation',
                    'payload': {
                        'limit': 100,
                        'limit_currency': 'RUB',
                        'rate': 15,
                    },
                    'created_at': '2020-06-23T08:00:00+00:00',
                    'updated_at': '2020-06-23T08:00:00+00:00',
                    'label': 'Промокод 15%',
                },
            },
            {
                'reason_reaction': {
                    'id': 4,
                    'reason_id': 2,
                    'reaction_id': 3,
                    'minimal_cost': 100.0,
                    'minimal_eater_reliability': 'bad',
                    'is_allowed_before_place_confirmed': True,
                    'is_allowed_for_fast_cancellation': True,
                    'is_for_vip_only': True,
                },
                'reaction': {
                    'id': 3,
                    'type': 'order.cancel.reaction.return_promocode',
                    'payload': {},
                    'created_at': '2020-06-23T08:00:00+00:00',
                    'updated_at': '2020-06-23T08:00:00+00:00',
                    'label': 'Возврат промокода',
                },
            },
        ],
    }
    assert len(data['reasons_reactions']) == 3
    assert data == expected_data
