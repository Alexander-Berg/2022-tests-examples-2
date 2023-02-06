import datetime
import json

import pytest


@pytest.fixture(name='mock_transactions_invoice')
def _mock_transactions_invoice(mockserver, load_json):
    def _setup_transactions(debt=None):
        if debt is None:
            debt = {'ride': '123'}
        invoice = dict(
            id='invoice_id',
            invoice_due='2020-01-21T00:00:00+00:00',
            currency='RUB',
            status='clear-failed',
            sum_to_pay={},
            cleared={},
            debt=debt,
            held={},
            operation_info={},
            transactions=[],
            yandex_uid='123',
        )

        @mockserver.json_handler('/transactions/invoice/retrieve')
        def _invoice_retrieve(request):
            return mockserver.make_response(json.dumps(invoice), 200)

        response_v2 = load_json(
            'transactions/response_invoice_retrive_v2.json',
        )
        if debt is not None:
            card_debts_list = []
            for item_id, amount in debt.items():
                card_debts_list.append({'item_id': item_id, 'amount': amount})
            response_v2['debt'] = [
                {'items': card_debts_list, 'payment_type': 'card'},
            ]

        @mockserver.json_handler('/transactions/v2/invoice/retrieve')
        def _invoice_retrieve(request):
            return mockserver.make_response(json.dumps(response_v2), 200)

    return _setup_transactions


@pytest.mark.parametrize(
    (),
    (
        pytest.param(
            marks=pytest.mark.config(DEBTS_USE_V2_TRANSACTIONS_API=False),
            id='v1_transactions_api',
        ),
        pytest.param(
            marks=pytest.mark.config(DEBTS_USE_V2_TRANSACTIONS_API=True),
            id='v2_transactions_api',
        ),
    ),
)
@pytest.mark.parametrize(
    'debt, expected_debt',
    [
        pytest.param({'ride': '123.45'}, '123.45', id='ride'),
        pytest.param({'cashback': '6.15'}, '6.15', id='cashback'),
        pytest.param(
            {'ride': '123.45', 'cashback': '6.15'},
            '129.6',
            id='ride&cashback',
        ),
    ],
)
@pytest.mark.parametrize(
    'payment_type, expected_uid, expected_phone',
    [
        pytest.param(
            'card', '1234567', '123456781234567812345678', id='regular',
        ),
        pytest.param('coop_account', 'shared_uid', 'shared_phone', id='coop'),
    ],
)
async def test_debts_processing_happy_path_set(
        stq,
        stq_runner,
        mockserver,
        debt,
        expected_debt,
        payment_type,
        expected_uid,
        expected_phone,
        mock_transactions_invoice,
        mock_archive_order,
):
    mock_transactions_invoice(debt)
    mock_archive_order(payment_type=payment_type)

    @mockserver.json_handler(
        '/taxi-shared-payments/internal/coop_account/owner_info',
    )
    def _get_account_owner_info(request):
        result = dict(yandex_uid='shared_uid', phone_id='shared_phone')
        return mockserver.make_response(json.dumps(result), 200)

    # TODO: improve and use mock_v1_debts from conftest instead
    @mockserver.json_handler('/debts/v1/debts')
    def _v1_debts(request):
        expected_patch = dict(
            action='set_debt',
            phone_id=expected_phone,
            yandex_uid=expected_uid,
            value=expected_debt,
            currency='RUB',
            brand='yataxi',
            patch_time='2020-01-20T00:00:00+00:00',
            created_at='2020-02-20T00:00:00+00:00',
            payment_type=payment_type,
        )
        assert request.args['order_id'] == 'happy_path'
        assert request.json == expected_patch
        return mockserver.make_response(status=200)

    task_id = '123456abcdef'
    args = ('happy_path', 'set_debt', datetime.datetime(2020, 1, 20))
    await stq_runner.debts_processing.call(task_id=task_id, args=args)
    assert not stq.debts_processing.times_called


@pytest.mark.parametrize(
    'payment_type, expected_uid, expected_phone',
    [
        pytest.param('', '1234567', '123456781234567812345678', id='regular'),
        pytest.param('coop_account', 'shared_uid', 'shared_phone', id='coop'),
    ],
)
async def test_debts_processing_happy_path_reset(
        stq,
        stq_runner,
        mockserver,
        payment_type,
        expected_uid,
        expected_phone,
        mock_transactions_invoice,
        mock_archive_order,
):
    mock_transactions_invoice({'ride': '50', 'cashback': '0'})
    mock_archive_order(payment_type=payment_type)

    @mockserver.json_handler(
        '/taxi-shared-payments/internal/coop_account/owner_info',
    )
    def _get_account_owner_info(request):
        result = dict(yandex_uid='shared_uid', phone_id='shared_phone')
        return mockserver.make_response(json.dumps(result), 200)

    # TODO: improve and use mock_v1_debts from conftest instead
    @mockserver.json_handler('/debts/v1/debts')
    def _v1_debts(request):
        expected_patch = dict(
            action='reset_debt',
            reason_code='just I want so',
            phone_id=expected_phone,
            yandex_uid=expected_uid,
            currency='RUB',
            brand='yataxi',
            patch_time='2020-01-20T00:00:00+00:00',
            created_at='2020-02-20T00:00:00+00:00',
            payment_type=payment_type,
        )
        assert request.args['order_id'] == 'happy_path'
        assert request.json == expected_patch
        return mockserver.make_response(status=200)

    task_id = '123456abcdef'
    args = (
        'happy_path',
        'reset_debt',
        datetime.datetime(2020, 1, 20),
        'just I want so',
    )
    await stq_runner.debts_processing.call(task_id=task_id, args=args)
    assert not stq.debts_processing.times_called


@pytest.mark.parametrize(
    'debt, expected_debt',
    [
        pytest.param(
            {'ride': '123.45', 'cashback': '6.15'},
            '129.6',
            id='ride&cashback',
        ),
    ],
)
@pytest.mark.parametrize(
    'payment_type, expected_uid, expected_phone, locked_phone_id, is_owner',
    [
        pytest.param(
            'card',
            'family_owner_uid',
            'family_owner_phone_id',
            'family_owner_phone_id',
            False,
            id='family_member',
        ),
        pytest.param(
            'card',
            '1234567',
            '123456781234567812345678',
            None,
            False,
            id='no_phone_id_arg',
        ),
        pytest.param(
            'card',
            '1234567',
            '123456781234567812345678',
            None,
            True,
            id='is_owner',
        ),
    ],
)
async def test_debts_processing_family_account(
        stq,
        stq_runner,
        mockserver,
        debt,
        expected_debt,
        payment_type,
        expected_uid,
        expected_phone,
        locked_phone_id,
        is_owner,
        mock_transactions_invoice,
        mock_archive_order,
):
    mock_transactions_invoice(debt)
    mock_archive_order(is_owner=is_owner, payment_type='card')

    # TODO: improve and use mock_v1_debts from conftest instead
    @mockserver.json_handler('/debts/v1/debts')
    def _v1_debts(request):
        expected_patch = dict(
            action='set_debt',
            phone_id=expected_phone,
            yandex_uid=expected_uid,
            value=expected_debt,
            currency='RUB',
            brand='yataxi',
            patch_time='2020-01-20T00:00:00+00:00',
            created_at='2020-02-20T00:00:00+00:00',
            payment_type=payment_type,
        )
        assert request.args['order_id'] == 'happy_path'
        assert request.json == expected_patch
        return mockserver.make_response(status=200)

    task_id = '123456abcdef'
    args = ('happy_path', 'set_debt', datetime.datetime(2020, 1, 20), None)
    if locked_phone_id:
        args = args + ('family_owner_phone_id',)
    await stq_runner.debts_processing.call(task_id=task_id, args=args)
    assert not stq.debts_processing.times_called


@pytest.mark.parametrize(
    ['debts_notifications_task_called'],
    (
        pytest.param(
            False,
            marks=(pytest.mark.config(DEBTS_NOTIFICATIONS_ENABLED=False),),
        ),
        pytest.param(
            True,
            marks=(pytest.mark.config(DEBTS_NOTIFICATIONS_ENABLED=True),),
        ),
    ),
)
async def test_debts_processing_debts_notification(
        stq,
        stq_runner,
        mock_transactions_invoice,
        mock_archive_order,
        mock_v1_debts,
        debts_notifications_task_called,
):
    mock_transactions_invoice()
    mock_archive_order()

    mock_v1_debts(order_id='debts_notification')

    task_id = '123456abcdef'
    args = ('debts_notification', 'set_debt', datetime.datetime(2020, 1, 20))
    await stq_runner.debts_processing.call(task_id=task_id, args=args)
    assert not stq.debts_processing.times_called
    assert (
        stq.taxi_debts_notifications.has_calls
        == debts_notifications_task_called
    )
    if debts_notifications_task_called:
        call = stq.taxi_debts_notifications.next_call()
        call_kwargs = call['kwargs']
        call_kwargs.pop('log_extra')
        assert call_kwargs == {
            'attempt': 0,
            'initial_run': True,
            'order_id': 'debts_notification',
        }
