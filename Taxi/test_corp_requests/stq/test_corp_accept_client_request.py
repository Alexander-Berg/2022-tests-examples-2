# pylint: disable=redefined-outer-name
# pylint: disable=too-many-locals
import datetime

import pytest

from corp_requests import consts
from corp_requests.stq import corp_accept_client_request


NOW = datetime.datetime.now().replace(microsecond=0)

DEFAULT_FEATURES = ['api_allowed', 'combo_orders_allowed', 'new_limits']
WITHOUT_VAT_FEATURES = ['new_limits']
CORP_FEATURE_SETTINGS = [
    {
        'country': 'rus',
        'feature_groups': [
            {
                'name': '__default__',
                'features': [
                    {'name': 'api_allowed'},
                    {'name': 'combo_orders_allowed'},
                    {'name': 'new_limits'},
                ],
            },
            {'name': 'without_vat', 'features': [{'name': 'new_limits'}]},
        ],
    },
    {
        'country': 'blr',
        'feature_groups': [
            {
                'name': '__default__',
                'features': [
                    {'name': 'api_allowed'},
                    {'name': 'combo_orders_allowed'},
                    {'name': 'new_limits'},
                ],
            },
        ],
    },
    {
        'country': 'kaz',
        'feature_groups': [
            {
                'name': '__default__',
                'features': [
                    {'name': 'api_allowed'},
                    {'name': 'combo_orders_allowed'},
                    {'name': 'new_limits'},
                ],
            },
        ],
    },
    {
        'country': 'kgz',
        'feature_groups': [
            {
                'name': '__default__',
                'features': [
                    {'name': 'api_allowed'},
                    {'name': 'combo_orders_allowed'},
                    {'name': 'new_limits'},
                ],
            },
        ],
    },
    {
        'country': 'isr',
        'feature_groups': [
            {
                'name': '__default__',
                'features': [
                    {'name': 'api_allowed'},
                    {'name': 'combo_orders_allowed'},
                    {'name': 'new_limits'},
                ],
            },
        ],
    },
]


@pytest.mark.parametrize(
    [
        'request_id',
        'request_patch',
        'expected_billing_data',
        'expected_corp_clients_update',
    ],
    [
        pytest.param(
            'trial_client_offer',
            {'services': ['cargo']},
            [
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 130,
                    'link_contract_id': None,
                    'manager_uid': 123456789,
                    'offer_activation_due_term': 30,
                    'offer_activation_payment_amount': '1000.00',
                    'offer_confirmation_type': 'min-payment',
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [718, 1040],
                },
            ],
            {
                'billing_name': 'Тр Сп',
                'is_trial': False,
                'without_vat_contract': False,
                'features': DEFAULT_FEATURES,
            },
            id='cargo-offer',
        ),
        pytest.param(
            'trial_client_offer',
            {'contract_type': 'taxi', 'services': ['taxi']},
            [
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 13,
                    'link_contract_id': None,
                    'manager_uid': 123456789,
                    'offer_activation_due_term': 30,
                    'offer_activation_payment_amount': '1000.00',
                    'offer_confirmation_type': 'min-payment',
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [650],
                },
            ],
            {
                'billing_name': 'Тр Сп',
                'is_trial': False,
                'without_vat_contract': False,
                'features': DEFAULT_FEATURES,
            },
            id='taxi-offer',
        ),
        pytest.param(
            'trial_client_offer',
            {'contract_type': 'taxi', 'country': 'isr', 'services': ['taxi']},
            [
                {
                    'client_id': 'BILLING_ID',
                    'country': 181,
                    'currency': 'ILS',
                    'firm_id': 1090,
                    'link_contract_id': None,
                    'manager_uid': 123456789,
                    'offer_confirmation_type': 'no',
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 181,
                    'services': [650],
                },
            ],
            {
                'billing_name': 'Тр Сп',
                'is_trial': False,
                'without_vat_contract': False,
                'features': DEFAULT_FEATURES,
            },
            id='taxi-offer-isr',
        ),
        pytest.param(
            'trial_client_offer',
            {
                'contract_type': 'multi',
                'services': ['taxi', 'eats2', 'drive', 'tanker'],
            },
            [
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 124,
                    'manager_uid': 123456789,
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [636],
                },
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 13,
                    'link_contract_id': 'TANKER_CONTRACT_ID',
                    'manager_uid': 123456789,
                    'offer_activation_due_term': 30,
                    'offer_activation_payment_amount': '1000.00',
                    'offer_confirmation_type': 'min-payment',
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [650, 672, 668, 1171],
                },
            ],
            {
                'billing_name': 'Тр Сп',
                'is_trial': False,
                'without_vat_contract': False,
                'features': DEFAULT_FEATURES,
            },
            id='multi-offer',
        ),
        pytest.param(
            'trial_client_offer',
            {
                'contract_type': 'multi_tanker',
                'services': ['taxi', 'eats2', 'drive', 'tanker'],
            },
            [
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 124,
                    'manager_uid': 123456789,
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [636],
                },
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 13,
                    'link_contract_id': 'TANKER_CONTRACT_ID',
                    'manager_uid': 123456789,
                    'offer_activation_due_term': 30,
                    'offer_activation_payment_amount': '1000.00',
                    'offer_confirmation_type': 'min-payment',
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [650, 672, 668, 1171],
                },
            ],
            {
                'billing_name': 'Тр Сп',
                'is_trial': False,
                'without_vat_contract': False,
                'features': DEFAULT_FEATURES,
            },
            id='multi-tanker-offer',
        ),
        pytest.param(
            'trial_client_offer',
            {
                'contract_type': 'multi_without_tanker',
                'services': ['taxi', 'eats2', 'drive'],
            },
            [
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 13,
                    'link_contract_id': None,
                    'manager_uid': 123456789,
                    'offer_activation_due_term': 30,
                    'offer_activation_payment_amount': '1000.00',
                    'offer_confirmation_type': 'min-payment',
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [650, 672, 668],
                },
            ],
            {
                'billing_name': 'Тр Сп',
                'is_trial': False,
                'without_vat_contract': False,
                'features': DEFAULT_FEATURES,
            },
            id='multi-without-tanker-offer',
        ),
        pytest.param(
            'trial_client_offer',
            {'contract_type': 'without_vat', 'services': ['taxi']},
            [
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 13,
                    'link_contract_id': None,
                    'manager_uid': 123456789,
                    'offer_activation_due_term': 30,
                    'offer_activation_payment_amount': '1000.00',
                    'offer_confirmation_type': 'min-payment',
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [1181, 1183],
                },
            ],
            {
                'billing_name': 'Тр Сп',
                'is_trial': False,
                'without_vat_contract': True,
                'features': WITHOUT_VAT_FEATURES,
            },
            id='without_vat',
        ),
        pytest.param(
            'kgz_client_offer',
            {'contract_type': 'taxi', 'services': ['taxi']},
            [
                {
                    'client_id': 'BILLING_ID',
                    'country': 207,
                    'currency': 'KGS',
                    'firm_id': 1100,
                    'link_contract_id': None,
                    'manager_uid': 123456789,
                    'offer_activation_due_term': 30,
                    'offer_activation_payment_amount': '1000.00',
                    'offer_confirmation_type': 'min-payment',
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 207,
                    'services': [650],
                },
            ],
            {
                'billing_name': 'Тр Сп KGZ',
                'is_trial': False,
                'without_vat_contract': False,
                'features': DEFAULT_FEATURES,
            },
            id='kgz request',
        ),
        pytest.param(
            'trial_client_offer',
            {
                'contract_type': 'multi_market',
                'services': ['taxi', 'eats2', 'drive', 'market'],
                'edo': {'organization': 'market', 'operator': 'diadoc'},
            },
            [
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 111,
                    'manager_uid': 123456789,
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [1173],
                },
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 13,
                    'link_contract_id': None,
                    'manager_uid': 123456789,
                    'offer_activation_due_term': 30,
                    'offer_activation_payment_amount': '1000.00',
                    'offer_confirmation_type': 'min-payment',
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [650, 672, 668],
                },
            ],
            {
                'billing_name': 'Тр Сп',
                'is_trial': False,
                'without_vat_contract': False,
                'features': DEFAULT_FEATURES,
            },
            id='multi-market-offer',
        ),
        pytest.param(
            'trial_client_offer',
            {
                'contract_type': 'multi_market',
                'services': ['taxi', 'eats2', 'drive', 'market'],
                'edo': {'organization': 'market', 'operator': 'diadoc'},
            },
            [
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 111,
                    'manager_uid': 123456789,
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [1173],
                },
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 1932,
                    'external_id': 'EXTERNAL_ID',
                    'manager_uid': 123456789,
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [1173],
                },
                {
                    'client_id': 'BILLING_ID',
                    'country': 225,
                    'currency': 'RUB',
                    'firm_id': 13,
                    'link_contract_id': None,
                    'manager_uid': 123456789,
                    'offer_activation_due_term': 30,
                    'offer_activation_payment_amount': '1000.00',
                    'offer_confirmation_type': 'min-payment',
                    'payment_type': 2,
                    'person_id': 'PERSON_ID',
                    'region': 225,
                    'services': [650, 672, 668],
                },
            ],
            {
                'billing_name': 'Тр Сп',
                'is_trial': False,
                'without_vat_contract': False,
                'features': DEFAULT_FEATURES,
            },
            marks=pytest.mark.config(CORP_MARKET_3P_CONTRACTS_ENABLED=True),
            id='multi-market-offer-with-3p',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'taxi-corp-admin', 'src': 'corp-requests'},
        {'dst': 'personal', 'src': 'corp-requests'},
    ],
    CORP_OFFER_BALANCE_MANAGER_UIDS={
        'rus': {'__default__': [123456789]},
        'isr': {'__default__': [123456789]},
        'kgz': {'__default__': [123456789]},
    },
    CORP_OFFER_ACCEPT_TERMS={
        'isr': {'offer_confirmation_type': 'no'},
        'rus': {
            'offer_activation_due_term': 30,
            'offer_activation_payment_amount': '1000.00',
            'offer_confirmation_type': 'min-payment',
        },
        'kgz': {
            'offer_activation_due_term': 30,
            'offer_activation_payment_amount': '1000.00',
            'offer_confirmation_type': 'min-payment',
        },
    },
    CORP_FEATURES_SETTINGS=CORP_FEATURE_SETTINGS,
)
async def test_clientrequests_accept(
        mockserver,
        patch,
        db,
        stq3_context,
        stq,
        mock_personal,
        mock_corp_clients,
        request_id,
        request_patch,
        expected_billing_data,
        expected_corp_clients_update,
        get_stats_by_label_values,
):
    @mockserver.json_handler('/corp-clients/v1/clients')
    def _client_handler(request):
        if request.method == 'PATCH':
            return {}
        if request.method == 'GET':
            return {'id': request.query['client_id'], 'features': []}
        return {}

    @patch('taxi.clients.billing_v2.BalanceClient.create_client')
    async def _create_client(*args, **kwargs):
        return 'BILLING_ID'

    @patch('taxi.clients.billing_v2.BalanceClient.get_passport_by_login')
    async def _get_passport_by_login(*args, **kwargs):
        return {'Uid': 'PASSPORT_UID'}

    @patch(
        'taxi.clients.billing_v2.BalanceClient.create_user_client_association',
    )
    async def _create_user_client_association(*args, **kwargs):
        pass

    @patch('taxi.clients.billing_v2.BalanceClient.create_person')
    async def _create_person(*args, **kwargs):
        return 'PERSON_ID'

    @patch('taxi.clients.billing_v2.BalanceClient.create_offer')
    async def _create_offer(*args, **kwargs):
        if consts.ServiceIds.TANKER.value in kwargs['services']:
            return {'EXTERNAL_ID': 'EXTERNAL_ID', 'ID': 'TANKER_CONTRACT_ID'}

        if consts.ServiceIds.TANKER_CC.value in kwargs['services']:
            assert kwargs['link_contract_id'] == 'TANKER_CONTRACT_ID'
        return {'EXTERNAL_ID': 'EXTERNAL_ID', 'ID': 'CONTRACT_ID'}

    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def _client_contracts(*args, **kwargs):
        return []

    client_request = await db.corp_client_requests.find_one(
        {'_id': request_id},
    )
    client_request.update(request_patch)
    await db.corp_client_requests.replace_one(
        {'_id': request_id}, client_request,
    )

    client_request['country_id'] = 0
    client_request['region_id'] = 0
    await corp_accept_client_request.task(
        stq3_context,
        client_request,
        status='accepted',
        operator_uid='0',
        locale='ru',
        x_remote_ip='remote_ip',
    )
    service_handle_mapping = {
        'taxi': mock_corp_clients.service_taxi,
        'cargo': mock_corp_clients.service_cargo,
        'drive': mock_corp_clients.service_drive,
        'eats2': mock_corp_clients.service_eats2,
        'tanker': mock_corp_clients.service_tanker,
        'market': mock_corp_clients.service_market,
    }

    for service in client_request.get('services'):
        if service != 'cargo':
            assert service_handle_mapping[service].next_call()[
                'request'
            ].json == {'is_active': True, 'is_visible': True}
        assert not service_handle_mapping[service].has_calls

    _create_offer_calls = [call['kwargs'] for call in _create_offer.calls]
    assert len(_create_offer_calls) == len(expected_billing_data)
    assert _create_offer_calls == expected_billing_data

    assert _client_handler.times_called == 2
    client_update_request = _client_handler.next_call()['request']
    assert client_update_request.query == {
        'client_id': client_request['client_id'],
        'fields': 'features',
    }
    client_update_request = _client_handler.next_call()['request']
    assert client_update_request.query == {
        'client_id': client_request['client_id'],
    }
    assert client_update_request.json == expected_corp_clients_update

    if request_patch.get('contract_type') in ('multi', 'cargo'):
        assert (
            stq.logistic_platform_processing_employer_create.times_called == 1
        )

    if request_patch.get('contract_type') not in ['multi_market']:
        assert stq.corp_registration_notices_tmp.times_called == 1
        assert stq.corp_registration_notices_tmp.next_call()['kwargs'] == {
            'client_id': client_request['client_id'],
        }

        assert stq.corp_notices_process_event.times_called == 1
        assert stq.corp_notices_process_event.next_call()['kwargs'] == {
            'event_name': 'ClientRequestStatusChanged',
            'data': {
                'request_id': client_request['_id'],
                'old': {'status': 'pending'},
                'new': {'status': 'accepted'},
            },
        }

    stats = get_stats_by_label_values(
        stq3_context, {'sensor': 'offer_contract_type'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'sensor': 'offer_contract_type',
                'contract_type': client_request['contract_type'],
            },
            'value': 1,
            'timestamp': None,
        },
    ]

    if client_request.get('edo'):
        assert stq.corp_send_edo_invite.times_called == 1
        assert stq.corp_send_edo_invite.next_call()['kwargs'] == {
            'client_id': 'trial',
            'operator': 'diadoc',
            'organization': 'market',
            'passport_login': 'l1tsolaiki',
        }

    assert stq.corp_sync_client_info.times_called == 1
    assert stq.corp_sync_client_info.next_call()['kwargs'] == {
        'client_id': client_request.get('client_id'),
        'billing_client_id': 'BILLING_ID',
    }
    assert stq.corp_sync_contracts_info.times_called == 1
    assert stq.corp_sync_contracts_info.next_call()['kwargs'] == {
        'client_id': client_request.get('client_id'),
        'billing_client_id': 'BILLING_ID',
    }
