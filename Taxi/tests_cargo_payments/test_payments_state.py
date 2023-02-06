import base64

import pytest

_CASHIER_FULLNAME_TAG = '1021'


async def test_happy_path(state_payment_created, taxi_cargo_payments):
    state = await state_payment_created()

    response = await taxi_cargo_payments.post(
        'v1/payment/info', params={'payment_id': state.payment_id},
    )
    assert response.status_code == 200

    json = response.json()
    assert json['status'] == 'new'
    assert json['revision'] == 1
    assert json['details']['external_id'] == '456'
    assert json['details']['geo_data']['zone_id'] == 'moscow'
    assert json['items'] == [
        {
            'article': 'article_1',
            'count': 2,
            'currency': 'RUB',
            'supplier_inn': '9705114405',
            'nds': 'nds_20',
            'price': '10',
            'title': 'title_1',
            'type': 'product',
        },
        {
            'article': 'article_2',
            'count': 2,
            'currency': 'RUB',
            'supplier_inn': '9705114405',
            'nds': 'nds_20',
            'price': '10',
            'title': 'title_2',
            'type': 'product',
        },
    ]
    assert len(json['payment_methods']) == 2


async def test_empty_inn_admin(
        state_payment_created, state_context, taxi_cargo_payments,
):
    state_context.supplier_inn = None
    state = await state_payment_created()

    response = await taxi_cargo_payments.post(
        'v1/payment/info', params={'payment_id': state.payment_id},
    )
    assert response.status_code == 200

    json = response.json()
    assert len(json['items']) == 2
    assert 'supplier_inn' not in json['items'][0]
    assert 'supplier_inn' not in json['items'][1]


async def test_empty_inn_taximeter(
        state_performer_found,
        confirm_diagnostics,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
        state_context,
        update_items,
        confirm_payment,
):
    """
        Eat's order is created without supplier_inn, but it was
        required.
        They fill it later on payment/update
    """
    state_context.supplier_inn = None
    state = await state_performer_found(items_count=1)
    await confirm_diagnostics()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 500

    response = await confirm_payment(
        status_code=409,
        payment_id=state.payment_id,
        revision=state.payment_revision,
        paymethod='card',
    )

    await update_items(
        status_code=200,
        payment_id=state.payment_id,
        snapshot_token='token1',
        items_count=1,
    )

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )

    assert response.status_code == 200
    json = response.json()
    assert len(json['payment']['items']) == 1
    assert json['payment']['items'][0]['supplier_inn'] == '9705114405'

    response = await confirm_payment(
        status_code=200,
        payment_id=state.payment_id,
        revision=state.payment_revision + 1,
        paymethod='card',
    )


async def test_empty_inn_taximeter_none_agent(
        state_performer_found,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
        state_context,
        confirm_payment,
):
    """
        Check supplier_inn is not required for agent_type: none.
    """
    state_context.supplier_inn = None
    state_context.agent_type = 'none'
    state = await state_performer_found()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    json = response.json()
    assert len(json['payment']['items']) == 2
    assert 'supplier_inn' not in json['payment']['items'][0]

    response = await confirm_payment(
        status_code=200,
        payment_id=state.payment_id,
        revision=state.payment_revision,
        paymethod='card',
    )


async def test_fiscal_data(
        state_payment_confirmed,
        taxi_cargo_payments,
        get_payment,
        load_json_var,
):
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'fiscal_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    response = await taxi_cargo_payments.post(
        'v1/payment/info', params={'payment_id': state.payment_id},
    )
    assert response.status_code == 200

    json = response.json()

    assert json['fiscal_data']['fiscal_datetime'] == '2021-02-12T19:12:00'
    assert json['fiscal_data']['fiscal_document_mark'] == '3910020199'
    assert json['fiscal_data']['fiscal_document_number'] == '112'
    assert json['fiscal_data']['fiscal_storage_number'] == '0000000020005880'
    assert json['fiscal_data']['invoice'] == '43V7LGPAK7EF'


async def test_payment_history(
        state_payment_confirmed, taxi_cargo_payments, driver_headers,
):
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        'v1/admin/payment/history', params={'payment_id': state.payment_id},
    )
    json = response.json()
    assert response.status_code == 200
    assert len(json['history']) == 2
    assert json['history'][0]['status'] == 'new'
    assert json['history'][0]['history_action'] == 'add'
    assert json['history'][1]['status'] == 'confirmed'
    assert json['history'][1]['history_action'] == 'update_data'


async def test_paymethods_without_nfc(
        state_performer_found,
        confirm_diagnostics,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
):
    state = await state_performer_found()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    assert len(response.json()['payment']['payment_methods']) == 1


async def test_paymethods_with_nfc(
        state_performer_found,
        confirm_diagnostics,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
):
    state = await state_performer_found()
    await confirm_diagnostics()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    assert len(response.json()['payment']['payment_methods']) == 2


async def test_paymethods_card_not_allowed(
        state_performer_found,
        confirm_diagnostics,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
):
    state = await state_performer_found()
    await confirm_diagnostics(is_diagnostics_passed=False)

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    assert len(response.json()['payment']['payment_methods']) == 1


@pytest.mark.parametrize(
    ['suffix'],
    (
        pytest.param(
            '_id_pd',
            marks=pytest.mark.config(
                CARGO_PAYMENTS_CONVERT_PERSONAL_DATA_ENABLED=True,
            ),
        ),
        pytest.param(
            '',
            marks=pytest.mark.config(
                CARGO_PAYMENTS_CONVERT_PERSONAL_DATA_ENABLED=False,
            ),
        ),
    ),
)
async def test_basic_taximeter(
        state_performer_found,
        confirm_diagnostics,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
        suffix,
        pgsql,
):
    state = await state_performer_found()
    await confirm_diagnostics()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_payments'].conn.cursor()
    cursor.execute('SELECT inn FROM cargo_payments.payment_items')
    assert list(cursor) == [('9705114405' + suffix,), ('9705114405' + suffix,)]

    assert response.json() == {
        'auth_info': {
            'login': state.performer.agent.login,
            'secret_code': state.performer.agent.secret_key,
            'pin_code': '000000',
        },
        'payment': {
            'details': {
                'client_id': {
                    'id': '651efc77d91b462f86a47eef39795b03',
                    'type': 'corp_client_id',
                },
                'customer': {
                    'email_pd_id': 'nsofya@yandex-team.ru_id',
                    'phone_pd_id': 'ooo_id',
                },
                'external_id': '456',
                'virtual_client_id': state.default_virtual_client_id,
            },
            'items': [
                {
                    'article': 'article_1',
                    'count': 2,
                    'currency': 'RUB',
                    'nds': 'nds_20',
                    'price': '10',
                    'supplier_inn': '9705114405',
                    'title': 'title_1',
                    'ui': {'title': 'title_1'},
                },
                {
                    'article': 'article_2',
                    'count': 2,
                    'currency': 'RUB',
                    'nds': 'nds_20',
                    'price': '10',
                    'supplier_inn': '9705114405',
                    'title': 'title_2',
                    'ui': {'title': 'title_2'},
                },
            ],
            'payment_id': state.payment_id,
            'payment_methods': [
                {
                    'is_alternative': False,
                    'is_sdk_flow': True,
                    'type': 'card',
                    'ui': {'title': 'Картой'},
                },
                {
                    'is_alternative': False,
                    'is_sdk_flow': False,
                    'type': 'link',
                    'ui': {'title': 'По ссылке'},
                },
            ],
            'revision': 1,
            'status': 'new',
            'is_paid': False,
        },
        'transaction': {
            'amount': '40',
            'aux_data': {
                'Purchases': [
                    {
                        '1212': 1,
                        '1214': 4,
                        '1222': 64,
                        '1225': 'yandex_virtual_client',
                        '1226': '9705114405',
                        'Price': '10',
                        'Quantity': 2,
                        'TaxCode': ['VAT2000'],
                        'Title': 'title_1',
                    },
                    {
                        '1212': 1,
                        '1214': 4,
                        '1222': 64,
                        '1225': 'yandex_virtual_client',
                        '1226': '9705114405',
                        'Price': '10',
                        'Quantity': 2,
                        'TaxCode': ['VAT2000'],
                        'Title': 'title_2',
                    },
                ],
                'Tags': {'1057': 64, '1021': 'Ершунов Иван Иванович'},
            },
            'customer_email': 'nsofya@yandex-team.ru',
            'customer_phone': 'ooo',
            'description': 'Order:456',
            'service_id': 'CARDPORT-PRO.ACCEPT-PAYMENT',
            'payment_confirmation_type': 'app',
        },
        'ui': {'header': 'Получите оплату', 'title': 'Получил оплату'},
    }
    assert response.headers['X-Polling-Delay-Ms'] == '1000'


async def test_valid_mark_gs1m(
        state_performer_found,
        confirm_diagnostics,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
):
    mark = {
        'kind': 'gs1_data_matrix_base64',
        'code': base64.b64encode(b']C1010000000000005521A').decode(),
    }

    state = await state_performer_found(item_mark=mark)
    await confirm_diagnostics()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    for purchase in response.json()['transaction']['aux_data']['Purchases']:
        assert purchase['1162'] == '444D00000000003741'


async def test_invalid_mark_gs1m(
        state_performer_found,
        confirm_diagnostics,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
):
    mark = {
        'kind': 'gs1_data_matrix_base64',
        'code': base64.b64encode(
            b'8005112000\x1d21zZyR5SDcpc0KD\x1d0104060511218058005112000',
        ).decode(),
    }

    state = await state_performer_found(item_mark=mark)
    await confirm_diagnostics()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    for purchase in response.json()['transaction']['aux_data']['Purchases']:
        assert '1162' not in purchase


async def test_mark_compiled(
        state_performer_found,
        confirm_diagnostics,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
):
    mark = {'kind': 'compiled', 'code': ' \n      444D00000000003741 \n '}

    state = await state_performer_found(item_mark=mark)
    await confirm_diagnostics()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    for purchase in response.json()['transaction']['aux_data']['Purchases']:
        assert purchase['1162'] == '444D00000000003741'


async def test_invalid_compiled_code_no_tag(
        state_performer_found,
        confirm_diagnostics,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
):
    mark = {'kind': 'compiled', 'code': '44D00000000003741'}

    state = await state_performer_found(item_mark=mark)
    await confirm_diagnostics()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    for purchase in response.json()['transaction']['aux_data']['Purchases']:
        assert '1162' not in purchase


@pytest.mark.parametrize('payment_status', ['authorized', 'finished'])
async def test_ui_for_paid_state(
        state_payment_confirmed,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
        set_payment_status,
        payment_status: str,
):
    """
        Check taximeter header/title changes on payment finish.
    """
    state = await state_payment_confirmed()

    set_payment_status(payment_id=state.payment_id, status=payment_status)

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    json = response.json()
    assert json['payment']['status'] == payment_status
    assert json['ui']['header'] == 'Вручите посылку'
    assert json['ui']['title'] == 'Вручил посылку'
    assert json['ui']['timer']['payment_wait_total'] == 30


@pytest.mark.parametrize('payment_method', ['card', 'link'])
async def test_ui_payment_method(
        state_payment_confirmed,
        taxi_cargo_payments,
        driver_headers,
        payment_method: str,
):
    """
        Check taximeter ui payment method.
    """
    state = await state_payment_confirmed(payment_method=payment_method)

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    json = response.json()
    assert json['ui']['timer']['payment_method'] == payment_method


async def test_wrong_performer(
        state_performer_found, driver_headers, taxi_cargo_payments,
):
    state = await state_performer_found()

    driver_headers['X-YaTaxi-Driver-Profile-Id'] = 'anotherone'
    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 403


@pytest.mark.parametrize(
    'available_payment_methods', [['card'], ['card', 'link']],
)
async def test_payment_methods_filter(
        state_performer_found,
        confirm_diagnostics,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
        setup_virtual_clients_settings,
        available_payment_methods,
):
    """
        Without filter [card, link] expected.
        With filter only [card].
    """
    state = await state_performer_found()
    await confirm_diagnostics()

    await setup_virtual_clients_settings(
        available_payment_methods=available_payment_methods,
    )

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    assert len(response.json()['payment']['payment_methods']) == len(
        available_payment_methods,
    )


@pytest.mark.parametrize(
    'cashier_kind, cashier_fullname, expected_tag',
    [
        ['courier_fullname', None, 'Ершунов Иван Иванович'],
        ['static_cashier', None, None],
        ['static_cashier', 'Заведов Николай', 'Заведов Николай'],
    ],
)
async def test_cashier_fullname_settings(
        state_performer_found,
        confirm_diagnostics,
        taxi_cargo_payments,
        exp_cargo_payments_post_payment_state,
        driver_headers,
        setup_virtual_clients_settings,
        cashier_kind,
        cashier_fullname,
        expected_tag,
):
    """
        Check tag "1021" with courier's fullname is optional.
    """
    state = await state_performer_found()
    await confirm_diagnostics()

    await setup_virtual_clients_settings(
        cashier_kind=cashier_kind, cashier_fullname=cashier_fullname,
    )

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    tags = response.json()['transaction']['aux_data']['Tags']
    assert tags.get(_CASHIER_FULLNAME_TAG) == expected_tag


@pytest.mark.parametrize(
    'payment_confirmation_type', ['none', 'app', 'app_with_signature'],
)
async def test_payment_confirmation_type(
        state_payment_confirmed,
        get_payment_state,
        exp_cargo_payments_nfc_callback,
        payment_confirmation_type: str,
):
    """
        Check payment_confirmation_type settings from
        config3.0 cargo_payments_nfc_callback.
    """
    await exp_cargo_payments_nfc_callback(
        payment_confirmation_type=payment_confirmation_type,
    )
    state = await state_payment_confirmed()

    response = await get_payment_state(state.payment_id)
    assert (
        response['transaction']['payment_confirmation_type']
        == payment_confirmation_type
    )


@pytest.mark.parametrize('payment_method', ['link', 'card'])
async def test_payment_method(
        run_operations_executor,
        state_performer_found,
        taxi_cargo_payments,
        driver_headers,
        mock_link_create,
        load_json_var,
        get_payment,
        payment_method,
):
    state = await state_performer_found()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/confirm',
        json={
            'payment_id': state.payment_id,
            'revision': state.payment_revision,
            'payment_method': payment_method,
        },
        headers=driver_headers,
    )
    assert response.status_code == 200
    await run_operations_executor()

    json = load_json_var(
        'pay_event.json', payment_id=state.payment_id, amount='40',
    )
    json['MID'] = (
        'nondefault@yandex' if payment_method == 'card' else 'default@yandex'
    )

    response = await taxi_cargo_payments.post('2can/status', json=json)
    assert response.status_code == 200

    payment = await get_payment(payment_id=state.payment_id)
    assert payment['chosen_payment_method'] == payment_method


@pytest.fixture(name='get_agent_virtual_id')
async def _get_agent_virtual_id(pgsql):
    def wrapper(park_id, driver_id):
        cursor = pgsql['cargo_payments'].dict_cursor()
        cursor.execute(
            """
            SELECT
                virtual_client_id
            FROM cargo_payments.performer_agents JOIN cargo_payments.agents ON
            cargo_payments.performer_agents.agent_id = cargo_payments.agents.id
            WHERE park_id=%s AND driver_id=%s
            """,
            (park_id, driver_id),
        )

        result = [dict(row) for row in cursor]
        if not result:
            return None
        return result[0]['virtual_client_id']

    return wrapper


async def test_eda_fallback_happy_path(
        taxi_cargo_payments,
        state_performer_found,
        confirm_diagnostics,
        mock_link_create,
        current_state,
        driver_headers,
        run_operations_executor,
        load_json_var,
        state_context,
        get_payment,
        get_agent_virtual_id,
):
    """
      EDA uses logistics couriers as fallback. Check happy path.
    """
    state = await state_performer_found(
        virtual_client_id=current_state.eats_virtual_client_id,
    )
    payment = await get_payment(state.payment_id)
    assert (
        payment['details']['virtual_client_id']
        == current_state.eats_virtual_client_id
    )

    agent_virtual_id = get_agent_virtual_id(
        state.performer.park_id, state.performer.driver_id,
    )
    assert agent_virtual_id == current_state.default_virtual_client_id

    mock_link_create.expected_token = current_state.eats_token
    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/confirm',
        json={
            'payment_id': state.payment_id,
            'revision': state.payment_revision,
            'payment_method': 'link',
        },
        headers=driver_headers,
    )
    assert response.status_code == 200

    await run_operations_executor()

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200

    payment = await get_payment(state.payment_id)
    assert payment['status'] == 'authorized'

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'fiscal_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200

    payment = await get_payment(state.payment_id)
    assert payment['status'] == 'finished'
    assert payment['is_paid']


async def test_no_card_for_eda_fallback(
        taxi_cargo_payments,
        state_performer_found,
        confirm_diagnostics,
        current_state,
        driver_headers,
):
    """
      EDA uses logistics couriers as fallback. Check that in that case the only
      available payment method is by link.
    """
    state = await state_performer_found(
        virtual_client_id=current_state.eats_virtual_client_id,
    )
    await confirm_diagnostics(is_diagnostics_passed=True)
    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )

    assert len(response.json()['payment']['payment_methods']) == 1
    assert response.json()['payment']['payment_methods'][0]['type'] == 'link'
