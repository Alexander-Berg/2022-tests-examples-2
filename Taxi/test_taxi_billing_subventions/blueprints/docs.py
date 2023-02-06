def existing_docs_for_order_amended_test(attrs):
    # pylint: disable=invalid-name
    docs = [
        {
            'created': '2019-02-05T16:14:27.686809+00:00',
            'data': {
                'context': {
                    'antifraud_config': {
                        'min_travel_distance': 0,
                        'min_travel_time': 10,
                    },
                    'use_separate_journal_topic': True,
                },
                'order': {
                    'accepted_by_driver_at': (
                        '2019-02-05T16:11:21.170000+00:00'
                    ),
                    'alias_id': 'some_alias_id',
                    'closed_without_accept': False,
                    'completed_at': '2019-02-05T16:13:31.762000+00:00',
                    'completed_by_dispatcher': False,
                    'cost': '150.0 RUB',
                    'cost_details': {
                        'call_center_commission': '0 RUB',
                        'cost_for_commission': (
                            '211.2676056338028169014084507 RUB'
                        ),
                        'cost_for_subvention': (
                            '211.2676056338028169014084507 RUB'
                        ),
                        'discount_details': {
                            'amendments': [],
                            'discount': '61.26760563380281690140845070 RUB',
                        },
                    },
                    'discount': {'method': 'full', 'rate': '0.29'},
                    'driver_workshift_ids': [],
                    'due': '2019-02-05T16:16:00.000000+00:00',
                    'id': 'some_order_id',
                    'park': {'brandings': []},
                    'park_corp_vat': None,
                    'payment_type': 'cash',
                    'performer': {
                        'activity_points': 90.0,
                        'db_id': 'some_db_id',
                        'driver_license': 'some_driver_license',
                        'has_co_branding': False,
                        'has_lightbox': False,
                        'has_sticker': False,
                        'park_id': 'some_park_id',
                        'tags': [],
                        'unique_driver_id': '5afee214453b0a524e56d237',
                        'uuid': 'some_uuid',
                    },
                    'rebate_rate': '0',
                    'source': None,
                    'status': 'finished',
                    'subvention_geoareas': ['moscow', 'test_zone_1', 'modcow'],
                    'tariff': {
                        'class_': 'econom',
                        'minimal_cost': '101 RUB',
                        'modified_minimal_cost': '101 RUB',
                    },
                    'taxi_status': 'complete',
                    'travel_distance': 0,
                    'travel_time': 20.892,
                    'tzinfo': 'Europe/Moscow',
                    'updated': '2019-02-05T16:13:31.762000+00:00',
                    'zone_name': 'moscow',
                },
            },
            'doc_id': 99,
            'event_at': '2019-02-05T16:13:31.762000+00:00',
            'external_event_ref': 'order_ready_for_billing',
            'external_obj_id': 'alias_id/some_alias_id',
            'kind': 'order_ready_for_billing',
            'process_at': '2019-02-05T16:14:27.686809+00:00',
            'service': 'taxi-billing-subventions',
            'status': 'new',
            'tags': [],
        },
        {
            'doc_id': 123,
            'external_obj_id': (
                'taxi/order_ready_for_billing/journal/some_alias_id'
            ),
            'event_at': '2019-02-05T16:13:31.762000+00:00',
            'kind': 'subvention_journal',
            'data': {'ancestor_doc_kind': 'order_ready_for_billing'},
            'tags': ['journal_ancestor_doc_id/99'],
            'journal_entries': [
                {
                    'doc_id': 123,
                    'account': {
                        'account_id': -1,
                        'agreement_id': (
                            'subvention_agreement/1/default/group_id/'
                            'MSK_GRNT_GROUP_ID2'
                        ),
                        'entity_external_id': (
                            'unique_driver_id/5afee214453b0a524e56d237'
                        ),
                        'currency': 'RUB',
                        'sub_account': 'unfit/income',
                    },
                    'account_id': -1,
                    'entry_id': -11,
                    'amount': '130',
                    'event_at': '2019-02-05T16:16:00.000000+00:00',
                    'reason': (
                        'MatchReason(version=1, type=\'unfit/in\', '
                        'properties=Properties(code=\'tariff_class\', '
                        'details={\'value\': \'econom\', '
                        '\'allowed_values\': [\'vip\']}))'
                    ),
                    'journal_entry_id': None,
                    'details': None,
                },
                {
                    'doc_id': 123,
                    'account': {
                        'account_id': -2,
                        'agreement_id': (
                            'subvention_agreement/1/default/group_id/'
                            'MSK_GRNT_GROUP_ID2'
                        ),
                        'entity_external_id': (
                            'unique_driver_id/5afee214453b0a524e56d237'
                        ),
                        'currency': 'XXX',
                        'sub_account': 'unfit/num_orders',
                    },
                    'account_id': -2,
                    'entry_id': -21,
                    'amount': attrs.get('unfit_by_tariff_class_amount', '1'),
                    'event_at': '2019-02-05T16:16:00.000000+00:00',
                    'reason': (
                        'MatchReason(version=1, type=\'unfit/in\', '
                        'properties=Properties(code=\'tariff_class\', '
                        'details={\'value\': \'econom\', '
                        '\'allowed_values\': [\'vip\']}))'
                    ),
                    'journal_entry_id': None,
                    'details': None,
                },
                {
                    'doc_id': 123,
                    'account': {
                        'account_id': -3,
                        'agreement_id': (
                            'subvention_agreement/1/default/group_id'
                            '/MSK_GRNT_GROUP_ID2'
                        ),
                        'entity_external_id': (
                            'unique_driver_id/5afee214453b0a524e56d237'
                        ),
                        'currency': 'RUB',
                        'sub_account': 'unfit/some_account',
                    },
                    'account_id': -3,
                    'entry_id': -31,
                    'amount': '666',
                    'event_at': '2019-02-05T16:16:00.000000+00:00',
                    'reason': (
                        'MatchReason(version=1, type=\'unfit/in\', '
                        'properties=Properties(code=\'tariff_class\', '
                        'details={\'value\': \'econom\', \'allowed_values\': '
                        '[\'vip\']}))'
                    ),
                    'journal_entry_id': None,
                    'details': None,
                },
            ],
        },
        {
            'doc_id': 124,
            'external_obj_id': (
                'taxi/order_ready_for_billing/journal/some_alias_id'
            ),
            'event_at': '2019-02-05T16:13:31.762000+00:00',
            'kind': 'payment_subvention_journal',
            'tags': ['journal_ancestor_doc_id/99'],
            'journal_entries': [
                {
                    'account': {'account_id': 1111},
                    'account_id': 1111,
                    'entry_id': 11111,
                    'amount': '788.7324',
                    'event_at': '2019-02-05T16:13:31.762000+00:00',
                    'reason': (
                        'MatchReason(version=1, type=\'unfit/in\', '
                        'properties=Properties(code=\'tariff_class\', '
                        'details={\'value\': \'econom\', '
                        '\'allowed_values\': [\'vip\']}))'
                    ),
                    'details': None,
                },
            ],
        },
        {
            'doc_id': 125,
            'external_obj_id': (
                'taxi/order_ready_for_billing/journal/some_alias_id'
            ),
            'event_at': '2019-02-05T16:13:31.762000+00:00',
            'kind': 'commission_journal',
            'tags': ['journal_ancestor_doc_id/99'],
            'journal_entries': [
                {
                    'account': {'account_id': 1112},
                    'account_id': 1112,
                    'entry_id': 11121,
                    'amount': '0',
                    'event_at': '2019-02-05T16:13:31.762000+00:00',
                    'reason': '',
                    'details': None,
                },
            ],
        },
        {
            'doc_id': 126,
            'external_obj_id': (
                'taxi/order_ready_for_billing/journal/some_alias_id'
            ),
            'event_at': '2019-02-05T16:16:00.000000+00:00',
            'kind': 'driver_income_journal',
            'tags': ['journal_ancestor_doc_id/99'],
            'data': {'reversal_event_at': '2019-02-05T16:16:00.000000+00:00'},
            'journal_entries': [
                {
                    'account': {
                        'account_id': 1113,
                        'agreement_id': 'taxi/yandex_ride+0',
                    },
                    'account_id': 1113,
                    'entry_id': 11131,
                    'amount': '150.0',
                    'event_at': '2019-02-05T16:16:00.000000+00:00',
                    'reason': '',
                    'details': None,
                },
            ],
        },
    ]
    docs.extend(attrs.get('extra_docs', []))
    return docs


def created_docs_for_order_amended_test(attrs):
    # pylint: disable=invalid-name
    minimal_doc_reversal = {
        'data': {
            'reverse_doc_id': 123,
            'ancestor_doc_kind': 'order_ready_for_billing',
        },
        'event_at': '2019-02-07T15:00:00.000000+00:00',
        'external_event_ref': (
            'order_ready_for_billing/order_amended/'
            '2019-02-05T16:13:31.762000+00:00/123/minimal_reversal'
        ),
        'external_obj_id': (
            'taxi/order_ready_for_billing/journal/some_alias_id'
        ),
        'journal_entries': [
            {
                'account_id': -1,
                'amount': '-130',
                'event_at': '2019-02-05T16:16:00.000000+00:00',
                'details': {'reverse_entry_id': -11},
            },
            {
                'account_id': -3,
                'amount': '-666',
                'event_at': '2019-02-05T16:16:00.000000+00:00',
                'details': {'reverse_entry_id': -31},
            },
        ],
        'kind': 'minimal_doc_reversal',
        'service': 'billing-subventions',
        'status': 'new',
        'tags': ['system://parent_doc_id/100', 'taxi/alias_id/some_alias_id'],
    }
    if 'minimal_doc_reversal' in attrs:
        minimal_doc_reversal = attrs['minimal_doc_reversal']
    subvention_journal_extra_tags = attrs.get(
        'subvention_journal_extra_tags', [],
    )
    docs = [
        {
            'data': {'reverse_doc_id': 124},
            'event_at': '2019-02-07T15:00:00.000000+00:00',
            'external_event_ref': (
                'order_ready_for_billing/order_amended/'
                '2019-02-05T16:13:31.762000+00:00/124/reversal'
            ),
            'external_obj_id': (
                'taxi/order_ready_for_billing/journal/some_alias_id'
            ),
            'journal_entries': [
                {
                    'account_id': 1111,
                    'amount': '-788.7324',
                    'event_at': '2019-02-07T15:00:00.000000+00:00',
                    'details': {'reverse_entry_id': 11111},
                },
            ],
            'kind': 'journal_reversal',
            'service': 'billing-subventions',
            'status': 'new',
            'tags': [
                'system://parent_doc_id/100',
                'taxi/alias_id/some_alias_id',
            ],
        },
        {
            'data': {'reverse_doc_id': 125},
            'event_at': '2019-02-07T15:00:00.000000+00:00',
            'external_event_ref': (
                'order_ready_for_billing/order_amended/'
                '2019-02-05T16:13:31.762000+00:00/125/reversal'
            ),
            'external_obj_id': (
                'taxi/order_ready_for_billing/journal/some_alias_id'
            ),
            'journal_entries': [
                {
                    'account_id': 1112,
                    'amount': '0',
                    'event_at': '2019-02-07T15:00:00.000000+00:00',
                    'details': {'reverse_entry_id': 11121},
                },
            ],
            'kind': 'journal_reversal',
            'service': 'billing-subventions',
            'status': 'new',
            'tags': [
                'system://parent_doc_id/100',
                'taxi/alias_id/some_alias_id',
            ],
        },
        {
            'data': {'reverse_doc_id': 126},
            'event_at': '2019-02-05T16:16:00.000000+00:00',
            'external_event_ref': (
                'order_ready_for_billing/order_amended/'
                '2019-02-05T16:13:31.762000+00:00/126/reversal'
            ),
            'external_obj_id': (
                'taxi/order_ready_for_billing/journal/some_alias_id'
            ),
            'journal_entries': [
                {
                    'account_id': 1113,
                    'amount': '-150.0',
                    'event_at': '2019-02-05T16:16:00.000000+00:00',
                    'details': {'reverse_entry_id': 11131},
                },
            ],
            'kind': 'journal_reversal',
            'service': 'billing-subventions',
            'status': 'new',
            'tags': [
                'system://parent_doc_id/100',
                'taxi/alias_id/some_alias_id',
            ],
        },
        minimal_doc_reversal,
        {
            'data': {'ancestor_doc_kind': 'order_ready_for_billing'},
            'event_at': '2019-02-07T15:00:00.000000+00:00',
            'external_event_ref': (
                'order_ready_for_billing/100/subvention_handled'
            ),
            'external_obj_id': (
                'taxi/order_ready_for_billing/journal/some_alias_id'
            ),
            'journal_entries': [
                {
                    'account_id': 0,
                    'amount': '150',
                    'event_at': '2019-02-05T16:16:00.000000+00:00',
                    'reason': (
                        'MatchReason(version=1, type=\'unfit/in\', '
                        'properties=Properties(code=\'tariff_class\', '
                        'details={\'value\': \'econom\', '
                        '\'allowed_values\': [\'vip\']}))'
                    ),
                    'details': {
                        'alias_id': 'some_alias_id',
                        'income_type': 'order',
                    },
                },
                {
                    'account_id': 1,
                    'amount': '1000',
                    'event_at': '2019-02-05T16:16:00.000000+00:00',
                },
                {
                    'account_id': 2,
                    'amount': '61.2676',
                    'event_at': '2019-02-05T16:16:00.000000+00:00',
                },
            ],
            'kind': 'subvention_journal',
            'service': 'billing-subventions',
            'status': 'new',
            'tags': [
                'system://parent_doc_id/100',
                'taxi/alias_id/some_alias_id',
                'journal_ancestor_doc_id/100',
                *subvention_journal_extra_tags,
            ],
        },
    ]
    return docs


def rebill_order(attrs):
    zone_name = attrs.pop('var:zone_name', 'moscow')
    due = attrs.pop('var:due', '2019-08-24T00:00:00+00:00')
    defaults = {
        'kind': 'rebill_order',
        'external_obj_id': 'taxi/rebill_order/some_alias_id',
        'external_event_ref': 'updated/2019-08-29T00:00:00+00:00',
        'service': 'billing-orders',
        'data': {
            'order': {
                'id': 'some_order_id',
                'alias_id': 'some_alias_id',
                'version': 3,
                'zone_name': zone_name,
                'due': due,
            },
            'reason': {
                'kind': 'cost_changed',
                'data': {
                    'ticket_type': 'chatterbox',
                    'ticket_id': '5d7b9ced5b88ff53435a0813',
                },
            },
        },
        'status': 'new',
        'event_at': '2019-08-29T01:00:00+00:00',
        'journal_entries': [],
    }
    defaults.update(attrs)
    return defaults
