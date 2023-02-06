from typing import List


def goal(attrs: dict) -> List[dict]:
    incomplete_fields = attrs.get('incomplete_fields', [])
    external_obj_id = (
        'taxi/shift_ended/subvention_agreement/1/default/group_id/'
        'goal_rule_group_id'
    )
    return [
        {
            'data': {
                'ancestor_doc_kind': 'shift_ended',
                'support_info': {
                    'data': {
                        'incomplete_fields': incomplete_fields,
                        'details': {'num_orders': []},
                        'last_shift_date': '2018-05-11',
                        'num_orders': 15,
                        'payout': {
                            'expenses': {
                                'calculations': [
                                    {
                                        'args': [
                                            {'amount': '0', 'currency': 'RUB'},
                                        ],
                                        'details': {},
                                        'op': 'set',
                                        'reason': 'set_from_commission',
                                        'value': {
                                            'amount': '0',
                                            'currency': 'RUB',
                                        },
                                    },
                                ],
                                'value': {'amount': '0', 'currency': 'RUB'},
                            },
                            'gross': {
                                'calculations': [
                                    {
                                        'args': [
                                            {
                                                'amount': '1000.0000',
                                                'currency': 'RUB',
                                            },
                                        ],
                                        'details': {},
                                        'op': 'set',
                                        'reason': 'set_from_bonus',
                                        'value': {
                                            'amount': '1000.0000',
                                            'currency': 'RUB',
                                        },
                                    },
                                ],
                                'value': {
                                    'amount': '1000.0000',
                                    'currency': 'RUB',
                                },
                            },
                            'net': {
                                'calculations': [
                                    {
                                        'args': [
                                            {
                                                'amount': '1000.0000',
                                                'currency': 'RUB',
                                            },
                                        ],
                                        'details': {},
                                        'op': 'set',
                                        'reason': (
                                            'set_from_bonus_commission_diff'
                                        ),
                                        'value': {
                                            'amount': '1000.0000',
                                            'currency': 'RUB',
                                        },
                                    },
                                ],
                                'value': {
                                    'amount': '1000.0000',
                                    'currency': 'RUB',
                                },
                            },
                        },
                        'rule': {'id': 'group_id/goal_rule_group_id'},
                        'unfit_details': {'num_orders': []},
                        'unfit_num_orders': 0,
                    },
                    'kind': 'taxi/v1/do_x_get_y',
                },
            },
            'event_at': '2018-05-12T05:00:00.000000+00:00',
            'external_event_ref': '2018-05-11/payment_subvention_handled',
            'external_obj_id': external_obj_id,
            'journal_entries': [
                {
                    'account_id': 0,
                    'amount': '1000',
                    'event_at': '2018-05-12T05:00:00.000000+00:00',
                },
                {
                    'account_id': 1,
                    'amount': '1000',
                    'event_at': '2018-05-12T05:00:00.000000+00:00',
                },
            ],
            'kind': 'payment_subvention_journal',
            'service': 'billing-subventions',
            'status': 'new',
            'tags': [
                'system://parent_doc_id/12345678',
                'journal_ancestor_doc_id/12345678',
            ],
        },
        {
            'data': {'ancestor_doc_kind': 'shift_ended'},
            'event_at': '2018-05-12T05:00:00.000000+00:00',
            'external_event_ref': '2018-05-11/subvention_handled',
            'external_obj_id': external_obj_id,
            'journal_entries': [],
            'kind': 'subvention_journal',
            'service': 'billing-subventions',
            'status': 'complete',
            'tags': [
                'system://parent_doc_id/12345678',
                'journal_ancestor_doc_id/12345678',
            ],
        },
    ]


def daily_guarantee(attrs: dict) -> List[dict]:
    incomplete_fields = attrs.get('incomplete_fields', [])
    external_obj_id = (
        'taxi/shift_ended/subvention_agreement/1/default/group_id/'
        'daily_guarantee_rule_group_id'
    )
    return [
        {
            'data': {
                'ancestor_doc_kind': 'shift_ended',
                'support_info': {
                    'data': {
                        'incomplete_fields': incomplete_fields,
                        'commission_multiplier': '1',
                        'details': {
                            'income': {
                                'expenses': [],
                                'gross': [
                                    {
                                        'alias_id': 'some_alias_id',
                                        'type': 'order',
                                        'value': {
                                            'amount': '500',
                                            'currency': 'RUB',
                                        },
                                    },
                                ],
                            },
                            'num_orders': [
                                {
                                    'alias_id': 'some_alias_id',
                                    'value': {
                                        'amount': '1',
                                        'currency': 'XXX',
                                    },
                                },
                            ],
                        },
                        'income': {
                            'expenses': {'amount': '0', 'currency': 'RUB'},
                            'gross': {'amount': '500', 'currency': 'RUB'},
                            'net': {'amount': '500', 'currency': 'RUB'},
                        },
                        'last_shift_date': '2018-05-11',
                        'num_orders': 16,
                        'num_orders_with_promocode': 0,
                        'num_orders_with_workshift': 0,
                        'payout': {
                            'expenses': {
                                'calculations': [
                                    {
                                        'args': [
                                            {'amount': '0', 'currency': 'RUB'},
                                        ],
                                        'details': {},
                                        'op': 'set',
                                        'reason': 'set_from_commission',
                                        'value': {
                                            'amount': '0',
                                            'currency': 'RUB',
                                        },
                                    },
                                ],
                                'value': {'amount': '0', 'currency': 'RUB'},
                            },
                            'gross': {
                                'calculations': [
                                    {
                                        'args': [
                                            {
                                                'amount': '1500.0000',
                                                'currency': 'RUB',
                                            },
                                        ],
                                        'details': {},
                                        'op': 'set',
                                        'reason': 'set_from_bonus',
                                        'value': {
                                            'amount': '1500.0000',
                                            'currency': 'RUB',
                                        },
                                    },
                                ],
                                'value': {
                                    'amount': '1500.0000',
                                    'currency': 'RUB',
                                },
                            },
                            'net': {
                                'calculations': [
                                    {
                                        'args': [
                                            {
                                                'amount': '1500.0000',
                                                'currency': 'RUB',
                                            },
                                        ],
                                        'details': {},
                                        'op': 'set',
                                        'reason': (
                                            'set_from_bonus_commission_diff'
                                        ),
                                        'value': {
                                            'amount': '1500.0000',
                                            'currency': 'RUB',
                                        },
                                    },
                                ],
                                'value': {
                                    'amount': '1500.0000',
                                    'currency': 'RUB',
                                },
                            },
                        },
                        'promocode_commission': {
                            'amount': '0',
                            'currency': 'RUB',
                        },
                        'rule': {
                            'id': 'group_id/daily_guarantee_rule_group_id',
                        },
                        'step': {
                            'guarantee': {'amount': '2000', 'currency': 'RUB'},
                            'num_orders': 2,
                        },
                        'unfit_details': {
                            'income': {'expenses': [], 'gross': []},
                            'num_orders': [],
                        },
                        'unfit_num_orders': 0,
                    },
                    'kind': 'taxi/v1/nmfg',
                },
            },
            'event_at': '2018-05-12T05:00:00.000000+00:00',
            'external_event_ref': '2018-05-11/payment_subvention_handled',
            'external_obj_id': external_obj_id,
            'journal_entries': [
                {
                    'account_id': 0,
                    'amount': '1500',
                    'event_at': '2018-05-12T05:00:00.000000+00:00',
                },
                {
                    'account_id': 1,
                    'amount': '1500',
                    'event_at': '2018-05-12T05:00:00.000000+00:00',
                },
            ],
            'kind': 'payment_subvention_journal',
            'service': 'billing-subventions',
            'status': 'new',
            'tags': [
                'system://parent_doc_id/12345678',
                'journal_ancestor_doc_id/12345678',
            ],
        },
        {
            'data': {'ancestor_doc_kind': 'shift_ended'},
            'event_at': '2018-05-12T05:00:00.000000+00:00',
            'external_event_ref': '2018-05-11/subvention_handled',
            'external_obj_id': external_obj_id,
            'journal_entries': [],
            'kind': 'subvention_journal',
            'service': 'billing-subventions',
            'status': 'complete',
            'tags': [
                'system://parent_doc_id/12345678',
                'journal_ancestor_doc_id/12345678',
            ],
        },
    ]
