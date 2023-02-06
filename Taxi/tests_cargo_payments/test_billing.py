import re

import pytest


@pytest.fixture(name='get_billing_tasks')
async def _get_billing_tasks(pgsql):
    def wrapper():
        cursor = pgsql['cargo_payments'].cursor()
        cursor.execute(
            'SELECT * FROM cargo_payments.billing_tasks_history',
            ' ORDER BY history_event_id',
        )
        return list(row for row in cursor)

    return wrapper


async def test_worker_with_state(
        run_transactions_scanner,
        state_payment_confirmed,
        taxi_cargo_payments,
        get_worker_state,
        load_json_var,
):
    state = await state_payment_confirmed()

    await run_transactions_scanner()
    worker_state = get_worker_state('cargo-payments-transactions-scanner')
    assert not worker_state

    await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_transactions_scanner()
    worker_state = get_worker_state('cargo-payments-transactions-scanner')
    assert len(worker_state) == 1
    assert worker_state[0]['last_event_id'] == 1


async def test_billing_task_simple(
        run_transactions_scanner,
        state_payment_confirmed,
        taxi_cargo_payments,
        get_worker_state,
        load_json_var,
        get_billing_tasks,
):
    state = await state_payment_confirmed()

    await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_transactions_scanner()
    tasks = get_billing_tasks()
    assert len(tasks) == 1

    await run_transactions_scanner()
    tasks = get_billing_tasks()
    assert len(tasks) == 1


@pytest.mark.config(
    CARGO_PAYMENTS_SETTINGS={
        'billing.enabled': '1',
        'billing.transactions_scanner.order_types': (
            'b2b_user_on_delivery_payment_fee,user_on_delivery_payment'
        ),
        'billing.comission.link': '0.01',
        'billing.comission.tariff_name': 'test',
    },
    CARGO_PAYMENTS_COMISSIONS={
        'default': [
            {
                'comission_link': '0.01',
                'comission_card': '0.02',
                'comission_cash': '0.03',
            },
        ],
    },
)
async def test_send_billing_order_comission(
        run_transactions_scanner,
        state_payment_confirmed,
        taxi_cargo_payments,
        get_worker_state,
        load_json_var,
        get_billing_tasks,
        run_billing_tasks_checker,
        stq,
        stq_runner,
        mock_corp_api,
        active_contracts,
        billing_orders_process,
        mock_agglomeration,
        default_corp_client_id,
):
    state = await state_payment_confirmed()

    await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_transactions_scanner()
    tasks = get_billing_tasks()
    assert len(tasks) == 2
    assert tasks[1][4] == 'new'
    assert tasks[1][5] == 'b2b_user_on_delivery_payment_fee'
    assert tasks[1][8] == '0.4000'

    await run_billing_tasks_checker()
    tasks = get_billing_tasks()
    assert len(tasks) == 2
    assert tasks[0][4] == 'processing'
    assert tasks[1][4] == 'processing'

    await stq_runner.cargo_payments_send_billing_data.call(
        task_id='%s/%d' % (state.payment_id, 1),
        kwargs={
            'order_id': state.payment_id,
            'event_id': 2,
            'order_type': 'b2b_user_on_delivery_payment_fee',
        },
    )

    tasks = get_billing_tasks()
    assert len(tasks) == 2
    assert tasks[1][4] == 'approved'

    billing_report = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/v1/billing/report',
        json={'order_id': '456'},
        headers={'X-B2B-Client-Id': default_corp_client_id},
    )

    assert billing_report.json()['sum'] == '40'
    assert billing_report.json()['transactions'][0]['payment_amount'] == '40'
    assert (
        billing_report.json()['transactions'][0]['comission_amount'] == '0.4'
    )
    assert billing_report.json()['transactions'][0]['comission'] == '0.01'
    assert billing_report.json()['transactions'][0]['status'] == 'processing'


async def test_send_billing_order_simple(
        run_transactions_scanner,
        state_payment_confirmed,
        taxi_cargo_payments,
        get_worker_state,
        load_json_var,
        get_billing_tasks,
        run_billing_tasks_checker,
        stq,
        stq_runner,
        mock_corp_api,
        active_contracts,
        billing_orders_process,
):
    state = await state_payment_confirmed()

    await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_transactions_scanner()
    tasks = get_billing_tasks()
    assert len(tasks) == 1
    assert tasks[0][4] == 'new'
    assert tasks[0][14]['payment_method'] == 'link'

    await run_billing_tasks_checker()
    tasks = get_billing_tasks()
    assert len(tasks) == 1
    assert tasks[0][4] == 'processing'

    assert stq.cargo_payments_send_billing_data.times_called == 1
    task_data = stq.cargo_payments_send_billing_data.next_call()
    assert task_data['queue'] == 'cargo_payments_send_billing_data'
    assert task_data['kwargs']['event_id'] == 1
    assert task_data['kwargs']['order_id'] == state.payment_id
    assert task_data['kwargs']['order_type'] == 'user_on_delivery_payment'

    await stq_runner.cargo_payments_send_billing_data.call(
        task_id='%s/%d' % (state.payment_id, 1),
        kwargs={
            'order_id': state.payment_id,
            'event_id': 1,
            'order_type': 'user_on_delivery_payment',
        },
    )

    tasks = get_billing_tasks()
    assert len(tasks) == 1
    assert tasks[0][4] == 'approved'

    await run_billing_tasks_checker()
    tasks = get_billing_tasks()
    assert len(tasks) == 1
    assert tasks[0][4] == 'approved'
    assert stq.cargo_payments_send_billing_data.times_called == 0


async def test_send_billing_order_refund(
        run_transactions_scanner,
        state_payment_confirmed,
        taxi_cargo_payments,
        get_worker_state,
        load_json_var,
        get_billing_tasks,
        run_billing_tasks_checker,
        stq,
        stq_runner,
        mock_corp_api,
        active_contracts,
        billing_orders_process,
        cancel_payment,
        run_operations_executor,
        default_corp_client_id,
):
    state = await state_payment_confirmed()

    await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_transactions_scanner()
    await run_billing_tasks_checker()
    tasks = get_billing_tasks()
    assert len(tasks) == 1
    assert tasks[0][4] == 'processing'

    assert stq.cargo_payments_send_billing_data.times_called == 1
    task_data = stq.cargo_payments_send_billing_data.next_call()
    assert task_data['queue'] == 'cargo_payments_send_billing_data'
    assert task_data['kwargs']['event_id'] == 1
    assert task_data['kwargs']['order_id'] == state.payment_id
    assert task_data['kwargs']['order_type'] == 'user_on_delivery_payment'

    await stq_runner.cargo_payments_send_billing_data.call(
        task_id='%s/%d' % (state.payment_id, 1),
        kwargs={
            'order_id': state.payment_id,
            'event_id': 1,
            'order_type': 'user_on_delivery_payment',
        },
    )

    tasks = get_billing_tasks()
    assert len(tasks) == 1
    assert tasks[0][4] == 'approved'

    billing_order = billing_orders_process.last_request['orders'][0]
    assert billing_order['external_ref'] == '1'
    assert billing_order['data']['event_version'] == 1
    assert billing_order['data']['entries'][0]['amount'] == '40'
    assert billing_order['data']['payments'][0]['amount'] == '40'

    await cancel_payment(payment_id=state.payment_id)
    await run_operations_executor()
    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'refund_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200
    await run_operations_executor()

    await run_transactions_scanner()
    await run_billing_tasks_checker()
    tasks = get_billing_tasks()
    assert len(tasks) == 2
    assert tasks[1][4] == 'processing'

    await stq_runner.cargo_payments_send_billing_data.call(
        task_id='%s/%d' % (state.payment_id, 1),
        kwargs={
            'order_id': state.payment_id,
            'event_id': 2,
            'order_type': 'user_on_delivery_payment',
        },
    )

    billing_order = billing_orders_process.last_request['orders'][0]
    assert billing_order['external_ref'] == '2'
    assert billing_order['data']['event_version'] == 2
    assert not billing_order['data']['entries']
    assert not billing_order['data']['payments']

    tasks = get_billing_tasks()
    assert len(tasks) == 2
    assert tasks[1][4] == 'approved'

    billing_report = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/v1/billing/report',
        json={'order_id': '456'},
        headers={'X-B2B-Client-Id': default_corp_client_id},
    )

    assert billing_report.json()['sum'] == '0'
    assert billing_report.json()['transactions'][0]['order_amount'] == '40'
    assert billing_report.json()['transactions'][0]['payment_amount'] == '0'
    assert billing_report.json()['transactions'][0]['status'] == 'approved'


async def test_billing_report_csv_simple(
        run_transactions_scanner,
        state_payment_confirmed,
        taxi_cargo_payments,
        get_worker_state,
        load_json_var,
        get_billing_tasks,
        default_corp_client_id,
):
    state = await state_payment_confirmed()

    await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_transactions_scanner()
    tasks = get_billing_tasks()
    assert len(tasks) == 1

    billing_report = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/v1/billing/report_csv',
        json={'order_id': '456'},
        headers={'X-B2B-Client-Id': default_corp_client_id},
    )
    # we insert two BOMs on back, because front side loses the first one
    # for some reason. So let's imagine that we have only one BOM
    billing_report_content = billing_report.content[2:]

    assert bytes(billing_report_content)[:2] == b'\xFF\xFE'  # BOM
    assert billing_report_content.decode('utf_16') == billing_report_content[
        2:
    ].decode('utf_16_le')
    assert (
        billing_report_content.decode('utf_16').encode('utf_16_le')
        == billing_report_content[2:]
    )
    date_format = r'\d{4}-\d{2}-\d{2}'
    time_format = r'\d{2}:\d{2}:\d{2}'
    rows = billing_report_content.decode('utf_16').split('\n')
    assert rows[0] == '\t'.join(
        [
            'Тип транзакции',
            'Идентификатор платежа',
            'Сумма заказа',
            'Сумма платежа',
            'Валюта',
            'Статус',
            'Дата заказа',
            'Время заказа',
            'Дата платежа',
            'Время платежа',
            'Дата запроса платежной системы',
            'Время запроса платежной системы',
            'Способ оплаты',
            'Процент комиссии',
            'Комиссия',
            'Идентификатор платежного документа',
        ],
    )
    assert re.fullmatch(
        '\t'.join(
            [
                'payment',
                '456',
                '40',
                '40',
                'RUB',
                'new',
                date_format,
                time_format,
                date_format,
                time_format,
                '',
                '',
                'link',
                '0',
                '0',
                '',
            ],
        ),
        rows[1],
    )


async def test_billing_report_json_simple(
        run_transactions_scanner,
        state_payment_confirmed,
        taxi_cargo_payments,
        get_worker_state,
        load_json_var,
        get_billing_tasks,
        default_corp_client_id,
):
    state = await state_payment_confirmed()

    await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_transactions_scanner()
    tasks = get_billing_tasks()
    assert len(tasks) == 1

    billing_report = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/v1/billing/report',
        json={'order_id': '456'},
        headers={'X-B2B-Client-Id': default_corp_client_id},
    )

    assert billing_report.json()['sum'] == '40'
    assert billing_report.json()['transactions'][0]['order_amount'] == '40'
    assert billing_report.json()['transactions'][0]['payment_amount'] == '40'
    assert billing_report.json()['transactions'][0]['status'] == 'new'
    assert billing_report.json()['transactions'][0]['comission_amount'] == '0'


@pytest.mark.config(
    CARGO_PAYMENTS_SETTINGS={
        'billing.enabled': '1',
        'billing.comission.tariff_name': 'test',
    },
)
async def test_register_payment_task(
        taxi_cargo_payments,
        get_worker_state,
        get_billing_tasks,
        default_corp_client_id,
        run_billing_tasks_checker,
        stq,
        stq_runner,
        mock_corp_api,
        active_contracts,
        billing_orders_process,
        mock_agglomeration,
        register_billing_tasks,
):
    await register_billing_tasks()

    tasks = get_billing_tasks()
    assert len(tasks) == 2

    billing_report = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/v1/billing/report',
        json={'order_id': '12445'},
        headers={'X-B2B-Client-Id': default_corp_client_id},
    )

    assert billing_report.json()['sum'] == '60.8'
    assert billing_report.json()['transactions'][0]['order_amount'] == '60.8'
    assert billing_report.json()['transactions'][0]['payment_amount'] == '60.8'
    assert billing_report.json()['transactions'][0]['status'] == 'new'
    assert (
        billing_report.json()['transactions'][0]['comission_amount'] == '6.08'
    )
    assert billing_report.json()['transactions'][0]['comission'] == '0.1'

    await run_billing_tasks_checker()
    tasks = get_billing_tasks()
    assert len(tasks) == 2
    assert tasks[0][4] == 'processing'
    assert tasks[1][4] == 'processing'

    assert stq.cargo_payments_send_billing_data.times_called == 2

    await stq_runner.cargo_payments_send_billing_data.call(
        task_id='%s/%d' % ('12445', 1),
        kwargs={
            'order_id': '12445',
            'event_id': 1,
            'order_type': 'user_on_delivery_payment',
        },
    )

    await stq_runner.cargo_payments_send_billing_data.call(
        task_id='%s/%d' % ('12445', 2),
        kwargs={
            'order_id': '12445',
            'event_id': 2,
            'order_type': 'b2b_user_on_delivery_payment_fee',
        },
    )

    tasks = get_billing_tasks()
    assert len(tasks) == 2
    assert tasks[0][4] == 'approved'
    assert tasks[1][4] == 'approved'

    billing_report = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/v1/billing/report',
        json={'order_id': '12445'},
        headers={'X-B2B-Client-Id': default_corp_client_id},
    )

    assert billing_report.json()['sum'] == '60.8'
    assert billing_report.json()['transactions'][0]['order_amount'] == '60.8'
    assert billing_report.json()['transactions'][0]['payment_amount'] == '60.8'
    assert billing_report.json()['transactions'][0]['status'] == 'approved'
    assert (
        billing_report.json()['transactions'][0]['comission_amount'] == '6.08'
    )
    assert billing_report.json()['transactions'][0]['comission'] == '0.1'


@pytest.mark.parametrize('cargo_finance_response', [200, 400, 404, 500])
@pytest.mark.config(
    CARGO_FINANCE_BILLING_ORDERS_REVISE_JOB_SETTINGS={
        'orders_sending_settings_by_migration_name': {
            'ndd': {'allow_revises': True},
        },
    },
)
async def test_cargo_finance_revise(
        run_transactions_scanner,
        state_payment_confirmed,
        taxi_cargo_payments,
        get_worker_state,
        load_json_var,
        get_billing_tasks,
        run_billing_tasks_checker,
        stq,
        stq_runner,
        mock_corp_api,
        active_contracts,
        billing_orders_process,
        mockserver,
        cargo_finance_response,
):
    @mockserver.json_handler(
        '/cargo-finance/internal/cargo-finance/ndd/billing-order/revise',
    )
    def _billing_order_revise(request):
        return mockserver.make_response(status=cargo_finance_response)

    state = await state_payment_confirmed()

    await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_transactions_scanner()
    tasks = get_billing_tasks()
    assert len(tasks) == 1
    assert tasks[0][4] == 'new'
    assert tasks[0][14]['payment_method'] == 'link'

    await run_billing_tasks_checker()
    tasks = get_billing_tasks()
    assert len(tasks) == 1
    assert tasks[0][4] == 'processing'

    assert stq.cargo_payments_send_billing_data.times_called == 1
    task_data = stq.cargo_payments_send_billing_data.next_call()
    assert task_data['queue'] == 'cargo_payments_send_billing_data'
    assert task_data['kwargs']['event_id'] == 1
    assert task_data['kwargs']['order_id'] == state.payment_id
    assert task_data['kwargs']['order_type'] == 'user_on_delivery_payment'

    await stq_runner.cargo_payments_send_billing_data.call(
        task_id='%s/%d' % (state.payment_id, 1),
        kwargs={
            'order_id': state.payment_id,
            'event_id': 1,
            'order_type': 'user_on_delivery_payment',
        },
    )

    tasks = get_billing_tasks()
    assert len(tasks) == 1
    assert tasks[0][4] == 'approved'

    await run_billing_tasks_checker()
    tasks = get_billing_tasks()
    assert len(tasks) == 1
    assert tasks[0][4] == 'approved'
    assert stq.cargo_payments_send_billing_data.times_called == 0

    assert _billing_order_revise.times_called == 1
