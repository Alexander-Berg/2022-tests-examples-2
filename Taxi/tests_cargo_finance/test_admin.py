import pytest

TRANSLATION_TABLE = {
    'Delivery_Admin_EntityTitle_Payments': {'ru': 'Платежи'},
    'Delivery_Admin_EntityTitle_PersonalData': {'ru': 'Персональные данные'},
    'Delivery_Admin_EntityTitle_Claim': {'ru': 'Заявка Доставки'},
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

ADMIN_FINANCE_MAIN_BOARD_SETTINGS_CONFIG = {
    'graphs_settings': {
        'settings_by_graph': {
            'hanged_payments': {'hanged_duration_seconds': 300},
        },
        'statistics_ttl_seconds': 60,
    },
    'worker_settings': {'sleep_time_seconds': 45},
}

ADMIN_PAYMENTS_WRONG_CONFIG = {
    'developer_context_settings': [
        {
            'flow': 'claims',
            'processing_queues': [
                {
                    'scope': 'cargo',
                    'queue': 'finance_flow_claims_payments',
                    'id_template': '{entity_id}',
                },
            ],
        },
    ],
    'graphic_settings': [
        {'flow': 'claims', 'color': '#0000ff'},
        {'flow': 'taxi_park', 'color': '#ff0000'},
    ],
}


@pytest.mark.translations(
    web_constructor={
        **TRANSLATION_TABLE,
        **{
            'payment_flow.claims': {'ru': 'ru_claims'},
            'payment_flow.taxi_park': {'ru': 'ru_taxipark'},
        },
    },
)
@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
    CARGO_FINANCE_MAIN_BOARD_SETTINGS=ADMIN_FINANCE_MAIN_BOARD_SETTINGS_CONFIG,
)
@pytest.mark.pgsql('cargo_finance', files=['developer_context_fragment.sql'])
async def test_developer_context_stubs(
        taxi_cargo_finance, mock_claims_full, claim_id,
):
    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={'entity_id': claim_id, 'flow': 'claims'},
        headers={'Accept-Language': 'ru'},
        json={'filter': {}},
    )
    assert response.status == 200
    assert response.json() == {
        'entities': [
            {
                'flow': 'claims',
                'id': 'ba05162748984b81affef7f6e92d96e2',
                'created_at': '2021-10-28T17:54:41+00:00',
                'flow_display_traits': {
                    'text': 'ru_claims',
                    'color': '#0000ff',
                },
                'display_status': {
                    'payment_processing_status': 'hanged',
                    'is_final_result_paid': False,
                    'has_debt': False,
                    'payment_processing_status_text': 'Зависла',
                    'debt_status_text': 'Нет долга',
                },
            },
        ],
        'has_more_matched_entities': False,
    }

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={'entity_id': '__invalid_id__', 'flow': 'claims'},
        headers={'Accept-Language': 'ru'},
        json={'filter': {}},
    )
    assert response.status == 200
    assert response.json() == {
        'entities': [],
        'has_more_matched_entities': False,
    }

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={'entity_id': '', 'flow': ''},
        headers={'Accept-Language': 'ru'},
        json={'filter': {}},
    )
    assert response.status == 200
    assert response.json() == {
        'entities': [
            {
                'flow': 'claims',
                'id': 'ba05162748984b81affef7f6e92d96e2',
                'created_at': '2021-10-28T17:54:41+00:00',
                'flow_display_traits': {
                    'text': 'ru_claims',
                    'color': '#0000ff',
                },
                'display_status': {
                    'payment_processing_status': 'hanged',
                    'is_final_result_paid': False,
                    'has_debt': False,
                    'payment_processing_status_text': 'Зависла',
                    'debt_status_text': 'Нет долга',
                },
            },
        ],
        'has_more_matched_entities': False,
    }

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/context/developer/fragment/list',
        params={'entity_id': claim_id, 'flow': 'claims'},
    )
    assert response.status == 200
    assert response.json() == {
        'kinds': [
            'pay_applying_state',
            'transactions_ng_invoices/'
            'claims/agent/ba05162748984b81affef7f6e92d96e2',
            'transactions_ng_invoices/'
            'claims/compensation/ba05162748984b81affef7f6e92d96e2',
            'procaas/cargo/finance_flow_claims_payments/'
            'ba05162748984b81affef7f6e92d96e2',
        ],
    }

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/context/developer/fragment/list',
        params={'entity_id': claim_id, 'flow': 'newclaims'},
    )
    assert response.status == 404


@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
)
@pytest.mark.pgsql('cargo_finance', files=['developer_context_fragment.sql'])
async def test_developer_context_fragment_pay_applying_state(
        taxi_cargo_finance, mock_claims_full, claim_id, load_json,
):
    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/context/developer/fragment',
        params={'entity_id': claim_id, 'flow': 'claims'},
        json={'kind': 'pay_applying_state'},
    )

    assert response.status == 200
    assert response.json() == load_json('pay_applying_fragment_response.json')

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/context/developer/fragment',
        params={'entity_id': '__invalid_id__', 'flow': 'claims'},
        json={'kind': 'unknown_kind'},
    )
    assert response.status == 404


@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
)
async def test_developer_context_fragment_transaction_invoices(
        taxi_cargo_finance,
        mock_claims_full,
        claim_id,
        mock_transactions_ng_retrieve_admin,
        load_json,
):
    invoice_id = '71478df92af4ca6a9a841a34b46c85b6'

    response = await taxi_cargo_finance.post(
        '/admin/cargo-finance/pay/order/context/developer/fragment',
        params={'entity_id': invoice_id, 'flow': 'claims'},
        json={
            'kind': (
                'transactions_ng_invoices/'
                'claims/agent/71478df92af4ca6a9a841a34b46c85b6'
            ),
        },
    )
    assert response.status == 200
    assert response.json() == load_json('invoice_fragment_response_agent.json')

    response = await taxi_cargo_finance.post(
        '/admin/cargo-finance/pay/order/context/developer/fragment',
        params={'entity_id': invoice_id, 'flow': 'claims'},
        json={
            'kind': (
                'transactions_ng_invoices/'
                'claims/compensation/71478df92af4ca6a9a841a34b46c85b6'
            ),
        },
    )
    assert response.status == 200
    assert response.json() == load_json(
        'invoice_fragment_response_compensation.json',
    )

    response = await taxi_cargo_finance.post(
        '/admin/cargo-finance/pay/order/context/developer/fragment',
        params={'entity_id': '__invalid__entity_id__', 'flow': 'claims'},
        json={
            'kind': (
                'transactions_ng_invoices/'
                'claims/agent/__invalid__entity_id__'
            ),
        },
    )
    assert response.status == 200
    assert response.json() == {
        'fragment': {
            'id': 'claims/agent/__invalid__entity_id__',
            'error': 'invoice is not found',
        },
        'kind': (
            'transactions_ng_invoices/' 'claims/agent/__invalid__entity_id__'
        ),
    }
    response = await taxi_cargo_finance.post(
        '/admin/cargo-finance/pay/order/context/developer/fragment',
        params={'entity_id': '__invalid__entity_id__', 'flow': 'claims'},
        json={
            'kind': (
                'transactions_ng_invoices/'
                'claims/compensation/__invalid__entity_id__'
            ),
        },
    )
    assert response.status == 200
    assert response.json() == {
        'fragment': {
            'id': 'claims/compensation/__invalid__entity_id__',
            'error': 'invoice is not found',
        },
        'kind': (
            'transactions_ng_invoices/'
            'claims/compensation/__invalid__entity_id__'
        ),
    }


@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
)
async def test_developer_context_fragment_processing_events(
        taxi_cargo_finance,
        claim_id,
        load_json,
        mock_procaas_events,
        procaas_events_response,
):
    response = await taxi_cargo_finance.post(
        '/admin/cargo-finance/pay/order/context/developer/fragment',
        params={'entity_id': '__invalid__claim_id__', 'flow': 'claims'},
        json={
            'kind': (
                'procaas/cargo/finance_flow_claims_payments/'
                '__invalid__claim_id__'
            ),
        },
    )

    assert response.status == 200
    assert response.json() == {
        'fragment': [],
        'kind': (
            'procaas/cargo/finance_flow_claims_payments/'
            '__invalid__claim_id__'
        ),
    }
    procaas_events_response.events = load_json(
        'processing_events_response.json',
    )
    response = await taxi_cargo_finance.post(
        '/admin/cargo-finance/pay/order/context/developer/fragment',
        params={'entity_id': claim_id, 'flow': 'claims'},
        json={
            'kind': ('procaas/cargo/finance_flow_claims_payments/' + claim_id),
        },
    )

    assert response.status == 200
    assert response.json()['fragment'] == load_json(
        'processing_events_response.json',
    )


@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_WRONG_CONFIG,
)
async def test_wrong_processing_events_config(
        taxi_cargo_finance,
        claim_id,
        load_json,
        mock_procaas_events,
        procaas_events_response,
):
    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/context/developer/fragment/list',
        params={'entity_id': claim_id},
    )
    assert response.status == 400


@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
)
@pytest.mark.pgsql('cargo_finance', files=['test_order_by_created_at.sql'])
async def test_order_by_created_at_without_filter(taxi_cargo_finance):

    expected_output = [
        '2021-10-28T13:54:41+00:00',
        '2021-10-28T12:54:41+00:00',
        '2021-10-28T11:54:41+00:00',
        '2021-10-28T10:54:41+00:00',
    ]

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={'entity_id': '', 'flow': 'claims'},
        headers={'Accept-Language': 'ru'},
        json={'filter': {}},
    )

    assert response.status == 200
    created_at_fields = [
        entity['created_at'] for entity in response.json()['entities']
    ]
    assert created_at_fields == expected_output


def expected_order_list_response(
        flow='claims',
        claim_id='1004',
        created_at='2021-10-28T11:54:41+00:00',
        flow_display_traits=None,
        display_status=None,
):
    # dangerous default value {} safety

    if display_status is None:
        display_status = {
            'payment_processing_status': 'waiting',
            'is_final_result_paid': False,
            'has_debt': False,
            'payment_processing_status_text': 'Ожидается обработка',
            'debt_status_text': 'Нет долга',
        }

    # dangerous default value {} safety
    if flow_display_traits is None:
        flow_display_traits = {'text': 'claims', 'color': '#0000ff'}

    return {
        'flow': flow,
        'id': claim_id,
        'created_at': created_at,
        'flow_display_traits': flow_display_traits,
        'display_status': display_status,
    }


def expected_display_status(
        requested_sum2pay=None,
        applying_sum2pay=None,
        applying_result=None,
        final_result=None,
        payment_processing_status='waiting',
        is_final_result_paid=False,
        has_debt=False,
        payment_processing_status_text='Ожидается обработка',
        debt_status_text='Нет долга',
):
    result = {
        'payment_processing_status': payment_processing_status,
        'is_final_result_paid': is_final_result_paid,
        'has_debt': has_debt,
        'payment_processing_status_text': payment_processing_status_text,
        'debt_status_text': debt_status_text,
    }

    if requested_sum2pay is not None:
        result['requested_sum2pay'] = requested_sum2pay

    if applying_sum2pay is not None:
        result['applying_sum2pay'] = applying_sum2pay

    if applying_result is not None:
        result['applying_result'] = applying_result

    if final_result is not None:
        result['final_result'] = final_result

    return result


@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
)
@pytest.mark.pgsql('cargo_finance', files=['test_order_by_created_at.sql'])
async def test_order_by_created_at_with_filter(taxi_cargo_finance):

    expected_output = [expected_order_list_response()]

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={'entity_id': '1004', 'flow': 'claims'},
        headers={'Accept-Language': 'ru'},
        json={'filter': {}},
    )

    assert response.status == 200
    assert response.json()['entities'] == expected_output


FIRST_GROUP_EXPECTED_OUTPUT = expected_order_list_response(
    claim_id='67d84b3e8e7043e4ab971f0ebe7c8ef3',
    created_at='2022-02-04T11:30:00.861903+00:00',
    display_status=expected_display_status(
        requested_sum2pay='484,00 ₽',
        final_result='484,00 ₽',
        is_final_result_paid=True,
    ),
)


@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
)
@pytest.mark.pgsql(
    'cargo_finance', files=['test_requesting_sum2pay_final_result.sql'],
)
async def test_requesting_sum2pay_final_result(taxi_cargo_finance):

    expected_output = [FIRST_GROUP_EXPECTED_OUTPUT]

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={
            'entity_id': '67d84b3e8e7043e4ab971f0ebe7c8ef3',
            'flow': 'claims',
        },
        headers={'Accept-Language': 'ru'},
        json={'filter': {}},
    )

    assert response.status == 200
    assert response.json()['entities'] == expected_output


@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
)
@pytest.mark.pgsql(
    'cargo_finance', files=['test_applying_sum2pay_applying_result.sql'],
)
async def test_applying_sum2pay_applying_result(taxi_cargo_finance):
    changed_output = FIRST_GROUP_EXPECTED_OUTPUT.copy()
    changed_output['display_status']['applying_sum2pay'] = '123,00 ₽'
    changed_output['display_status']['applying_result'] = '321,00 ₽'

    expected_output = [changed_output]

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={
            'entity_id': '67d84b3e8e7043e4ab971f0ebe7c8ef3',
            'flow': 'claims',
        },
        headers={'Accept-Language': 'ru'},
        json={'filter': {}},
    )

    assert response.status == 200
    assert response.json()['entities'] == expected_output


@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
)
@pytest.mark.pgsql(
    'cargo_finance', files=['test_pay_admin_order_list_all.sql'],
)
async def test_pay_admin_order_list_all(taxi_cargo_finance):

    expected_output = [
        expected_order_list_response(
            claim_id='1001', created_at='2021-10-28T13:54:41+00:00',
        ),
        expected_order_list_response(
            claim_id='1003', created_at='2021-10-28T12:54:41+00:00',
        ),
        expected_order_list_response(),
        expected_order_list_response(
            claim_id='1002', created_at='2021-10-28T10:54:41+00:00',
        ),
    ]

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={'entity_id': '', 'flow': 'claims'},
        headers={'Accept-Language': 'ru'},
        json={'filter': {}},
    )

    assert response.status == 200
    assert response.json()['entities'] == expected_output


@pytest.mark.parametrize(
    'expected_output, request_json',
    [
        (
            [
                'ba05162748984b81affef7f6e92d96e2',
                'ca05162748984b81affef7f6e92d96e2',
            ],
            {'filter': {'has_debt': False}},
        ),
        (
            [
                'da05162748984b81affef7f6e92d96e2',
                'ea05162748984b81affef7f6e92d96e2',
            ],
            {'filter': {'has_debt': True}},
        ),
        (
            [
                'ba05162748984b81affef7f6e92d96e2',
                'ca05162748984b81affef7f6e92d96e2',
                'da05162748984b81affef7f6e92d96e2',
                'ea05162748984b81affef7f6e92d96e2',
            ],
            {'filter': {'is_final_result_paid': True}},
        ),
        ([], {'filter': {'is_final_result_paid': False}}),
        (
            [
                'da05162748984b81affef7f6e92d96e2',
                'ea05162748984b81affef7f6e92d96e2',
            ],
            {'filter': {'has_debt': True, 'is_final_result_paid': True}},
        ),
    ],
)
@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
@pytest.mark.pgsql(
    'cargo_finance', files=['test_pay_admin_order_list_filter.sql'],
)
@pytest.mark.config(
    CARGO_FINANCE_MAIN_BOARD_SETTINGS=ADMIN_FINANCE_MAIN_BOARD_SETTINGS_CONFIG,
)
async def test_pay_admin_order_list_filter_by_debt_and_result_paid(
        taxi_cargo_finance, expected_output, request_json,
):

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={'entity_id': '', 'flow': 'claims'},
        headers={'Accept-Language': 'ru'},
        json=request_json,
    )

    assert response.status == 200
    created_at_fields = [
        entity['id'] for entity in response.json()['entities']
    ]
    assert created_at_fields == expected_output


@pytest.mark.parametrize(
    'expected_output, request_json',
    [
        (
            [
                'ca05162748984b81affef7f6e92d96e2',
                'da05162748984b81affef7f6e92d96e2',
            ],
            {'filter': {'payment_processing_statuses': ['hanged']}},
        ),
        (
            ['ea05162748984b81affef7f6e92d96e2'],
            {'filter': {'payment_processing_statuses': ['waiting']}},
        ),
        (
            ['ba05162748984b81affef7f6e92d96e2'],
            {'filter': {'payment_processing_statuses': ['processing']}},
        ),
        (
            [
                'ba05162748984b81affef7f6e92d96e2',
                'ca05162748984b81affef7f6e92d96e2',
                'da05162748984b81affef7f6e92d96e2',
            ],
            {
                'filter': {
                    'payment_processing_statuses': ['processing', 'hanged'],
                },
            },
        ),
        ([], {'filter': {'payment_processing_statuses': []}}),
    ],
)
@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
@pytest.mark.config(
    CARGO_FINANCE_MAIN_BOARD_SETTINGS=ADMIN_FINANCE_MAIN_BOARD_SETTINGS_CONFIG,
)
@pytest.mark.pgsql(
    'cargo_finance', files=['test_pay_admin_order_list_filter.sql'],
)
async def test_pay_admin_order_list_filter_by_payment_status(
        taxi_cargo_finance, expected_output, request_json,
):

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={'entity_id': '', 'flow': 'claims'},
        headers={'Accept-Language': 'ru'},
        json=request_json,
    )

    assert response.status == 200
    created_at_fields = [
        entity['id'] for entity in response.json()['entities']
    ]
    assert created_at_fields == expected_output


@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
)
@pytest.mark.pgsql('cargo_finance', files=['test_using_debt_collector.sql'])
async def test_using_debt_collector_true(taxi_cargo_finance):

    expected_output = [
        expected_order_list_response(
            claim_id='1001',
            created_at='2021-10-28T13:54:41+00:00',
            display_status=expected_display_status(
                has_debt=True, debt_status_text='Есть долг',
            ),
        ),
    ]

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={'entity_id': '1001', 'flow': 'claims'},
        headers={'Accept-Language': 'ru'},
        json={'filter': {}},
    )

    assert response.status == 200
    assert response.json()['entities'] == expected_output


SECOND_GROUP_EXPECTED_OUTPUT = expected_order_list_response(
    claim_id='1002',
    created_at='2021-10-28T10:54:41+00:00',
    display_status=expected_display_status(has_debt=False),
)


@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
)
@pytest.mark.pgsql('cargo_finance', files=['test_using_debt_collector.sql'])
async def test_using_debt_collector_false(taxi_cargo_finance):

    expected_output = [SECOND_GROUP_EXPECTED_OUTPUT]

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={'entity_id': '1002', 'flow': 'claims'},
        headers={'Accept-Language': 'ru'},
        json={'filter': {}},
    )

    assert response.status == 200
    assert response.json()['entities'] == expected_output


@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
    CARGO_FINANCE_MAIN_BOARD_SETTINGS=ADMIN_FINANCE_MAIN_BOARD_SETTINGS_CONFIG,
)
@pytest.mark.pgsql('cargo_finance', files=['test_is_hanged.sql'])
async def test_is_hanged(taxi_cargo_finance):
    changed_output = SECOND_GROUP_EXPECTED_OUTPUT.copy()
    changed_output['display_status']['payment_processing_status'] = 'hanged'
    changed_output['display_status'][
        'payment_processing_status_text'
    ] = 'Зависла'

    expected_output = [changed_output]

    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={'entity_id': '1002', 'flow': 'claims'},
        headers={'Accept-Language': 'ru'},
        json={'filter': {}},
    )

    assert response.status == 200
    assert response.json()['entities'] == expected_output


@pytest.mark.translations(web_constructor=TRANSLATION_TABLE)
@pytest.mark.config(
    CARGO_FINANCE_ADMIN_PAYMENTS_SETTINGS_V2=ADMIN_PAYMENTS_SETTINGS_CONFIG,
    CARGO_FINANCE_MAIN_BOARD_SETTINGS=ADMIN_FINANCE_MAIN_BOARD_SETTINGS_CONFIG,
)
@pytest.mark.pgsql(
    'cargo_finance', files=['test_is_hanged_and_processing.sql'],
)
async def test_is_hanged_and_processing(taxi_cargo_finance):
    changed_output = SECOND_GROUP_EXPECTED_OUTPUT.copy()
    changed_output['display_status'][
        'payment_processing_status'
    ] = 'processing'
    changed_output['display_status'][
        'payment_processing_status_text'
    ] = 'В обработке'
    expected_output = [changed_output]
    response = await taxi_cargo_finance.post(
        'admin/cargo-finance/pay/order/list-filtered',
        params={'entity_id': '1002', 'flow': 'claims'},
        headers={'Accept-Language': 'ru'},
        json={'filter': {}},
    )

    assert response.status == 200
    assert response.json()['entities'] == expected_output
