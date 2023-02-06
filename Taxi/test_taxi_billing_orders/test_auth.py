import pytest

from taxi import discovery

from taxi_billing_orders import config as orders_config

FORBIDDEN_RESPONSE = 403

ENTRY_TEMPLATES = [
    {
        'agreement_id': 'taxi/%',
        'entity_external_id': 'taximeter_driver_id/%/%',
        'sub_account': '%',
        'mappers': ['park_entry_mapper'],
        'actions': ['send_to_taximeter'],
        'applied_at': {
            'begin': '2020-09-20T12:00:00.00000+00:00',
            'end': '2099-01-01T00:00:00.00000+00:00',
        },
    },
]
ENTRIES_MAPPERS_AND_ACTIONS = {
    'actions': [{'name': 'send_to_taximeter', 'vars': {}}],
    'mappers': [
        {
            'name': 'park_entry_mapper',
            'vars': {
                'alias_id': 'context.alias_id',
                'driver_uuid': 'context.driver.driver_uuid',
            },
        },
    ],
}
GROUPS_RULES = {
    'full_access_group': {
        'accounts': [{'kind': '%', 'agreement': '%'}],
        'documents': [{'external_obj_id': '%'}],
        'tags': [{'tag': '%'}],
        'payments': [{'payment_kind': '%'}],
    },
    'valid_access_group': {
        'accounts': [
            {'kind': 'driver', 'agreement': 'taxi/%'},
            {'kind': 'park', 'agreement': 'taxi/%'},
            {'kind': 'corp_client', 'agreement': 'claim/%'},
            {'kind': 'park', 'agreement': 'acquisition/%'},
            {'kind': 'wallet', 'agreement': 'wallet/yandex%'},
        ],
        'documents': [
            {'external_obj_id': 'taxi/manual_transactions/%'},
            {'external_obj_id': 'topic'},
            {'external_obj_id': 'taxi/b2b_client_payment/%'},
            {'external_obj_id': 'taxi/b2b_trip_payment/%'},
            {'external_obj_id': 'taxi/b2b_partner_payment/%'},
            {'external_obj_id': 'cargo/claim_id/%'},
            {'external_obj_id': 'cargo/order_id/%'},
            {'external_obj_id': 'cashback/%'},
            {'external_obj_id': 'taxi/payout/driver_fix/%'},
            {'external_obj_id': 'alias_id/ref/%/driver_referral'},
            {'external_obj_id': 'taxi/partner_scoring/%'},
            {'external_obj_id': 'taxi/remittance_order/%'},
            {'external_obj_id': 'taxi/scout_payment/%'},
            {'external_obj_id': 'shuttle/order_id/%'},
            {'external_obj_id': 'taxi/partners/motivation_program/%'},
            {'external_obj_id': 'taxi/driver_mode_subscription/%'},
            {'external_obj_id': 'taxi/driver_partner/%'},
            {'external_obj_id': 'taxi/park_commission/%'},
            {'external_obj_id': 'taxi/commission/%'},
            {'external_obj_id': 'taxi/subvention/%'},
            {'external_obj_id': 'alias_id/%'},
            {'external_obj_id': 'taxi/driverfix/%'},
            {'external_obj_id': 'taxi/invoice_transaction_cleared/%'},
            {'external_obj_id': 'taxi/personal_wallet_charge/%'},
            {'external_obj_id': 'billing_wallet_create/%'},
            {'external_obj_id': 'billing_wallet_top_up/%'},
            {'external_obj_id': 'billing_wallet_withdraw/%'},
            {'external_obj_id': 'taxi/payment_order/%'},
        ],
        'tags': [{'tag': '%'}],
    },
    'restricted_access_group': {
        'accounts': [{'kind': 'test', 'agreement': 'test'}],
        'documents': [{'external_obj_id': 'test'}],
        'tags': [{'tag': 'test%'}],
    },
    'restricted_access_group_by_tags': {
        'accounts': [{'kind': '%', 'agreement': '%'}],
        'documents': [{'external_obj_id': '%'}],
        'tags': [{'tag': 'invalid_tag'}],
    },
    'restricted_access_to_payments_group': {
        'accounts': [{'kind': '%', 'agreement': '%'}],
        'documents': [{'external_obj_id': '%'}],
        'tags': [{'tag': '%'}],
        'payments': [{'payment_kind': 'not_restricted_kind'}],
    },
    'valid_access_to_payments_group': {
        'accounts': [{'kind': '%', 'agreement': '%'}],
        'documents': [{'external_obj_id': '%'}],
        'tags': [{'tag': '%'}],
        'payments': [
            {'payment_kind': 'cargo_multi_park_b2b_trip_payment'},
            {'payment_kind': 'billing_wallet_top_up'},
            {'payment_kind': 'childseat'},
            {'payment_kind': 'driver_referrals'},
            {'payment_kind': 'partner_scoring'},
            {'payment_kind': 'coupon'},
            {'payment_kind': 'scout'},
            {'payment_kind': 'subvention'},
            {'payment_kind': 'commission'},
        ],
    },
}
SERVICE_GROUPS_FULL_ACCESS = {'billing_orders': ['full_access_group']}
SERVICE_GROUPS_VALID_ACCESS = {'billing_orders': ['valid_access_group']}
SERVICE_GROUPS_RESTRICTED_ACCESS = {
    'billing_orders': ['restricted_access_group'],
}
SERVICE_GROUPS_RESTRICTED_ACCESS_BY_TAGS = {
    'billing_orders': ['restricted_access_group_by_tags'],
}
SERVICE_GROUPS_WITH_PAYMENTS_VALID_ACCESS = {
    'billing_orders': ['valid_access_to_payments_group'],
}
SERVICE_GROUPS_WITH_PAYMENTS_RESTRICTED_ACCESS = {
    'billing_orders': ['restricted_access_to_payments_group'],
}


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
    BILLING_ARBITRARY_ENTRIES_TEMPLATES=ENTRY_TEMPLATES,
    BILLING_ARBITRARY_ENTRIES_MAPPERS_AND_ACTIONS=ENTRIES_MAPPERS_AND_ACTIONS,
    BILLING_AUTH_GROUPS_RULES=GROUPS_RULES,
    TVM_ENABLED=True,
)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'arbitrary_payout_v3.json',
        'arbitrary_entries_with_tags.json',
        'b2b_client_payment.json',
        'b2b_partner_payment.json',
        'cargo_claim.json',
        'cargo_order.json',
        'cashback.json',
        'childseat_v3.json',
        'driver_fix_docs.json',
        'driver_partner_raw_v2.json',
        'driver_referral_v3.json',
        'partner_scoring.json',
        'promocode.json',
        'remittance_order.json',
        'scout.json',
        'shuttle_order.json',
        'subvention_revoke_v3.json',
        'subvention_antifraud_check.json',
        'partners_payment.json',
        'partners_payment_wrong_amount.json',
        'park_commission.json',
        'personal_wallet_charge.json',
        'subvention_v3.json',
        'invoice_transaction_cleared.json',
        'commission_v3.json',
        'driver_partner_v1.json',
        'payment_order.json',
    ],
)
async def test_auth_process_v2(
        test_data_path,
        load_py_json_dir,
        request_headers,
        monkeypatch,
        response_mock,
        patch_aiohttp_session,
        patched_tvm_ticket_check,
        taxi_billing_orders_client,
):
    data = load_py_json_dir('test_v2_process_async', test_data_path)

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        doc = json.copy()
        doc['doc_id'] = 111111
        doc['created'] = doc['event_at']
        return response_mock(status=200, json=doc)

    @patch_aiohttp_session(
        discovery.find_service('billing_calculators').url, 'POST',
    )
    def _patch_billing_calculators_request(
            method, url, headers, json, **kwargs,
    ):
        return response_mock(json=json)

    # Test positive result with turned off Auth
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', False)

    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == data['response_status'], text

    # Test positive result with turned on Auth and full access
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', True)
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_FULL_ACCESS,
    )
    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == data['response_status'], text

    # Test positive result with turned on Auth and valid for this rules request
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_VALID_ACCESS,
    )
    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == data['response_status'], text

    # Test negative result with turned on Auth and non-valid request for rules
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_RESTRICTED_ACCESS,
    )
    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == FORBIDDEN_RESPONSE, text

    # Test negative result with turned on Auth and non-valid tags for rules
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_RESTRICTED_ACCESS_BY_TAGS,
    )
    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == (
        FORBIDDEN_RESPONSE
        if any(map(lambda x: x.get('tags', []), data['request']['orders']))
        else data['response_status']
    ), text

    # Tests for payments
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_WITH_PAYMENTS_VALID_ACCESS,
    )
    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == data['response_status'], text


@pytest.mark.config(
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
    BILLING_AUTH_GROUPS_RULES=GROUPS_RULES,
    TVM_ENABLED=True,
)
@pytest.mark.parametrize('test_data_path', ['commission_v3.json'])
async def test_auth_restrict_payments_process_v2(
        test_data_path,
        load_py_json_dir,
        request_headers,
        monkeypatch,
        response_mock,
        patched_tvm_ticket_check,
        taxi_billing_orders_client,
):
    data = load_py_json_dir('test_v2_process_async', test_data_path)
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', True)
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_WITH_PAYMENTS_RESTRICTED_ACCESS,
    )
    response = await taxi_billing_orders_client.post(
        '/v2/process/async', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == FORBIDDEN_RESPONSE, text


@pytest.mark.config(
    BILLING_AUTH_GROUPS_RULES=GROUPS_RULES,
    TVM_ENABLED=True,
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'subscribe_driver_fix.json',
        'subscribe_driver_fix_error_resp.json',
        'subscribe_orders.json',
        'subscribe_orders_with_settings.json',
        'billing_wallet/billing_wallet_create.json',
        'billing_wallet/billing_wallet_topup.json',
        'billing_wallet/billing_wallet_withdraw.json',
    ],
)
async def test_auth_execute_v1(
        test_data_path,
        load_py_json_dir,
        patch,
        request_headers,
        monkeypatch,
        patched_tvm_ticket_check,
        taxi_billing_orders_client,
        patch_aiohttp_session,
        response_mock,
):
    data = load_py_json_dir('test_execute', test_data_path)

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'v1/docs/create' in url:
            doc = json.copy()
            doc['doc_id'] = 111111
            doc['created'] = doc['event_at']
            doc['revision'] = 3254365
            doc['entry_ids'] = []
            return response_mock(status=200, json=doc)
        if 'v1/docs/search' in url:
            return response_mock(status=200, json={'docs': []})
        raise NotImplementedError

    @patch_aiohttp_session(
        discovery.find_service('billing_subventions').url, 'POST',
    )
    def _patch_billing_subventions_request(*args, **kwargs):
        subvention_response = data['subvention_response']
        return response_mock(
            status=subvention_response['status'],
            json=subvention_response['data'],
        )

    @patch_aiohttp_session(
        discovery.find_service('billing_calculators').url, 'POST',
    )
    def _patch_billing_calculators_request(
            method, url, headers, json, **kwargs,
    ):
        json['status'] = 'complete'
        json['data']['status_info'] = {'status': 'success'}
        return response_mock(json=json)

    # Test positive result with turned off Auth
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', False)

    response = await taxi_billing_orders_client.post(
        '/v1/execute', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == data['expected_response']['status'], text

    # Test positive result with turned on Auth and full access
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', True)
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_FULL_ACCESS,
    )
    response = await taxi_billing_orders_client.post(
        '/v1/execute', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == data['expected_response']['status'], text

    # Test positive result with turned on Auth and valid for this rules request
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_VALID_ACCESS,
    )
    response = await taxi_billing_orders_client.post(
        '/v1/execute', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == data['expected_response']['status'], text

    # Test negative result with turned on Auth and non-valid request for rules
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_RESTRICTED_ACCESS,
    )
    response = await taxi_billing_orders_client.post(
        '/v1/execute', headers=request_headers, json=data['request'],
    )
    text = await response.text()
    assert response.status == FORBIDDEN_RESPONSE, text
