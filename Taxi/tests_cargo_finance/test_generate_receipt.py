import pytest

_CLAIM_ID = '731d5f778c8b4ac9b5569d38357b92b2'
_INVOICE_ID = f'claims/agent/{_CLAIM_ID}'

STATE = {
    'flow': 'claims',
    'entity_id': _CLAIM_ID,
    'created_at': '2022-02-04T11:30:00.861903+00:00',
    'last_modified_at': '2022-02-04T11:30:00.861903+00:00',
    'last_request_taken_at': '2022-02-04T11:30:00.861903+00:00',
    'requested_sum2pay': {
        'revision': 0,
        'client': {
            'agent': {
                'sum': '100',
                'currency': 'RUB',
                'payment_methods': {
                    'card': {
                        'cardstorage_id': 'some_cardstorage_id',
                        'owner_yandex_uid': 'some_owner_yandex_uid',
                    },
                },
                'context': {
                    'billing_product': {'name': '', 'id': ''},
                    'customer_ip': '10.20.30.40',
                    'invoice_due': '2022-02-04T11:30:00.861903+00:00',
                    'corp_client_id': 'clid49012ee2fc1e762848568d6228fq',
                    'fiscal_receipt_info': {
                        'personal_tin_id': 'personal_tin_id_value',
                        'vat': 'nds_18',
                        'title': 'title_value',
                        'tin': 'tin_value',
                    },
                    'country': 'RUS',
                    'taxi_order_id': 'a089ed783ecbcd8b9d09620dbea1e1bd',
                },
            },
        },
    },
    'applied_sum2pay_revision': 0,
    'notification_revision': 0,
    'final_paid_sum_revision': 0,
}

STATE_C2C = {
    'flow': 'claims',
    'entity_id': _CLAIM_ID,
    'created_at': '2022-02-04T11:30:00.861903+00:00',
    'last_modified_at': '2022-02-04T11:30:00.861903+00:00',
    'last_request_taken_at': '2022-02-04T11:30:00.861903+00:00',
    'requested_sum2pay': {
        'revision': 0,
        'client': {
            'agent': {
                'sum': '100',
                'currency': 'RUB',
                'payment_methods': {
                    'card': {
                        'cardstorage_id': 'some_cardstorage_id',
                        'owner_yandex_uid': 'some_owner_yandex_uid',
                    },
                },
                'context': {
                    'billing_product': {'name': '', 'id': ''},
                    'customer_ip': '10.20.30.40',
                    'invoice_due': '2022-02-04T11:30:00.861903+00:00',
                    'fiscal_receipt_info': {
                        'personal_tin_id': 'personal_tin_id_value',
                        'vat': 'nds_18',
                        'title': 'title_value',
                        'tin': 'tin_value',
                    },
                    'country': 'ISR',
                    'taxi_order_id': 'a089ed783ecbcd8b9d09620dbea1e1bd',
                },
            },
        },
    },
    'applied_sum2pay_revision': 0,
    'notification_revision': 0,
    'final_paid_sum_revision': 0,
}

C2C_CARD_FISCAL_REQUEST = {
    'transaction_id': '725b676b22d6b43fb68b62059d0c5da8',
    'is_refund': False,
    'payment_method': 'card',
    'price_details': {'total': '96'},
    'isr_data': {
        'cc_deal_type': 1,
        'cc_num_of_payments': 1,
        'cc_number': '4444',
        'cc_payment_num': 1,
        'cc_type': 2,
        'cc_type_name': 'VISA',
        'customer_name': '+79001111111',
        'developer_email': 'voytekh@yandex-team.ru',
        'item_amount': 1,
        'payment_type': 3,
    },
    'service_rendered_at': '2022-03-01T10:32:50.203+00:00',
    'title': 'Delivery',
    'country': 'ISR',
    'provider_inn': '085715582283',
}

C2C_CASH_FISCAL_REQUEST = {
    'transaction_id': '725b676b22d6b43fb68b62059d0c5da8',
    'is_refund': False,
    'payment_method': 'cash',
    'price_details': {'total': '96'},
    'isr_data': {
        'developer_email': 'voytekh@yandex-team.ru',
        'customer_name': '+79001111111',
        'payment_type': 1,
        'item_amount': 1,
    },
    'service_rendered_at': '2022-03-01T10:32:50.203+00:00',
    'title': 'Delivery',
    'country': 'ISR',
    'provider_inn': '085715582283',
}


@pytest.fixture(name='mock_fiscal_generate')
def _mock_fiscal_generate(mockserver, mock_with_context):
    url = '/cargo-fiscal/internal/cargo-fiscal/receipts/delivery/orders/generate-transaction'  # noqa pylint: disable

    @mockserver.json_handler(url)
    def handler(request):
        return {}

    return handler


@pytest.fixture(name='mock_fiscal_generate_transactions')
def _mock_fiscal_generate_transactions(mockserver, mock_with_context):
    url = '/cargo-fiscal/internal/cargo-fiscal/receipts/delivery/taxiorders/generate-transaction'  # noqa pylint: disable

    @mockserver.json_handler(url)
    def handler(request):
        return {}

    return handler


@pytest.fixture(name='mock_corp_info')
def _mock_corp_info(mockserver, mock_with_context):
    url = '/cargo-corp/internal/cargo-corp/v1/client/info'

    @mockserver.json_handler(url)
    def handler(request):
        return {
            'corp_client_id': 'clid49012ee2fc1e762848568d6228fq',
            'company': {'name': 'Beloved Client'},
            'revision': 1,
            'created_ts': '2020-01-01T00:00:00+00:00',
            'updated_ts': '2020-01-01T00:00:00+00:00',
        }

    return handler


@pytest.fixture(name='mock_cardstorage')
def _mock_cardstorage(mockserver, mock_with_context):
    url = '/cardstorage/v1/card'

    @mockserver.json_handler(url)
    def handler(request):
        return {
            'card_id': '1',
            'billing_card_id': '1',
            'permanent_card_id': '1',
            'currency': 'RUB',
            'expiration_month': 12,
            'expiration_year': 2020,
            'owner': 'Mr',
            'possible_moneyless': False,
            'region_id': 'RU',
            'regions_checked': ['RU'],
            'system': 'VISA',
            'valid': True,
            'bound': True,
            'unverified': False,
            'busy': False,
            'busy_with': [],
            'from_db': True,
            'number': '51002222****4444',
            'bin': '510022',
        }

    return handler


@pytest.fixture(name='run_cargo_finance_receipt_by_tng_data_stq')
async def _run_cargo_finance_receipt_by_tng_data_stq():
    async def wrapper(stq_runner):
        await stq_runner.cargo_finance_receipt_by_tng_data.call(
            task_id=f'{_CLAIM_ID}_receipt',
            kwargs={
                'invoice_id': _INVOICE_ID,
                'entity_id': _CLAIM_ID,
                'flow': 'claims',
            },
            expect_fail=False,
        )

    return wrapper


@pytest.mark.parametrize(
    'country,payment_state,is_corp,client_name',
    [
        pytest.param('RUS', 'cleared', True, None),
        pytest.param('KAZ', 'cleared', True, None),
        pytest.param('RUS', 'hold', True, None),
        pytest.param('KAZ', 'hold', True, None),
        pytest.param('ISR', 'hold', True, 'Beloved Client'),
        pytest.param('ISR', 'hold', False, '+79001111111'),
        pytest.param('ISR', 'cleared', True, 'Beloved Client'),
    ],
)
async def test_order_cleared(
        mockserver,
        load_json,
        order_archive_mock,
        stq_runner,
        run_cargo_finance_receipt_by_tng_data_stq,
        mock_fiscal_generate,
        mock_corp_info,
        mock_cardstorage,
        country,
        payment_state,
        is_corp,
        client_name,
):

    STATE['requested_sum2pay']['client']['agent']['context'][
        'country'
    ] = country

    order_proc = load_json('order_proc_fiscal_card.json')
    order_archive_mock.set_order_proc(order_proc)

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal_phones(request):
        return mockserver.make_response(
            json={'id': 'eee', 'value': '+79001111111'}, status=200,
        )

    @mockserver.json_handler(
        '/cargo-finance/internal/cargo-finance/pay/order/applying/state',
    )
    def _mock_state(request):
        if is_corp:
            return mockserver.make_response(json=STATE, status=200)
        return mockserver.make_response(json=STATE_C2C, status=200)

    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def _mock_invoice_retrieve(request):
        assert request.json['id'] == _INVOICE_ID
        return mockserver.make_response(
            json=load_json(
                f'response_t-ng_v2_invoice_retrieve_{payment_state}.json',
            ),
            status=200,
        )

    await run_cargo_finance_receipt_by_tng_data_stq(stq_runner)
    expected_requests = load_json(
        'test_generate_receipt_expected_requests.json',
    )[f'{country}_{payment_state}']
    assert mock_fiscal_generate.times_called == len(expected_requests)
    for _ in range(mock_fiscal_generate.times_called):
        actual_request = mock_fiscal_generate.next_call()['request'].json
        expected_request = expected_requests[_]
        if client_name:
            expected_request['isr_data']['customer_name'] = client_name
        assert actual_request == expected_request


@pytest.fixture(name='run_cargo_finance_taxi_invoice_update_callback')
async def _run_cargo_finance_taxi_invoice_update_callback():
    async def wrapper(stq_runner):
        await stq_runner.cargo_finance_taxi_invoice_update_callback.call(
            task_id=f'order_id',
            args=[
                'a089ed783ecbcd8b9d09620dbea1e1bd',
                None,
                'done',
                'transaction_clear',
            ],
            kwargs={
                'transactions': [
                    {
                        'external_payment_id': (
                            'a089ed783ecbcd8b9d09620dbea1e1bd'
                        ),
                        'status': 'clear_success',
                        'payment_type': 'card',
                    },
                ],
                'created_at': {'$date': 1656948166509},
                'log_extra': {
                    '_link': '52a9e856c0164892b84bd9df39a41850',
                    'extdict': {
                        'uri': '/v2/invoice/update',
                        'method': 'debug_orders_shards',
                        'meta': [{'n': 'type', 'v': 'v2/invoice/update'}],
                        'parent_link': '71839bd06cd942f1917f33c8be026ed3',
                        'span_id': '6b157579dd802bd4',
                        'trace_id': 'f140db2b53db4e6e82c70bb85d8aa88b',
                        'operation': 'find_and_modify',
                        'has_shard_id': True,
                        'meta_order_id': '000a965636013cb99d8e1e302d873e6b',
                        'order_id': '000a965636013cb99d8e1e302d873e6b',
                        'parent_id': 'bff3e0667715364c',
                        'queue': 'transactions_events_clear',
                        'task_id': '000a965636013cb99d8e1e302d873e6b',
                        'stq_task_id': '000a965636013cb99d8e1e302d873e6b',
                        'stq_run_id': '7fe9c2b05f2645e49cc285f46f048724',
                        'purchase_token': '739cad45028d97aee6e13803a30679c0',
                    },
                    '_ot_ctx': {
                        'trace_id': 'f140db2b53db4e6e82c70bb85d8aa88b',
                        'span_id': 'bff3e0667715364c',
                    },
                },
            },
            expect_fail=False,
        )

    return wrapper


@pytest.mark.tariff_settings(filename='tariff_settings_moscow_tel_aviv.json')
@pytest.mark.parametrize(
    'order_proc_response,expected_query,order_archive_duplicate',
    [
        pytest.param(
            'order_proc_fiscal_card.json',
            C2C_CARD_FISCAL_REQUEST,
            False,
            id='card',
        ),
        pytest.param(
            'order_proc_fiscal_cash.json',
            C2C_CASH_FISCAL_REQUEST,
            False,
            id='cash',
        ),
        pytest.param(
            'order_proc_fiscal_card.json',
            C2C_CARD_FISCAL_REQUEST,
            True,
            id='card_bson_duplicate_key',
        ),
    ],
)
async def test_c2c_stq(
        mockserver,
        load_json,
        stq_runner,
        run_cargo_finance_taxi_invoice_update_callback,
        mock_fiscal_generate_transactions,
        mock_corp_info,
        mock_cardstorage,
        order_archive_mock,
        mock_py2_fiscal_data,
        order_proc_response,
        expected_query,
        order_archive_duplicate,
):
    invoice_json = load_json(f'response_t-ng_v2_invoice_retrieve_hold2.json')

    @mockserver.json_handler('/transactions/v2/invoice/retrieve')
    def _mock_invoice_retrieve(request):
        assert request.json['id'] == 'a089ed783ecbcd8b9d09620dbea1e1bd'
        return mockserver.make_response(json=invoice_json, status=200)

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal_phones(request):
        return mockserver.make_response(
            json={'id': 'eee', 'value': '+79001111111'}, status=200,
        )

    if order_archive_duplicate:
        # bson has duplicate order.discount.reason key
        @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
        def _mock_order_archive(request):
            return mockserver.make_response(
                open(
                    'services/cargo-finance/testsuite/static/'
                    'order_archive_with_doble_key_binary',
                    'rb',
                ).read(),
                status=200,
            )

    else:
        order_proc = load_json(order_proc_response)
        order_archive_mock.set_order_proc(order_proc)

    await run_cargo_finance_taxi_invoice_update_callback(stq_runner)

    assert mock_fiscal_generate_transactions.times_called == len(
        invoice_json['transactions'],
    )
    for _ in range(mock_fiscal_generate_transactions.times_called):
        request = mock_fiscal_generate_transactions.next_call()['request']
        assert (
            request.path == '/cargo-fiscal/internal/cargo-fiscal/receipts/'
            'delivery/taxiorders/generate-transaction'
        )
        assert request.query == {
            'topic_id': 'a089ed783ecbcd8b9d09620dbea1e1bd',
            'transaction_id': '725b676b22d6b43fb68b62059d0c5da8',
        }
        assert request.json == expected_query
