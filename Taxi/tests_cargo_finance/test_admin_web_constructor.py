import pytest

TRANSLATION_TABLE = {
    'Delivery_Admin_EntityTitle_Payments': {'ru': 'Платежи'},
    'Delivery_Admin_EntityTitle_PersonalData': {'ru': 'Персональные данные'},
    'Delivery_Admin_EntityTitle_Claim': {'ru': 'Заявка Доставки'},
    'Delivery_Admin_EntityTitle_LogPlatformRequestId': {
        'ru': 'Заказ Логистической Платформы',
    },
    'Delivery_Admin_EntityTitle_TaxiOrder': {'ru': 'Заказ Такси'},
    'Delivery_Admin_EntityTitle_TaxiOrderAlias': {
        'ru': 'Заказ Такси, id для партнёра',
    },
    'Delivery_Admin_EntityTitle_ClaimStatus': {'ru': 'Статус'},
    'Delivery_Admin_EntityTitle_Created': {'ru': 'Создан'},
    'Delivery_Admin_EntityTitle_Due': {'ru': 'Время подачи'},
    'Delivery_Admin_EntityTitle_PickupTime': {'ru': 'Время забора'},
    'Delivery_Admin_EntityTitle_TerminationTime': {'ru': 'Время завершения'},
    'Delivery_Admin_EntityTitle_PaymentType': {'ru': 'Тип оплаты'},
    'Delivery_Admin_EntityTitle_PaymentStatus': {'ru': 'Статус платежа'},
    'Delivery_Admin_EntityTitle_RouteContactsPersonalData': {
        'ru': 'Персональные данные контактных лиц по маршруту',
    },
    'Delivery_Admin_EntityTitle_Offer': {'ru': 'Оффер'},
    'Delivery_Admin_EntityTitle_FinalPrice': {'ru': 'Итоговая стоимость'},
    'Delivery_Admin_EntityTitle_Pricing': {'ru': 'Детализация прайсинга'},
    'Delivery_Admin_EntityTitle_ZoneId': {'ru': 'Зона'},
    'Delivery_Admin_EntityTitle_Route': {'ru': 'Маршрут'},
    'Delivery_Admin_EntityTitle_CorpClient': {'ru': 'Клиент'},
    'Delivery_Admin_EntityValue_PaymentTypeCard': {'ru': 'Карта'},
    'Delivery_Admin_EntityTitle_Tariffs': {'ru': 'Тарифы'},
    'payment_flow.claims': {'ru': 'claims'},
    'payment_flow.taxi_park': {'ru': 'taxipark'},
    'Delivery_Admin_WebConstructorBlockCargoFinancePaymentStatus_'
    'DebtStatus.HasDebt': {'ru': 'Есть долг'},
    'Delivery_Admin_WebConstructorBlockCargoFinancePaymentStatus_'
    'DebtStatus.HasNoDebt': {'ru': 'Нет долга'},
    'Delivery_Admin_WebConstructorBlockCargoFinancePaymentStatus_'
    'CargoFinancePaymentProcessingStatus.waiting': {
        'ru': 'Ожидается обработка',
    },
    'Delivery_Admin_WebConstructorBlockCargoFinancePaymentStatus_'
    'CargoFinancePaymentProcessingStatus.hanged': {'ru': 'Зависла'},
    'Delivery_Admin_WebConstructorBlockCargoFinancePaymentStatus_'
    'CargoFinancePaymentProcessingStatus.processing': {'ru': 'В обработке'},
    'Delivery_Admin_WebConstructorBlockPersonalData_'
    'Text.phones': {'ru': 'Показать телефон'},
    'Delivery_Admin_WebConstructorBlockPersonalData_'
    'Text.emails': {'ru': 'Показать почту'},
    'Delivery_Admin_EntityTitle_ActualContract': {
        'ru': 'Действующая версия контракта',
    },
    'Delivery_Admin_EntityTitle_PaymentsAndCommissions': {
        'ru': 'Платежи и комиссии',
    },
    'Delivery_Admin_EntityTitle_Shipper': {'ru': 'Грузоотправитель'},
    'Delivery_Admin_EntityTitle_Carrier': {'ru': 'Перевозчик'},
    'Delivery_Admin_EntityTitle_ThereIsNoData': {'ru': 'Нет данных'},
    'Delivery_Admin_EntityTitle_Trucks': {'ru': 'Заказ Магистралей'},
    'Delivery_Admin_EntityTitle_LastModified': {'ru': 'Последнее обновление'},
    'Delivery_Admin_EntityTitle_InvoiceDate': {'ru': 'Дата инициации'},
    'Delivery_Admin_EntityTitle_BillingClientId': {
        'ru': 'Идентификатор клиента биллинга',
    },
    'Delivery_Admin_EntityTitle_BillingContractId': {
        'ru': 'Идентификатор контракта',
    },
    'Delivery_Admin_EntityTitle_ContractVersion': {'ru': 'Версия контракта'},
    'Delivery_Admin_EntityValue_PaymentKind.trucks.payment.idle': {
        'ru': 'Оплата за простой',
    },
    'Delivery_Admin_EntityValue_PaymentKind.trucks.payment.contract': {
        'ru': 'Оплата за доставку',
    },
    'Delivery_Admin_EntityValue_PaymentKind.trucks.commission.contract': {
        'ru': 'Базовая комиссия',
    },
    'Delivery_Admin_EntityValue_PaymentKind.trucks.commission.idle': {
        'ru': 'Комиссия за простой',
    },
    'Delivery_Admin_EntityValue_PaymentKind.trucks.commission.discount': {
        'ru': 'Скидка на комиссию',
    },
    'Delivery_Admin_EntityValue_PaymentKind.trucks.commission.service': {
        'ru': 'Оплата запроса',
    },
}

DEVELOPER_CONTEXT_SETTINGS = {
    'flow': 'claims',
    'transaction_invoices': [
        {'id_template': 'claims/agent/{}'},
        {'id_template': 'claims/compensation/{}'},
    ],
    'processing_queues': [
        {
            'scope': 'cargo',
            'queue': 'finance_flow_claims_payments',
            'id_template': '{}',
        },
    ],
}

ADMIN_PAYMENTS_SETTINGS_CONFIG = {
    'developer_context_settings': [
        DEVELOPER_CONTEXT_SETTINGS,
        {
            'flow': 'new_claims',
            'transaction_invoices': [
                {'id_template': 'new_claims/agent/{}'},
                {'id_template': 'new_claims/compensation/{}'},
            ],
            'processing_queues': [
                {
                    'scope': 'cargo',
                    'queue': 'finance_flow_new_claims_payments',
                    'id_template': '{}',
                },
            ],
        },
    ],
    'graphic_settings': [
        {'flow': 'claims', 'color': '#0000ff'},
        {'flow': 'taxi_park', 'color': '#ff0000'},
    ],
    'currency_settings': [{'code': 'RUB', 'precision': 2}],
}


@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2={
        **ADMIN_PAYMENTS_SETTINGS_CONFIG,
        **{
            'developer_context_settings': [
                {**DEVELOPER_CONTEXT_SETTINGS},
                {**DEVELOPER_CONTEXT_SETTINGS, **{'flow': 'new_claims'}},
            ],
        },
    },
)
@pytest.mark.translations(
    web_constructor=TRANSLATION_TABLE,
    corp_client={'claim.status.accepted': {'ru': 'Подтверждено'}},
    tariff={'cargo': {'ru': 'грузовой'}},
)
@pytest.mark.pgsql(
    'cargo_finance', files=['test_web_constructor_with_payment_status.sql'],
)
async def test_web_constructor(
        taxi_cargo_finance, mock_claims_full, claim_id, load_json, order_proc,
):
    response = await taxi_cargo_finance.post(
        '/admin/cargo-finance/pay/order/context/operator',
        params={'flow': 'claims', 'entity_id': claim_id},
        headers={'Accept-Language': 'ru'},
    )

    web_constructor = load_json('web_constructor_response.json')

    assert response.status == 200
    assert response.json() == web_constructor


@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2={
        **ADMIN_PAYMENTS_SETTINGS_CONFIG,
        **{
            'developer_context_settings': [
                {**DEVELOPER_CONTEXT_SETTINGS, **{'flow': 'ndd_c2c'}},
            ],
        },
    },
)
@pytest.mark.pgsql(
    'cargo_finance',
    files=['test_web_constructor_ndd_agent_with_payment_status.sql'],
)
@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
async def test_web_constructor_ndd_agent_with_payment_status(
        taxi_cargo_finance, ndd_order_id, load_json,
):
    response = await taxi_cargo_finance.post(
        '/admin/cargo-finance/pay/order/context/operator',
        params={'flow': 'ndd_c2c', 'entity_id': ndd_order_id},
        headers={'Accept-Language': 'ru'},
    )

    web_constructor = load_json('web_constructor_ndd_response.json')

    assert response.status == 200
    assert response.json() == web_constructor


@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2={
        **ADMIN_PAYMENTS_SETTINGS_CONFIG,
        **{
            'developer_context_settings': [
                {**DEVELOPER_CONTEXT_SETTINGS, **{'flow': 'trucks'}},
            ],
        },
    },
)
@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
async def test_web_constructor_for_flow_trucks(
        taxi_cargo_finance, trucks_order_id, load_json, mockserver,
):
    url = '/processing/v1/cargo/finance_flow_trucks/events'

    @mockserver.json_handler(url)
    def _handler(request):
        return load_json(
            'billing_orders_v1_cargo_finance_flow_trucks_response.json',
        )

    response = await taxi_cargo_finance.post(
        '/admin/cargo-finance/pay/order/context/operator',
        params={'flow': 'trucks', 'entity_id': trucks_order_id},
        headers={'Accept-Language': 'ru'},
    )
    print(response.json())
    web_constructor = load_json('web_constructor_trucks_response.json')

    assert response.status == 200
    assert response.json() == web_constructor
