import datetime

import pytest

TEST_KWARGS_PURCHASE = {
    'transaction_id': 'transaction_id',
    'bank_uid': '024e7db5-9bd6-4f45-a1cd-2a442e15ffff',
    'mcc': 'mcc',
    'merchant_name': '123',
    'currency': 'RUB',
    'order_id': 'service_order_id',
    'trust_service_id': 'service_name',
    'timestamp': '2018-01-28T12:08:48.372+03:00',
    'amount': '100.00',
    'type': 'PURCHASE',
}

TEST_KWARGS_TOPUP = {
    'transaction_id': 'transaction_id',
    'bank_uid': '024e7db5-9bd6-4f45-a1cd-2a442e15ffff',
    'currency': 'RUB',
    'timestamp': '2018-01-28T12:08:48.372+03:00',
    'amount': '100.00',
    'type': 'WALLETC2ACREDIT',
    'order_id': 'service_order_id',
    'trust_service_id': 'service_name',
}

TEST_KWARGS_REFUND = {
    'transaction_id': 'refund_transaction_id',
    'bank_uid': '024e7db5-9bd6-4f45-a1cd-2a442e15ffff',
    'mcc': 'mcc',
    'merchant_name': '123',
    'currency': 'RUB',
    'order_id': 'service_order_id',
    'trust_service_id': 'service_name',
    'timestamp': '2018-01-28T12:08:48.372+03:00',
    'amount': '10',
    'type': 'REFUND',
    'parent_transaction_id': 'transaction_id',
}

TEST_KWARGS_REFUND_2 = {
    'transaction_id': 'refund_transaction_id_2',
    'bank_uid': '024e7db5-9bd6-4f45-a1cd-2a442e15ffff',
    'mcc': 'mcc',
    'merchant_name': '123',
    'currency': 'RUB',
    'order_id': 'service_order_id',
    'trust_service_id': 'service_name',
    'timestamp': '2018-01-28T12:08:48.372+03:00',
    'amount': '20',
    'type': 'REFUND',
    'parent_transaction_id': 'transaction_id',
}


def get_last_calc_trx(pgsql):
    cursor = pgsql['bank_cashback_processing'].cursor()
    cursor.execute(
        f'select transaction_id, timestamp, currency, '
        f'amount, rule_ids '
        f'from bank_cashback_processing.calculated_transactions '
        f'order by timestamp '
        f'desc ',
    )
    return cursor.fetchall()[0]


def select_trust_payload(pgsql, cashback_idempotency_token):
    cursor = pgsql['bank_cashback_processing'].cursor()
    cursor.execute(
        f'select trust_payload '
        f'from bank_cashback_processing.cashbacks '
        f'where idempotency_token = \'{cashback_idempotency_token}\'',
    )
    res = cursor.fetchall()[0][0]
    return res.get('pass_params').get('payload'), res.get('developer_payload')


def select_parent_purchase_token(pgsql, cashback_idempotency_token):
    cursor = pgsql['bank_cashback_processing'].cursor()
    cursor.execute(
        f'select parent_purchase_token '
        f'from bank_cashback_processing.cashbacks '
        f'where idempotency_token = \'{cashback_idempotency_token}\'',
    )
    return cursor.fetchall()[0][0]


def get_cashback_by_id_and_rule(pgsql, trx_id, rule_id):
    cursor = pgsql['bank_cashback_processing'].cursor()
    cursor.execute(
        f'select cashback_idempotency_token, amount, currency '
        f'from bank_cashback_processing.transaction_cashbacks trx_cb '
        f'join bank_cashback_processing.cashbacks cb '
        f'on (trx_cb.cashback_idempotency_token = cb.idempotency_token) '
        f'where transaction_id=\'{trx_id}\' and rule_id=\'{rule_id}\' ',
    )

    return cursor.fetchall()[0]


@pytest.mark.parametrize('kwargs', [TEST_KWARGS_PURCHASE, TEST_KWARGS_TOPUP])
async def test_new_cashback(
        stq_runner,
        _calculator_mock,
        _userinfo_mock,
        _blackbox_mock,
        pgsql,
        _stq_mock,
        kwargs,
):
    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=kwargs, expect_fail=False,
    )

    last_trx = get_last_calc_trx(pgsql)
    last_trx[4].sort()
    assert last_trx == (
        kwargs['transaction_id'],
        datetime.datetime.fromisoformat(TEST_KWARGS_PURCHASE['timestamp']),
        kwargs['currency'],
        kwargs['amount'],
        ['id_1', 'id_2'],
    )

    assert _calculator_mock.calc_handle.times_called == 1
    assert _userinfo_mock.buid_info_handle.times_called == 1
    assert _blackbox_mock.userinfo_handle.times_called == 1

    for i in range(1, 3):
        stq_schedule_next_call = _stq_mock.schedule_handle.next_call()
        stq_req_body = stq_schedule_next_call['request'].json
        assert (
            stq_schedule_next_call['queue_name']
            == 'bank_cashback_charge_processing'
        )
        assert 'idempotency_token' in stq_req_body['kwargs']
        cashback_idempotency_token = stq_req_body['kwargs'][
            'idempotency_token'
        ]
        gaap_payload, bank_data = select_trust_payload(
            pgsql, cashback_idempotency_token,
        )

        assert gaap_payload == {
            'cashback_service': 'bank',
            'cashback_type': 'transaction',
            'has_plus': True,
            'base_amount': '100.00',
            'currency': 'RUB',
            'bank_commission_irf_rate': '0.0117',
            'bank_commission_acquiring_rate': '0.013',
            'service_id': '1129',
            'issuer': 'issuer',
            'campaign_name': 'campaign_name',
            'ticket': 'ticket',
            'country': 'RU',
        }

        assert bank_data == {
            'transaction_id': 'transaction_id',
            'rule_id': f'id_{i}',
            'order_id': 'service_order_id',
            'trust_service_id': 'service_name',
        }

    assert get_cashback_by_id_and_rule(pgsql, 'transaction_id', 'id_1') == (
        'TRANSACTION-transaction_id-id_1',
        '1.11',
        kwargs['currency'],
    )
    assert get_cashback_by_id_and_rule(pgsql, 'transaction_id', 'id_2') == (
        'TRANSACTION-transaction_id-id_2',
        '11.1',
        kwargs['currency'],
    )


async def test_no_uid(
        stq_runner,
        mockserver,
        _calculator_mock,
        _blackbox_mock,
        pgsql,
        _stq_mock,
):
    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _mock_buid_info(request):
        return {'buid_info': {'buid': 'bank_uid'}}

    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=TEST_KWARGS_PURCHASE, expect_fail=True,
    )


async def test_no_cashback(
        mockserver, stq_runner, _userinfo_mock, _blackbox_mock, _stq_mock,
):
    @mockserver.json_handler(
        '/bank-cashback-calculator/cashback-calculator-internal/v1/calculate',
    )
    def _mock_internal_calculator(request):
        return mockserver.make_response(status=200)

    def make_checks():
        assert _mock_internal_calculator.has_calls
        assert _userinfo_mock.buid_info_handle.has_calls
        assert not _blackbox_mock.userinfo_handle.has_calls
        assert not _stq_mock.schedule_handle.has_calls

    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=TEST_KWARGS_PURCHASE, expect_fail=False,
    )
    make_checks()

    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=TEST_KWARGS_TOPUP, expect_fail=False,
    )
    make_checks()


async def test_conflict_trx(
        mockserver,
        stq_runner,
        _userinfo_mock,
        _stq_mock,
        _calculator_mock,
        _blackbox_mock,
        pgsql,
):
    cursor = pgsql['bank_cashback_processing'].cursor()
    cursor.execute(
        f'insert into bank_cashback_processing.calculated_transactions '
        f'( transaction_id, timestamp, currency, amount,'
        f'rule_ids, transaction_info, type, bank_uid, yandex_uid) '
        f'values (\'{TEST_KWARGS_PURCHASE["transaction_id"]}\', '
        f'\'{TEST_KWARGS_PURCHASE["timestamp"]}\', '
        f'\'{TEST_KWARGS_PURCHASE["currency"]}\', '
        f'\'{TEST_KWARGS_PURCHASE["amount"]}\', '
        f'\'{{"id_2"}}\', '
        f'\'{{"order_id":"{TEST_KWARGS_PURCHASE["order_id"]}", '
        f'"trust_service_id":"{TEST_KWARGS_PURCHASE["trust_service_id"]}", '
        f'"merchant_name":"{TEST_KWARGS_PURCHASE["merchant_name"]}", '
        f'"mcc":"{TEST_KWARGS_PURCHASE["mcc"]}"}}\'::jsonb, '
        f'\'{TEST_KWARGS_PURCHASE["type"]}\''
        f'::bank_cashback_processing.trx_type_t,'
        f'\'{TEST_KWARGS_PURCHASE["bank_uid"]}\', '
        f'\'yandex_uid\')',
    )

    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=TEST_KWARGS_PURCHASE, expect_fail=True,
    )

    assert _calculator_mock.calc_handle.times_called == 1
    assert _userinfo_mock.buid_info_handle.times_called == 1
    assert _blackbox_mock.userinfo_handle.has_calls
    assert not _stq_mock.schedule_handle.has_calls


async def test_refund_after_trx(
        stq_runner,
        _calculator_mock,
        _userinfo_mock,
        _blackbox_mock,
        pgsql,
        _stq_mock,
):
    cursor = pgsql['bank_cashback_processing'].cursor()

    def complete_charges():
        cursor.execute(
            f'update bank_cashback_processing.cashbacks '
            f'set status = \'PAYMENT_RECEIVED\', '
            f'purchase_token = \'purchase_token\' '
            f'where direction = '
            f'\'TOPUP\'::bank_cashback_processing.cashback_direction_t',
        )

    for _ in range(2):
        await stq_runner.bank_cashback_processing_transaction.call(
            task_id='purchase_id',
            kwargs=TEST_KWARGS_PURCHASE,
            expect_fail=False,
        )
        complete_charges()
        await stq_runner.bank_cashback_processing_transaction.call(
            task_id='refund_id', kwargs=TEST_KWARGS_REFUND, expect_fail=False,
        )
        await stq_runner.bank_cashback_processing_transaction.call(
            task_id='refund_id_2',
            kwargs=TEST_KWARGS_REFUND_2,
            expect_fail=False,
        )
        assert _stq_mock.schedule_handle.times_called == 6

        for _ in range(2):
            stq_schedule_next_call = _stq_mock.schedule_handle.next_call()
            stq_req_body = stq_schedule_next_call['request'].json
            assert (
                stq_schedule_next_call['queue_name']
                == 'bank_cashback_charge_processing'
            )
            id_token = stq_req_body['kwargs']['idempotency_token']
            assert (
                select_trust_payload(pgsql, id_token)[0]['base_amount']
                == '100.00'
            )

        for i in range(1, 3):
            stq_schedule_next_call = _stq_mock.schedule_handle.next_call()
            assert (
                stq_schedule_next_call['queue_name']
                == 'bank_cashback_processing_refunds'
            )
            id_token = (
                f'TRANSACTION-{TEST_KWARGS_REFUND["transaction_id"]}-id_{i}'
            )
            assert (
                select_parent_purchase_token(pgsql, id_token)
                == 'purchase_token'
            )

        for i in range(1, 3):
            stq_schedule_next_call = _stq_mock.schedule_handle.next_call()
            assert (
                stq_schedule_next_call['queue_name']
                == 'bank_cashback_processing_refunds'
            )
            id_token = (
                f'TRANSACTION-{TEST_KWARGS_REFUND_2["transaction_id"]}-id_{i}'
            )
            assert (
                select_parent_purchase_token(pgsql, id_token)
                == 'purchase_token'
            )

    cursor.execute(f'select * from bank_cashback_processing.cashbacks ')
    assert len(cursor.fetchall()) == 7
    cursor.execute(
        f'select * from bank_cashback_processing.transaction_cashbacks ',
    )
    assert len(cursor.fetchall()) == 7
    cursor.execute(
        f'select * from bank_cashback_processing.calculated_transactions ',
    )
    assert len(cursor.fetchall()) == 4


async def test_blocking_cashbacks(
        stq_runner,
        _calculator_mock,
        _userinfo_mock,
        _blackbox_mock,
        pgsql,
        _stq_mock,
):
    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='purchase_id', kwargs=TEST_KWARGS_PURCHASE, expect_fail=False,
    )
    assert _stq_mock.schedule_handle.has_calls
    assert not _stq_mock.reschedule_handle.has_calls
    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='purchase_id', kwargs=TEST_KWARGS_REFUND, expect_fail=False,
    )
    assert _stq_mock.reschedule_handle.has_calls


async def test_saved_transaction(
        mockserver,
        stq_runner,
        _userinfo_mock,
        _stq_mock,
        _calculator_mock,
        _blackbox_mock,
        pgsql,
):
    cursor = pgsql['bank_cashback_processing'].cursor()
    cursor.execute(
        f'insert into bank_cashback_processing.calculated_transactions '
        f'(transaction_id, timestamp, currency, amount,'
        f'rule_ids, transaction_info, type, bank_uid, yandex_uid) '
        f'values (\'{TEST_KWARGS_PURCHASE["transaction_id"]}\','
        f' \'{TEST_KWARGS_PURCHASE["timestamp"]}\','
        f'\'{TEST_KWARGS_PURCHASE["currency"]}\','
        f' \'{TEST_KWARGS_PURCHASE["amount"]}\', '
        f'\'{{"id_2", "id_1"}}\','
        f'\'{{"order_id":"{TEST_KWARGS_PURCHASE["order_id"]}", '
        f'"trust_service_id":"{TEST_KWARGS_PURCHASE["trust_service_id"]}", '
        f'"merchant_name":"{TEST_KWARGS_PURCHASE["merchant_name"]}", '
        f'"mcc":"{TEST_KWARGS_PURCHASE["mcc"]}"}}\'::jsonb, '
        f'\'{TEST_KWARGS_PURCHASE["type"]}\''
        f'::bank_cashback_processing.trx_type_t,'
        f'\'{TEST_KWARGS_PURCHASE["bank_uid"]}\', '
        f'\'yandex_uid\')',
    )

    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=TEST_KWARGS_PURCHASE, expect_fail=False,
    )

    assert _calculator_mock.calc_handle.times_called == 1
    assert _userinfo_mock.buid_info_handle.times_called == 1
    assert _blackbox_mock.userinfo_handle.has_calls
    assert _stq_mock.schedule_handle.times_called == 2


@pytest.mark.parametrize(
    'trx_type, kwargs, queue_name',
    [
        ('PURCHASE', TEST_KWARGS_PURCHASE, 'bank_cashback_charge_processing'),
        ('REFUND', TEST_KWARGS_REFUND, 'bank_cashback_processing_refunds'),
    ],
)
async def test_processed_transaction_call_tasks(
        mockserver,
        trx_type,
        stq_runner,
        _userinfo_mock,
        _stq_mock,
        _calculator_mock,
        _blackbox_mock,
        pgsql,
        kwargs,
        queue_name,
):
    cursor = pgsql['bank_cashback_processing'].cursor()

    cursor.execute(
        f'insert into bank_cashback_processing.calculated_transactions '
        f'(transaction_id, timestamp, currency, amount,'
        f'rule_ids, transaction_info, type, bank_uid, yandex_uid) '
        f'values (\'{TEST_KWARGS_PURCHASE["transaction_id"]}\','
        f' \'{TEST_KWARGS_PURCHASE["timestamp"]}\','
        f'\'{TEST_KWARGS_PURCHASE["currency"]}\','
        f' \'{TEST_KWARGS_PURCHASE["amount"]}\', '
        f'\'{{"id_2", "id_1"}}\','
        f'\'{{"order_id":"{TEST_KWARGS_PURCHASE["order_id"]}", '
        f'"trust_service_id":"{TEST_KWARGS_PURCHASE["trust_service_id"]}", '
        f'"merchant_name":"{TEST_KWARGS_PURCHASE["merchant_name"]}", '
        f'"mcc":"{TEST_KWARGS_PURCHASE["mcc"]}"}}\'::jsonb, '
        f'\'{TEST_KWARGS_PURCHASE["type"]}\''
        f'::bank_cashback_processing.trx_type_t,'
        f'\'{TEST_KWARGS_PURCHASE["bank_uid"]}\', '
        f'\'yandex_uid\')',
    )

    for i in {1, 2}:
        cursor.execute(
            f'insert into bank_cashback_processing.cashbacks '
            f'(idempotency_token,'
            f'cashback_type, direction, bank_uid, '
            f'yandex_uid, amount,'
            f'currency, status, trust_payload) '
            f'values (\'idempotency_token_{i}\','
            f' \'TRANSACTION\'::bank_cashback_processing.cashback_type_t,'
            f' \'TOPUP\'::bank_cashback_processing.cashback_direction_t,'
            f'\'bank_uid\', \'yandex_uid\', '
            f'\'100\','
            f'\'RUB\','
            f'\'PAYMENT_RECEIVED\','
            f'\'{{}}\')',
        )

        cursor.execute(
            f'insert into bank_cashback_processing.transaction_cashbacks '
            f'(transaction_id, rule_id, cashback_idempotency_token) '
            f'values ('
            f'\'{TEST_KWARGS_PURCHASE["transaction_id"]}\','
            f'\'id_{i}\', '
            f'\'idempotency_token_{i}\')',
        )

        if trx_type == 'REFUND':
            cursor.execute(
                f'insert into bank_cashback_processing.cashbacks '
                f'(idempotency_token, '
                f'cashback_type, direction, bank_uid, '
                f'yandex_uid, amount,'
                f'currency, trust_payload, status, parent_idempotency_token) '
                f'values (\'refund_idempotency_token_{i}\','
                f' \'TRANSACTION\'::bank_cashback_processing.cashback_type_t,'
                f' \'REFUND\'::bank_cashback_processing.cashback_direction_t,'
                f'\'bank_uid\', \'yandex_uid\', '
                f'\'5\','
                f'\'RUB\','
                f'\'{{}}\','
                f'\'PAYMENT_RECEIVED\','
                f'\'idempotency_token_{i}\')',
            )

            cursor.execute(
                f'insert into bank_cashback_processing.transaction_cashbacks '
                f'(transaction_id, rule_id, '
                f'cashback_idempotency_token, parent_transaction_id) '
                f'values ('
                f'\'{TEST_KWARGS_REFUND["transaction_id"]}\','
                f'\'id_{i}\', '
                f'\'refund_idempotency_token_{i}\','
                f'\'{TEST_KWARGS_PURCHASE["transaction_id"]}\')',
            )

    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=kwargs, expect_fail=False,
    )

    assert _calculator_mock.calc_handle.times_called == 1
    assert _userinfo_mock.buid_info_handle.times_called == 1
    assert _stq_mock.schedule_handle.times_called == 2

    assert _stq_mock.schedule_handle.next_call()['queue_name'] == queue_name


async def test_no_plus(
        mockserver,
        stq_runner,
        pgsql,
        _calculator_mock,
        _userinfo_mock,
        _blackbox_mock,
        _stq_mock,
):
    @mockserver.json_handler('/blackbox/blackbox')
    def _mock_blackbox(request):
        return {'users': [{'id': 'yandex_uid', 'attributes': {}}]}

    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=TEST_KWARGS_PURCHASE, expect_fail=False,
    )

    assert _calculator_mock.calc_handle.times_called == 1
    assert _userinfo_mock.buid_info_handle.times_called == 1
    assert _mock_blackbox.times_called == 1

    stq_schedule_next_call = _stq_mock.schedule_handle.next_call()
    stq_request_body = stq_schedule_next_call['request'].json

    assert (
        stq_schedule_next_call['queue_name']
        == 'bank_cashback_charge_processing'
    )
    cashback_idempotency_token = stq_request_body['kwargs'][
        'idempotency_token'
    ]
    assert select_trust_payload(pgsql, cashback_idempotency_token) == (
        {
            'cashback_service': 'bank',
            'cashback_type': 'transaction',
            'has_plus': False,
            'base_amount': '100.00',
            'currency': 'RUB',
            'bank_commission_irf_rate': '0.0117',
            'bank_commission_acquiring_rate': '0.013',
            'service_id': '1129',
            'issuer': 'issuer',
            'campaign_name': 'campaign_name',
            'ticket': 'ticket',
            'country': 'RU',
        },
        {
            'transaction_id': 'transaction_id',
            'rule_id': 'id_1',
            'order_id': 'service_order_id',
            'trust_service_id': 'service_name',
        },
    )


async def test_calculator_request(
        mockserver,
        stq_runner,
        _userinfo_mock,
        _blackbox_mock,
        _calculator_mock,
        _stq_mock,
        monkeypatch,
):
    def to_datetime(datetime_str):
        return datetime.datetime.fromisoformat(
            TEST_KWARGS_PURCHASE['timestamp'],
        )

    @mockserver.json_handler(
        '/bank-cashback-calculator/cashback-calculator-internal/v1/calculate',
    )
    def _mock_calc(request):
        fields = ('merchant_name', 'mcc', 'rule_ids')
        for field in fields:
            assert request.json.get(field) == TEST_KWARGS_PURCHASE.get(field)
        assert to_datetime(request.json['timestamp']) == to_datetime(
            TEST_KWARGS_PURCHASE['timestamp'],
        )
        assert request.json['yandex_uid'] == 'yandex_uid'
        assert (
            request.json['money']['amount'] == TEST_KWARGS_PURCHASE['amount']
        )
        assert (
            request.json['money']['currency']
            == TEST_KWARGS_PURCHASE['currency']
        )
        return mockserver.make_response(
            status=200,
            json={
                'rules': [
                    {
                        'rule_id': 'id_1',
                        'ticket': 'ticket',
                        'issuer': 'issuer',
                        'campaign_name': 'campaign_name',
                        'cashback': {'amount': '1.11', 'currency': 'RUB'},
                    },
                ],
            },
        )

    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=TEST_KWARGS_PURCHASE, expect_fail=False,
    )

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _mock_buid_info(request):
        return {
            'buid_info': {
                'buid': '024e7db5-9bd6-4f45-a1cd-2a442e15ffff',
                'yandex_uid': 'yandex_uid_',
                'phone_id': 'phone_id_',
            },
        }

    refund_kwargs = {
        'transaction_id': 'refund_transaction_id',
        'bank_uid': '024e7db5-9bd6-4f45-a1cd-2a442e15ffff',
        'mcc': 'mcc_',
        'merchant_name': '123_',
        'currency': 'RUB',
        'order_id': 'service_order_id',
        'trust_service_id': 'service_name',
        'timestamp': '2018-02-28T12:08:48.372+03:00',
        'amount': '10',
        'type': 'REFUND',
        'parent_transaction_id': 'transaction_id',
    }
    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=refund_kwargs, expect_fail=False,
    )


async def test_invalid_precision(stq_runner, monkeypatch):
    monkeypatch.setitem(TEST_KWARGS_PURCHASE, 'amount', '100.000')
    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=TEST_KWARGS_PURCHASE, expect_fail=True,
    )


async def test_unsupported_type(stq_runner, monkeypatch):
    monkeypatch.setitem(TEST_KWARGS_PURCHASE, 'type', 'PINCHANGE')
    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=TEST_KWARGS_PURCHASE, expect_fail=False,
    )


@pytest.mark.parametrize('bad_currency', ['EUR', 'BLAHBLAH'])
async def test_unsupported_currency(stq_runner, monkeypatch, bad_currency):
    monkeypatch.setitem(TEST_KWARGS_PURCHASE, 'currency', bad_currency)
    await stq_runner.bank_cashback_processing_transaction.call(
        task_id='id', kwargs=TEST_KWARGS_PURCHASE, expect_fail=False,
    )
