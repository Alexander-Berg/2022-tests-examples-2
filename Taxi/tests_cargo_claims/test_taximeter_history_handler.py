async def test_skip_confirmation(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    await state_controller.apply(target_status='performer_found')

    response = await taxi_cargo_claims.post(
        'v1/claims/taximeter-history',
        params={'order_id': 'order_alias_id_1'},
        headers=get_default_headers(),
        json={},
    )

    assert response.json() == {
        'cargo_ref_id': 'order/9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
        'claim_points': [
            {
                'address': {
                    'building': '82',
                    'city': 'Москва',
                    'coordinates': [37.5, 55.7],
                    'country': 'Россия',
                    'fullname': 'БЦ Аврора',
                    'porch': '4',
                    'street': 'Садовническая улица',
                },
                'id': 1,
                'label': 'Получение',
                'phones': [
                    {
                        'label': 'phone_label.source',
                        'type': 'source',
                        'view': 'main',
                    },
                ],
                'type': 'source',
            },
            {
                'address': {
                    'building': '30',
                    'city': 'Киев',
                    'comment': 'other_comment',
                    'coordinates': [37.6, 55.6],
                    'country': 'Украина',
                    'door_code': '0к123',
                    'flat': 87,
                    'floor': 12,
                    'fullname': 'Свободы, 30',
                    'porch': '2',
                    'sflat': '87B',
                    'sfloor': '12',
                    'street': 'Свободы',
                },
                'id': 2,
                'label': 'Выдача',
                'phones': [
                    {
                        'label': 'phone_label.destination',
                        'type': 'destination',
                        'view': 'extra',
                    },
                ],
                'type': 'destination',
            },
        ],
    }
