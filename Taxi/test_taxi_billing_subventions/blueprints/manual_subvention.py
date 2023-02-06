def test_case(attrs):
    amount = attrs['amount']
    amount_by_reason = attrs['amount_by_reason']
    amount_by_reason_with_currency = attrs['amount_by_reason_with_currency']
    subventions_input_value = attrs['subventions_input_value']
    rule_details = attrs['rule_details']
    expected_docs_updated_events = attrs['expected_docs_updated_events']
    expected_created_order_docs = attrs['expected_created_order_docs']
    taximeter_driver_id = (
        'taximeter_driver_id/e414001e44434a00a93b65cc49548d5e/'
        '7bc343fc873a49159483e487663ba761'
    )
    external_event_ref = (
        'manual_subvention/1000/subventions_input_enrichment_needed'
    )
    return {
        'doc': {
            'data': {
                'alias_id': 'some_alias_id',
                'billing_contract': {
                    'acquiring_percent': '0',
                    'currency': 'RUB',
                    'currency_rate': '1',
                    'donate_multiplier': '1',
                    'ind_bel_nds_percent': None,
                    'offer_currency': 'RUB',
                    'offer_currency_rate': '1',
                    'rebate_percent': '0',
                    'subventions_hold_delay': 99999,
                },
                'billing_contract_is_set': True,
                'order_id': 'some_order_id',
                'performer': {
                    'db_id': 'e414001e44434a00a93b65cc49548d5e',
                    'driver_uuid': '7bc343fc873a49159483e487663ba761',
                },
                'subvention': {
                    'amount': amount,
                    'amount_by_reason': amount_by_reason,
                    'currency': 'RUB',
                },
                'version': 2,
            },
            'doc_id': 1000,
            'event_at': '2018-11-16T13:00:00+00:00',
            'external_event_ref': 'taxi/manual_subvention/some_alias_id/2',
            'external_obj_id': 'taxi/manual_subvention/some_alias_id',
            'kind': 'manual_subvention',
            'service': 'billing-orders',
            'status': 'new',
        },
        'existing_docs': [
            {
                'data': {'version': 1},
                'doc_id': 111,
                'event_at': '2018-11-15T12:00:00+00:00',
                'external_event_ref': (
                    'taxi/manual_subvention/some_alias_id/1/subvention_handled'
                ),
                'external_obj_id': (
                    'taxi/manual_subvention/some_alias_id/journal'
                ),
                'journal_entries': [
                    {
                        'account': {'account_id': 0},
                        'amount': '100',
                        'details': {
                            'amount_by_reason': {'dryclean': '100 RUB'},
                        },
                        'entry_id': 0,
                        'event_at': '2018-11-15T12:00:00.000000+00:00',
                    },
                    {
                        'account': {'account_id': 1},
                        'amount': '100',
                        'details': {
                            'amount_by_reason': {'dryclean': '100 RUB'},
                        },
                        'entry_id': 1,
                        'event_at': '2018-11-15T12:00:00.000000+00:00',
                    },
                ],
                'kind': 'subvention_journal',
                'service': 'billing-subventions',
                'status': 'new',
            },
            {
                'data': {
                    'context': {
                        'antifraud_config': {
                            'min_travel_distance': 0,
                            'min_travel_time': 0,
                        },
                        'based_on_doc_id': 1000,
                        'driver_promocode_config': {
                            'enabled': True,
                            'min_commission': '1 RUB',
                        },
                        'hold_config': {'delay': 0},
                    },
                    'order': {
                        'accepted_by_driver_at': (
                            '2018-07-02T00:30:00.750000+00:00'
                        ),
                        'billing_at': '2018-07-02T00:30:00.750000+00:00',
                        'alias_id': 'some_alias_id',
                        'closed_without_accept': False,
                        'completed_at': '2018-07-02T00:40:00.750000+00:00',
                        'completed_by_dispatcher': False,
                        'cost': '2 RUB',
                        'cost_details': {
                            'call_center_commission': '0.0000 RUB',
                            'cost_for_commission': '2 RUB',
                            'cost_for_subvention': '2 RUB',
                            'discount_details': {
                                'amendments': [],
                                'discount': '5 RUB',
                            },
                        },
                        'discount': {'method': 'time-dist', 'rate': '0'},
                        'driver_workshift_ids': [],
                        'due': '2018-07-02T00:00:00.750000+00:00',
                        'id': 'some_order_id',
                        'park': {'brandings': []},
                        'park_corp_vat': None,
                        'park_ride_sum': '0 RUB',
                        'payment_type': 'cash',
                        'performer': {
                            'activity_points': 0,
                            'db_id': 'db_id',
                            'driver_license': 'AXH903VV',
                            'has_co_branding': True,
                            'has_lightbox': False,
                            'has_sticker': False,
                            'park_id': 'clid',
                            'tags': ['some_tag'],
                            'unique_driver_id': '0123456789ab0123456789ab',
                            'uuid': 'uuid',
                            'zone': 'driver_zone',
                        },
                        'rebate_rate': '0',
                        'source': 'call_center',
                        'status': 'finished',
                        'subvention_geoareas': ['moscow'],
                        'tariff': {
                            'class_': 'econom',
                            'minimal_cost': '0 RUB',
                            'modified_minimal_cost': '0 RUB',
                        },
                        'taxi_status': 'complete',
                        'travel_distance': 123.0,
                        'travel_time': 60.0,
                        'tzinfo': 'Europe/Moscow',
                        'updated': '2018-07-02T00:40:00.750000+00:00',
                        'zone_name': 'moscow',
                    },
                },
                'doc_id': 12345678,
                'event_at': '2018-07-02T00:40:00.750000+00:00',
                'external_event_ref': 'order_ready_for_billing',
                'external_obj_id': 'alias_id/some_alias_id',
                'journal_entries': [],
                'kind': 'order_ready_for_billing',
                'service': 'taxi-billing-subventions',
                'status': 'new',
            },
        ],
        'replication_contracts': [
            {
                'CONTRACT_TYPE': 9,
                'COUNTRY': 123,
                'CURRENCY': 'USD',
                'DT': '2019-10-01 00:00:00',
                'END_DT': None,
                'EXTERNAL_ID': 'GEN/123456',
                'FINISH_DT': None,
                'ID': 123456,
                'IND_BEL_NDS': None,
                'IND_BEL_NDS_PERCENT': None,
                'IS_ACTIVE': 1,
                'IS_CANCELLED': 0,
                'IS_DEACTIVATED': None,
                'IS_FAXED': 1,
                'IS_SIGNED': 1,
                'IS_SUSPENDED': 0,
                'LINK_CONTRACT_ID': None,
                'NDS': 0,
                'NDS_FOR_RECEIPT': None,
                'NETTING': None,
                'NETTING_PCT': None,
                'OFFER_ACCEPTED': None,
                'PARTNER_COMMISSION_PCT': '5',
                'PARTNER_COMMISSION_PCT2': None,
                'PAYMENT_TYPE': None,
                'PERSON_ID': 8486204,
                'SERVICES': [111, 128],
            },
            {
                'CONTRACT_TYPE': 87,
                'COUNTRY': 123,
                'CURRENCY': 'USD',
                'DT': '2019-10-01 00:00:00',
                'END_DT': None,
                'EXTERNAL_ID': 'SPEND/123456',
                'FINISH_DT': None,
                'ID': 123457,
                'IND_BEL_NDS': None,
                'IND_BEL_NDS_PERCENT': None,
                'IS_ACTIVE': 1,
                'IS_CANCELLED': 0,
                'IS_DEACTIVATED': None,
                'IS_FAXED': 1,
                'IS_SIGNED': 1,
                'IS_SUSPENDED': 0,
                'LINK_CONTRACT_ID': 123456,
                'NDS': 0,
                'NDS_FOR_RECEIPT': None,
                'NETTING': None,
                'NETTING_PCT': None,
                'OFFER_ACCEPTED': None,
                'PARTNER_COMMISSION_PCT': '5',
                'PARTNER_COMMISSION_PCT2': None,
                'PAYMENT_TYPE': None,
                'PERSON_ID': 8486204,
                'SERVICES': [651, 137],
            },
        ],
        'expected_accounts': [
            {
                'account_id': 0,
                'agreement_id': 'dry/migration/taxi/driver_balance',
                'currency': 'RUB',
                'entity_external_id': taximeter_driver_id,
                'expired': '9999-12-31T23:59:59.999999+00:00',
                'sub_account': 'dry/migration/subvention',
            },
            {
                'account_id': 1,
                'agreement_id': 'subvention_agreement/misc',
                'currency': 'RUB',
                'entity_external_id': taximeter_driver_id,
                'expired': '9999-12-31T23:59:59.999999+00:00',
                'sub_account': 'income',
            },
        ],
        'expected_created_docs': [
            {
                'data': {'reverse_doc_id': 111},
                'event_at': '2018-11-16T13:00:00.000000+00:00',
                'external_event_ref': (
                    'taxi/manual_subvention/some_alias_id/journal/1/reversal'
                ),
                'external_obj_id': (
                    'doc_reversal/taxi/manual_subvention/some_alias_id/journal'
                ),
                'journal_entries': [
                    {
                        'account_id': 0,
                        'amount': '-100',
                        'details': {
                            'amount_by_reason': {'dryclean': '100 RUB'},
                            'reverse_entry_id': 0,
                        },
                        'event_at': '2018-11-16T13:00:00.000000+00:00',
                    },
                    {
                        'account_id': 1,
                        'amount': '-100',
                        'details': {
                            'amount_by_reason': {'dryclean': '100 RUB'},
                            'reverse_entry_id': 1,
                        },
                        'event_at': '2018-11-16T13:00:00.000000+00:00',
                    },
                ],
                'kind': 'journal_reversal',
                'service': 'billing-subventions',
                'status': 'new',
                'tags': [
                    'system://parent_doc_id/1000',
                    'taxi/alias_id/some_alias_id',
                ],
            },
            {
                'data': {
                    'accepted_by_driver_at': (
                        '2018-07-02T00:30:00.750000+00:00'
                    ),
                    'activity_points': 0,
                    'base_doc_id': 1000,
                    'billing_client_id': 'billing_client_id',
                    'billing_v2_id': None,
                    'closed_without_accept': False,
                    'comment': None,
                    'completed_by_dispatcher': False,
                    'create_via_py2': False,
                    'currency_data': None,
                    'db_id': 'db_id',
                    'discount_details': {
                        'amendments': [],
                        'discount': '0 RUB',
                    },
                    'driver_license': 'AXH903VV',
                    'dry_mode': True,
                    'due': '2018-07-02T00:00:00.750000+00:00',
                    'force_hold': False,
                    'has_co_branding': True,
                    'has_lightbox': False,
                    'has_sticker': False,
                    'hold_config': {'delay': 0},
                    'order_alias_id': 'some_alias_id',
                    'order_completed_at': '2018-07-02T00:40:00.750000+00:00',
                    'order_id': 'some_order_id',
                    'order_payment_type': 'cash',
                    'park': None,
                    'park_id': 'clid',
                    'rule_details': rule_details,
                    'rule_group': 'manual',
                    'sub_commission': '0 RUB',
                    'subvention_geoareas': ['moscow'],
                    'tags': ['some_tag'],
                    'tariff_class': 'econom',
                    'unique_driver_id': '0123456789ab0123456789ab',
                    'unrealized_sub_commission': '0 RUB',
                    'uuid': 'uuid',
                    'value': subventions_input_value,
                    'zone_name': 'moscow',
                    'is_cargo': False,
                },
                'event_at': '2018-11-30T19:31:35.000000+00:00',
                'external_event_ref': external_event_ref,
                'external_obj_id': 'alias_id/some_alias_id',
                'journal_entries': [],
                'kind': 'subventions_input_enrichment_needed',
                'service': 'billing-subventions',
                'status': 'new',
            },
            {
                'data': {'version': 2},
                'event_at': '2018-11-30T19:31:35.000000+00:00',
                'external_event_ref': (
                    'taxi/manual_subvention/some_alias_id/2/subvention_handled'
                ),
                'external_obj_id': (
                    'taxi/manual_subvention/some_alias_id/journal'
                ),
                'journal_entries': [
                    {
                        'account_id': 0,
                        'amount': amount,
                        'details': {
                            'amount_by_reason': amount_by_reason_with_currency,
                        },
                        'event_at': '2018-11-30T19:31:35.000000+00:00',
                    },
                    {
                        'account_id': 1,
                        'amount': amount,
                        'details': {
                            'amount_by_reason': amount_by_reason_with_currency,
                        },
                        'event_at': '2018-11-30T19:31:35.000000+00:00',
                    },
                ],
                'kind': 'subvention_journal',
                'service': 'billing-subventions',
                'status': 'new',
                'tags': [
                    'system://parent_doc_id/1000',
                    'journal_ancestor_doc_id/1000',
                    'taxi/alias_id/some_alias_id',
                ],
            },
        ],
        'expected_created_orders_docs': expected_created_order_docs,
        'expected_entities': [
            {'external_id': taximeter_driver_id, 'kind': 'driver'},
        ],
        'expected_docs_updated_events': expected_docs_updated_events,
    }
