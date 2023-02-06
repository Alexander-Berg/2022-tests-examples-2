async def test_cargo_make_order(web_app_client, mockserver):
    @mockserver.json_handler('/cargo-claims/api/integration/v2/claims/create')
    async def _create(request):
        assert request.json == {
            'claim_kind': 'platform_usage',
            'client_requirements': {
                'cargo_options': [],
                'pro_courier': False,
                'taxi_class': 'eda',
            },
            'custom_context': {
                'brand_id': 151272,
                'brand_name': 'cargo-newflow claim',
                'delivery_flags': {
                    'assign_rover': False,
                    'is_forbidden_to_be_in_batch': False,
                    'is_forbidden_to_be_in_taxi_batch': False,
                    'is_forbidden_to_be_second_in_batch': False,
                },
                'place_id': 1873,
                'region_id': 1,
            },
            'features': [],
            'items': [
                {
                    'cost_currency': 'RUB',
                    'cost_value': '10150.0',
                    'droppof_point': 1,
                    'fiscalization': {
                        'article': 'Item0',
                        'item_type': 'service',
                        'supplier_inn': '762457411530',
                        'vat_code_str': 'vat0',
                    },
                    'pickup_point': 0,
                    'quantity': 1,
                    'size': {'height': 1.0, 'length': 2.0, 'width': 1.0},
                    'title': 'Робот-Котопёс, лимитированная версия',
                    'weight': 35.0,
                },
                {
                    'cost_currency': 'RUB',
                    'cost_value': '270.0',
                    'droppof_point': 1,
                    'fiscalization': {
                        'article': 'Item1',
                        'item_type': 'service',
                        'supplier_inn': '762457411530',
                        'vat_code_str': 'vat0',
                    },
                    'pickup_point': 0,
                    'quantity': 1,
                    'size': {'height': 0.1, 'length': 0.1, 'width': 0.25},
                    'title': 'Хэппи милл',
                    'weight': 0.7,
                },
                {
                    'cost_currency': 'RUB',
                    'cost_value': '140.0',
                    'droppof_point': 1,
                    'fiscalization': {
                        'article': 'Item2',
                        'item_type': 'service',
                        'supplier_inn': '762457411530',
                        'vat_code_str': 'vat0',
                    },
                    'pickup_point': 0,
                    'quantity': 1,
                    'size': {'height': 0.1, 'length': 0.15, 'width': 0.2},
                    'title': 'Кипяток в красной тарелке (борщ)',
                    'weight': 0.6,
                },
            ],
            'optional_return': False,
            'route_points': [
                {
                    'address': {
                        'coordinates': [30.406462100000002, 59.959402],
                        'fullname': (
                            'пр-кт Пискаревский, д 2, корп 3, ' 'литер А'
                        ),
                    },
                    'contact': {'name': 'John Doe', 'phone': '+70000000000'},
                    'point_id': 0,
                    'skip_confirmation': True,
                    'type': 'source',
                    'visit_order': 1,
                },
                {
                    'address': {
                        'coordinates': [30.406462100000002, 59.959402],
                        'fullname': (
                            'пр-кт Пискаревский, д 2, корп 3, ' 'литер А'
                        ),
                    },
                    'contact': {'name': 'John Doe', 'phone': '+79099999999'},
                    'point_id': 1,
                    'skip_confirmation': True,
                    'type': 'destination',
                    'visit_order': 2,
                },
            ],
            'skip_client_notify': False,
            'skip_door_to_door': True,
            'skip_emergency_notify': False,
        }

        return {
            'available_cancel_state': 'free',
            'client_requirements': {
                'taxi_class': 'eda',
                'taxi_classes': [
                    'courier',
                    'express',
                    'eda',
                    'lavka',
                    'scooters',
                ],
            },
            'corp_client_id': 'b8cfabb9d01d48079e35655c253035a9',
            'created_ts': '2022-01-13T10:30:04.058734+00:00',
            'emergency_contact': {'name': 'string', 'phone': '+70009999999'},
            'features': [],
            'id': '74ad1ab778734681bc676bbe9f8823c1',
            'items': [
                {
                    'cost_currency': 'RUB',
                    'cost_value': '100.00',
                    'droppof_point': 1068903,
                    'extra_id': '3433434232',
                    'pickup_point': 1068902,
                    'quantity': 1,
                    'size': {'height': 0.1, 'length': 0.1, 'width': 0.1},
                    'title': 'Блиночек из Теремочка',
                    'weight': 1.0,
                },
            ],
            'optional_return': True,
            'pricing': {},
            'revision': 1,
            'route_points': [
                {
                    'address': {
                        'coordinates': [37.641432, 55.735023],
                        'fullname': 'Россия, Москва, Садовническая, 77',
                    },
                    'contact': {
                        'email': 'lesf0@yandex-team.ru',
                        'name': 'string',
                        'phone': '+70009999999',
                    },
                    'external_order_cost': {
                        'currency': 'RUB',
                        'currency_sign': '₽',
                        'value': '663',
                    },
                    'external_order_id': '211-218111',
                    'id': 1068902,
                    'leave_under_door': False,
                    'meet_outside': False,
                    'no_door_call': False,
                    'skip_confirmation': True,
                    'type': 'source',
                    'visit_order': 1,
                    'visit_status': 'pending',
                    'visited_at': {},
                },
                {
                    'address': {
                        'building': '35 ',
                        'city': 'Москва',
                        'comment': 'eda claim',
                        'coordinates': [37.637299, 55.745012],
                        'country': 'Российская Федерация',
                        'fullname': 'Россия, Москва, Садовническая улица, 35',
                        'shortname': 'Садовническая улица 35 ',
                        'street': 'Садовническая улица',
                    },
                    'contact': {'name': 'string', 'phone': '+70009999999'},
                    'external_order_cost': {
                        'currency': 'RUB',
                        'currency_sign': '₽',
                        'value': '663',
                    },
                    'external_order_id': '211011-218111',
                    'id': 1068903,
                    'leave_under_door': False,
                    'meet_outside': False,
                    'no_door_call': False,
                    'skip_confirmation': True,
                    'type': 'destination',
                    'visit_order': 2,
                    'visit_status': 'pending',
                    'visited_at': {},
                },
                {
                    'address': {
                        'coordinates': [37.641432, 55.735023],
                        'fullname': 'Россия, Москва, Садовническая, 77',
                    },
                    'contact': {
                        'email': 'lesf0@yandex-team.ru',
                        'name': 'string',
                        'phone': '+70009999999',
                    },
                    'external_order_cost': {
                        'currency': 'RUB',
                        'currency_sign': '₽',
                        'value': '663',
                    },
                    'id': 1068904,
                    'leave_under_door': False,
                    'meet_outside': False,
                    'no_door_call': False,
                    'skip_confirmation': True,
                    'type': 'return',
                    'visit_order': 3,
                    'visit_status': 'pending',
                    'visited_at': {},
                },
            ],
            'skip_act': True,
            'skip_client_notify': True,
            'skip_door_to_door': False,
            'skip_emergency_notify': True,
            'status': 'new',
            'updated_ts': '2022-01-13T10:30:04.058734+00:00',
            'user_request_revision': '1',
            'version': 1,
        }

    response = await web_app_client.post(
        '/ptom/driver/v1/make-cargo-order',
        headers={'X-Idempotency-Token': 'foo'},
        json={
            'addresses': [
                {
                    'lat': 59.959402,
                    'lon': 30.406462100000002,
                    'point_id': 0,
                    'street': 'пр-кт Пискаревский, д 2, корп 3, литер А',
                },
                {
                    'lat': 59.959402,
                    'lon': 30.406462100000002,
                    'point_id': 1,
                    'street': 'пр-кт Пискаревский, д 2, корп 3, литер А',
                },
            ],
            'goods': [
                {
                    'count': 1,
                    'destination': 1,
                    'height': 1.0,
                    'length': 2.0,
                    'name': 'Робот-Котопёс, лимитированная версия',
                    'price': 10150.0,
                    'weight': 35.0,
                    'width': 1.0,
                },
                {
                    'count': 1,
                    'destination': 1,
                    'height': 0.1,
                    'length': 0.1,
                    'name': 'Хэппи милл',
                    'price': 270.0,
                    'weight': 0.7,
                    'width': 0.25,
                },
                {
                    'count': 1,
                    'destination': 1,
                    'height': 0.1,
                    'length': 0.15,
                    'name': 'Кипяток в красной тарелке (борщ)',
                    'price': 140.0,
                    'weight': 0.6,
                    'width': 0.2,
                },
            ],
            'markdown': False,
            'tariff': 'eda',
        },
    )

    assert response.status == 200
    assert _create.times_called == 1


async def test_cargo_order_status(web_app_client, mockserver):
    @mockserver.json_handler('/cargo-claims/v1/claims/cut')
    async def _get(request):
        return {
            'id': '64b47f84825b483fa143abbaba500f05',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '1',
            'skip_client_notify': False,
        }

    @mockserver.json_handler('/cargo-claims/v2/admin/claim/courier')
    async def _forced_performer(request):
        return {}

    @mockserver.json_handler('/cargo-claims/api/integration/v2/claims/accept')
    async def _accept(request):
        return {
            'id': '64b47f84825b483fa143abbaba500f05',
            'status': 'performer_lookup',
            'version': 1,
            'user_request_revision': '1',
            'skip_client_notify': False,
        }

    response = await web_app_client.post(
        '/ptom/driver/v1/cargo-order-status',
        json={
            'claim_id': '867539f3816b43c6b38c0c0b1989b8df',
            'park_id': '7ad36bc7560449998acbe2c57a75c293',
            'driver_id': '68b16e654baae06b8993d2dcf122b0bf',
        },
    )

    assert response.status == 200
    assert _get.times_called == 1
    assert _forced_performer.times_called == 1
    assert _accept.times_called == 1
