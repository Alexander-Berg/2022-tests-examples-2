def get_default_calcplan_config():
    return {
        'plan': [
            {'stage_name': 'AddPhysical', 'version': 1},
            {'stage_name': 'AddVat', 'version': 1},
            {'stage_name': 'RoundPrices', 'version': 1},
        ],
    }


def get_default_calculated_price():
    return {'total': 2040, 'total_without_vat': 1700}


def get_default_calc_request(idempotency_token='token'):
    return {
        'idempotency_token': idempotency_token,
        'stations': [
            {
                'operator_station_id': 'FM Logistic',
                'phone': '+79991231231',
                'station_id': 'e83b4c00-9cd7-4edc-8ef8-00ddbec93fcf',
                'operator_id': 'nespresso',
                'station_name': 'ФМ Чехов',
                'contact_name': 'Doe John ',
                'address': 'ул. Производственная, владение 3',
                'location': [37, 55],
            },
        ],
        'employer': {
            'employer_id': 'a82624ff-303a-4242-bf93-cceb31869bc1',
            'employer_meta': {
                'registry': {
                    'separator': ';',
                    'config_template': 'nespresso',
                    'skip_header': True,
                },
                'default_nds': 20,
                'default_inn': '7705739450',
                'default_store_id': '',
                'brand_name': 'Nespresso',
            },
            'employer_type': 'default',
            'employer_code': 'nespresso',
        },
        'model': {
            'request_code': '912271121',
            'request_id': 'b6b9395c-4941-4642-85a1-10176773c7eb',
            'events_chain': [
                {
                    'reservation_details': {
                        'external_order_id': '',
                        'internal_place_id': (
                            '65a4272c-4268-42bf-9f91-f00949a83f9b'
                        ),
                        'operator_id': 'nespresso',
                        'reserve_take_ts': 1615532400,
                        'deploy_id': '',
                        'reservation_id': (
                            '898f790e-e979-4e41-ae53-2ad16ca0433f'
                        ),
                        'reserve_put_ts': 1615467414,
                        'status': 'current',
                    },
                    'node_details': {
                        'node_id': '860aa215-e9e1-48e2-9caa-eb9a50cd111e',
                        'implementation': {
                            'station_id': (
                                'e83b4c00-9cd7-4edc-8ef8-00ddbec93fcf'
                            ),
                            'class_name': 'warehouse',
                        },
                        'code': 'node_from',
                    },
                    'type': 'NODE',
                },
                {
                    'action_details': {
                        'requested_instant': {
                            'max': 1615532400,
                            'policy': 'interval_with_fees',
                            'min': 1615467414,
                        },
                        'action_status': 'rejected',
                        'status': 'finished',
                        'action_id': 3788,
                        'action_code': (
                            'a_from_8ef78dc1-abae0a27-5cac2713-8565b98c'
                        ),
                    },
                    'type': 'ACTION',
                },
                {
                    'type': 'TRANSFER',
                    'transfer_details': {
                        'transfer_id': '776b1234-60b8-4ef6-b463-98da806f661d',
                        'external_order_id': '2271939',
                        'internal_place_id': (
                            '65a4272c-4268-42bf-9f91-f00949a83f9b'
                        ),
                        'waybill_planner_task_id': '',
                        'enabled': True,
                        'operator_id': 'strizh',
                        'return_node_id': (
                            '860aa215-e9e1-48e2-9caa-eb9a50cd111e'
                        ),
                        'semi_live_batching_allowed': False,
                        'batching_allowed': False,
                        'status': 'canceled',
                        'is_allow_to_be_second_in_batching': True,
                        'new_logistic_contract': False,
                        'is_allowed_to_be_in_taxi_batch': True,
                    },
                },
                {
                    'action_details': {
                        'requested_instant': {
                            'max': 1615539600,
                            'policy': 'interval_with_fees',
                            'min': 1615532400,
                        },
                        'action_status': 'rejected',
                        'status': 'finished',
                        'action_id': 3789,
                        'action_code': (
                            'a_to_8ef78dc1-abae0a27-5cac2713-8565b98c'
                        ),
                    },
                    'type': 'ACTION',
                },
                {
                    'reservation_details': {
                        'external_order_id': (
                            'fake:fcfdf6e2-1c3fd25-e46c521a-6dca18e'
                        ),
                        'internal_place_id': (
                            '65a4272c-4268-42bf-9f91-f00949a83f9b'
                        ),
                        'operator_id': 'external_operator',
                        'reserve_take_ts': 1615539600,
                        'deploy_id': '',
                        'reservation_id': (
                            '644e600c-dde4-4366-8ff8-765b67971544'
                        ),
                        'reserve_put_ts': 1615532400,
                        'status': 'canceled',
                    },
                    'node_details': {
                        'node_id': '9553382a-6d7d-4d27-a952-daed051db16e',
                        'implementation': {
                            'delivery_expectations': {
                                'max': 1615539600,
                                'policy': 'interval_with_fees',
                                'min': 1615532400,
                            },
                            'class_name': 'tmp',
                            'coord': {'lat': 55.739554, 'lon': 37.597414},
                            'details': {
                                'house': '25',
                                'country': 'Россия',
                                'comment': '',
                                'locality': 'Москва',
                                'full_address': (
                                    'Остоженка, д 25,Москва,119034'
                                ),
                                'region': '213',
                                'street': 'улица Остоженка',
                            },
                        },
                        'code': 'node_to',
                    },
                    'type': 'NODE',
                },
            ],
            'resource': {
                'incorrect_place_ids': [],
                'place_barcodes': ['LD454'],
                'resource_id': 'e319f71d-b053-4584-a8e0-f004548eaa95',
                'resource_code': '912271121.1',
                'features': [
                    {
                        'resource_billing_feature': {
                            'assessed_cost': 641000,
                            'delivery_n_d_s': 20,
                            'payment_method': 'card_on_receipt',
                            'delivery_cost': 20000,
                            'client_order_id': '',
                        },
                        'class_name': 'billing',
                        'resource_personal_info_feature': {
                            'patronymic': '',
                            'last_name': '',
                            'first_name': 'Маркин, Дмитрий Викторович',
                            'contacts': [
                                {
                                    'class_name': 'phone',
                                    'phone_contact': {
                                        'phone_number': '+79117749840',
                                    },
                                },
                            ],
                            'yandex_u_i_d': '',
                        },
                    },
                    {
                        'class_name': 'recipient',
                        'resource_personal_info_feature': {
                            'patronymic': '',
                            'last_name': '',
                            'first_name': 'Маркин, Дмитрий Викторович',
                            'contacts': [
                                {
                                    'class_name': 'phone',
                                    'phone_contact': {
                                        'phone_number': '+79117749840',
                                    },
                                },
                            ],
                            'yandex_u_i_d': '',
                        },
                    },
                    {
                        'class_name': 'physical',
                        'resource_physical_feature': {
                            'd_x': 300,
                            'barcode': '',
                            'items': [
                                {
                                    'marking_code': '',
                                    'barcode': '',
                                    'd_x': 0,
                                    'assessed_unit_price': 200000,
                                    'article': '5105.01',
                                    'd_z': 0,
                                    'd_y': 0,
                                    'name': 'Насадка для капучинатора 5105.01',
                                    'billing_details': {
                                        'refundable': True,
                                        'i_n_n': '7705739450',
                                        'currency': 'RUB',
                                        'assessed_unit_price': 200000,
                                        'n_d_s': 20,
                                        'tax_system_code': 1,
                                    },
                                    'weight_net': 0,
                                    'count': 3,
                                    'non_physical_item': False,
                                    'description': '',
                                    'weight_gross': 0,
                                    'weight_tare': 0,
                                    'physical_dims': {
                                        'weight_tare': 0,
                                        'd_y': 0,
                                        'd_x': 0,
                                        'weight_gross': 0,
                                        'd_z': 0,
                                        'weight_net': 0,
                                    },
                                },
                                {
                                    'marking_code': '',
                                    'barcode': '',
                                    'd_x': 0,
                                    'assessed_unit_price': 41000,
                                    'article': '5048-6',
                                    'd_z': 0,
                                    'd_y': 0,
                                    'name': (
                                        'Средство для удаления накипи 5048-6'
                                    ),
                                    'billing_details': {
                                        'refundable': True,
                                        'i_n_n': '7705739450',
                                        'currency': 'RUB',
                                        'assessed_unit_price': 41000,
                                        'n_d_s': 20,
                                        'tax_system_code': 1,
                                    },
                                    'weight_net': 0,
                                    'count': 1,
                                    'non_physical_item': False,
                                    'description': '',
                                    'weight_gross': 0,
                                    'weight_tare': 0,
                                    'physical_dims': {
                                        'weight_tare': 0,
                                        'd_y': 0,
                                        'd_x': 0,
                                        'weight_gross': 0,
                                        'd_z': 0,
                                        'weight_net': 0,
                                    },
                                },
                                {
                                    'marking_code': '',
                                    'barcode': '',
                                    'd_x': 0,
                                    'assessed_unit_price': 20000,
                                    'article': '003',
                                    'd_z': 0,
                                    'd_y': 0,
                                    'name': 'Услуги по организации доставки',
                                    'billing_details': {
                                        'refundable': True,
                                        'i_n_n': '7705739450',
                                        'currency': 'RUB',
                                        'assessed_unit_price': 20000,
                                        'n_d_s': 20,
                                        'tax_system_code': 1,
                                    },
                                    'weight_net': 0,
                                    'count': 1,
                                    'non_physical_item': False,
                                    'description': '',
                                    'weight_gross': 0,
                                    'weight_tare': 0,
                                    'physical_dims': {
                                        'weight_tare': 0,
                                        'd_y': 0,
                                        'd_x': 0,
                                        'weight_gross': 0,
                                        'd_z': 0,
                                        'weight_net': 0,
                                    },
                                },
                            ],
                            'd_z': 300,
                            'd_y': 300,
                            'description': '',
                            'weight': 1992,
                            'physical_dims': {
                                'weight_tare': 0,
                                'd_y': 300,
                                'd_x': 300,
                                'weight_gross': 1992,
                                'd_z': 300,
                                'weight_net': 0,
                            },
                        },
                    },
                ],
            },
            'status': 'returned',
        },
    }


def get_default_calc_offer_request():
    return {
        'idempotency_token': 'token',
        'employer_id': 'a82624ff-303a-4242-bf93-cceb31869bc1',
        'delivery_status': 'returned',
        'delivery_policy': 'interval_with_fees',
        'items': [
            {
                'billing_details': {
                    'refundable': True,
                    'i_n_n': '7705739450',
                    'currency': 'RUB',
                    'assessed_unit_price': 200000,
                    'n_d_s': 20,
                    'tax_system_code': 1,
                },
                'count': 1,
            },
            {
                'billing_details': {
                    'refundable': True,
                    'i_n_n': '7705739450',
                    'currency': 'RUB',
                    'assessed_unit_price': 41000,
                    'n_d_s': 20,
                    'tax_system_code': 1,
                },
                'count': 1,
            },
            {
                'billing_details': {
                    'refundable': True,
                    'i_n_n': '7705739450',
                    'currency': 'RUB',
                    'assessed_unit_price': 20000,
                    'n_d_s': 20,
                    'tax_system_code': 1,
                },
                'count': 3,
            },
        ],
        'cargo_physical_dims': {
            'weight_tare': 0,
            'd_y': 300,
            'd_x': 300,
            'weight_gross': 1992,
            'd_z': 300,
            'weight_net': 0,
        },
        'waypoints': [[37, 55], [37.597414, 55.739554]],
    }


def get_default_tariff_composition():
    return {
        'composition_id': 'cargo-tariffs/v1/any_id',
        'tariff': {
            'type': 'ndd_client_base_prices',
            'delivery': {'intake': '100', 'return_price_pct': '10'},
            'parcels': {
                'add_declared_value_pct': '5',
                'included_weight_price': '17',
                'weight_prices': [{'begin': '2', 'price_per_kilogram': '7'}],
            },
        },
        'composer_process': {'tariff_nodes': ['some_id_1/1', 'some_id_2/1']},
    }
