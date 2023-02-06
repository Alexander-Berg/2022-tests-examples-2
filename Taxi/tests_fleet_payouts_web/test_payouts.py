import pytest

ENDPOINT = '/fleet/fleet-payouts-web/v2/payouts'

HEADERS = {
    'Accept-Language': 'ru,en;q=0.9,la;q=0.8',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'yandex-user',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
}

ERRORS = [
    {
        'reject_code': 'N_CONTRACT_ORIGINAL_NOT_PRESENT',
        'tanker_key': 'error.contract_not_present',
    },
    {
        'reject_code': 'N_BANK_ACCOUNT_NOT_VALID',
        'tanker_key': 'error.invalid_bank_details',
    },
    {
        'reject_code': 'N_DOCUMENT_ORIGINAL_NOT_PRESENT',
        'tanker_key': 'error.document_not_present',
    },
]

CONTRACTS = [
    {
        'id': '0',
        'tanker_key': 'label_general_contract',
        'tanker_key_hint': 'label_general_contract_hint',
        'types': ['TAXI'],
    },
    {
        'id': '1',
        'tanker_key': 'label_marketing_contract',
        'tanker_key_hint': 'label_marketing_contract_hint',  # noqa: E501
        'types': ['PROMOCODES'],
    },
    {
        'id': '2',
        'tanker_key': 'label_corporate_contract',
        'tanker_key_hint': 'label_corporate_contract_hint',  # noqa: E501
        'types': ['CORPORATE'],
    },
    {
        'id': '3',
        'tanker_key': 'label_other_contract',
        'tanker_key_hint': 'label_other_contract_hint',
        'types': ['SCOUTS'],
    },
]

TRANSLATIONS_BACKEND = {
    'error.invalid_bank_details': {
        'ru': (
            'Ошибка в реквизитах. Проверьте поля ИНН, Расчётный счёт и БИК. '
            '%(service_name)s №%(contract_alias)s'
        ),
    },
    'error.contract_not_present': {
        'ru': (
            'Ошибка оплаты. Нет оригинала договора: '
            '%(service_name)s №%(contract_alias)s'
        ),
    },
    'error.document_not_present': {
        'ru': (
            'Ошибка оплаты. Нет документов за прошлые периоды: '
            '%(service_name)s №%(contract_alias)s'
        ),
    },
    'payout_error_current_prefix': {'ru': '(Действ)'},
    'default_contract': {'ru': 'Контракт'},
    'label_bank_details_taxi': {'ru': 'Реквизиты Такси'},
    'label_bank_details_delivery': {'ru': 'Реквизиты Доставка'},
    'label_bank_details': {'ru': 'Реквизиты'},
    'service_name_taxi': {'ru': 'Такси'},
    'service_name_delivery': {'ru': 'Доставка'},
}

TRANSLATIONS_OPTEUM = {
    'label_general_contract': {'ru': 'Договор на доступ к сервису'},
    'label_general_contract_hint': {
        'ru': 'Сумма всех доступных к перечислению остатков по договорам из категории «Основной контракт»',  # noqa: E501
    },
    'label_marketing_contract': {'ru': 'Маркетинговый договор'},
    'label_marketing_contract_hint': {
        'ru': 'Сумма всех доступных к перечислению остатков по договорам из категории «Маркетинговые услуги»',  # noqa: E501
    },
    'label_corporate_contract': {'ru': 'Договор на корпоративные поездки'},
    'label_corporate_contract_hint': {
        'ru': 'Сумма всех доступных к перечислению остатков по договорам из категории «Корпоративные поездки»',  # noqa: E501
    },
    'label_other_contract': {'ru': 'Прочее'},
    'label_other_contract_hint': {
        'ru': 'Сумма всех доступных к перечислению остатков по договорам из категории «Прочее»',  # noqa: E501
    },
}


@pytest.mark.parametrize(
    ('billing_replication', 'service_response'),
    [
        ('billing_replication_contract.json', 'service_response.json'),
        ('billing_replication_contract_common.json', 'service_response2.json'),
    ],
)
@pytest.mark.config(FLEET_PAYOUTS_WEB_CONTRACTS=CONTRACTS)
@pytest.mark.config(FLEET_PAYOUTS_WEB_CONTRACT_ERRORS=ERRORS)
@pytest.mark.translations(
    opteum_page_report_payouts_withdrawal=TRANSLATIONS_OPTEUM,
    backend_fleet_payouts_web=TRANSLATIONS_BACKEND,
)
async def test_success(
        taxi_fleet_payouts_web,
        mockserver,
        load_json,
        mock_fleet_parks_list,
        billing_replication,
        service_response,
):
    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _v1_parks_billing_client_id_retrieve(request):
        stub = load_json('parks_replica.json')
        assert request.query == stub['request']
        return stub['response']

    fleet_payouts = load_json('fleet_payouts.json')

    @mockserver.json_handler('/fleet-payouts/v1/parks/payouts/status')
    def _balances_valid(request):
        assert request.query == fleet_payouts['request']
        return fleet_payouts['response']

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _v1_parks_retrieve(request):
        stub = load_json('parks_replica_balances.json')
        assert request.query['consumer'] == stub['request']['consumer']
        assert request.json == stub['request']['body']
        return stub['response']

    @mockserver.json_handler('/billing-replication/contract/')
    def _contract(request):
        stub = load_json(billing_replication)
        assert request.query == stub['request']
        return stub['response']

    @mockserver.json_handler('/billing-replication/person/')
    def _person(request):
        stub = load_json('billing_replication_person.json')
        assert request.query == stub['request']
        return stub['response']

    @mockserver.json_handler('/parks-activation/v2/parks/activation/balances')
    def _balances(request):
        stub = load_json('parks_activation.json')
        assert request.query == stub['request']
        return stub['response']

    response = await taxi_fleet_payouts_web.get(ENDPOINT, headers=HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json(service_response)
