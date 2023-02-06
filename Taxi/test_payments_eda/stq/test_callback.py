import typing

import pytest

from payments_eda import consts
from payments_eda.utils import experiments
from test_payments_eda import consts as test_consts
from test_payments_eda.stq import consts as stq_consts

CARD = 'card'
APPLEPAY = 'applepay'
GOOGLEPAY = 'googlepay'
CORP = 'corp'
BADGE = 'badge'
UNKNOWN = 'unknown'
PERSONAL_WALLET = 'personal_wallet'

ALL_PAYMENT_TYPES = (CARD, APPLEPAY, GOOGLEPAY, CORP, BADGE)

ALL_INVOICE_STATUSES = (
    'init',
    'holding',
    'held',
    'hold-failed',
    'clearing',
    'cleared',
    'clear-failed',
    'refunding',
)

CORPORATE = 'corporate'

DEFAULT_PAYMENT_DATA = {
    'total': '100.00',
    'held': '10.00',
    'debt': '17.00',
    'cleared': '10.00',
    'currency': 'RUB',
}


def _make_eda_confirm_event_data(**extra):
    return {
        'order_id': 'test_order',
        'transactions': [],
        **DEFAULT_PAYMENT_DATA,
        **extra,
    }


def _make_eda_item_change_event_data(**extra):
    return {'order_id': 'test_order', **DEFAULT_PAYMENT_DATA, **extra}


def _make_full_sum_extra_with_personal_wallet(
        keys: typing.List[str], payment_type: str,
) -> dict:
    full_sum_extra = {
        key: [
            {'payment_type': payment_type, 'amount': '17.00'},
            {'payment_type': 'personal_wallet', 'amount': '7.00'},
        ]
        for key in keys
    }

    for key in ['total', 'debt', 'held', 'cleared']:
        full_sum_extra.setdefault(key, [])
    return full_sum_extra


def _make_full_sum_invoice_extra(full_sum_extra: dict) -> dict:
    extra = {
        (key if key != 'total' else 'sum_to_pay'): [
            {
                'payment_type': item['payment_type'],
                'items': [{'amount': item['amount'], 'item_id': 'food'}],
            }
            for item in items
        ]
        for key, items in full_sum_extra.items()
    }
    for key in ['sum_to_pay', 'debt', 'held', 'cleared']:
        extra.setdefault(key, [])
    return extra


def _make_eda_event_payment_data(keys: typing.List[str]):
    payment_data = {key: '17.00' for key in keys}
    for key in ['total', 'debt', 'held', 'cleared']:
        payment_data.setdefault(key, '0')
    return payment_data


def _make_eda_full_sum(full_sum_extra: dict) -> dict:
    return {'currency': 'RUB', **full_sum_extra}


async def test_task_without_service(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
):
    invoice_retrieve_mock = mock_invoice_retrieve(status='held', service=None)
    eda_event_mock = mock_eda_event(
        expected_extra_query_data={'service': 'eats'},
    )
    mock_user_api()

    await invoke_callback_task(operation_id='create:123')

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 1


@pytest.mark.config(EDA_REPLACE_SERVICE_IN_QUERY={'some_new_service': 'eats'})
@pytest.mark.parametrize(
    'invoice_service, expected_eda_service',
    [('eats', 'eats'), ('grocery', 'grocery'), ('some_new_service', 'eats')],
)
async def test_task_invoice_service(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        invoice_service,
        expected_eda_service,
):
    invoice_retrieve_mock = mock_invoice_retrieve(
        status='held', service=invoice_service,
    )
    eda_event_mock = mock_eda_event(
        expected_action='confirm',
        expected_data=_make_eda_confirm_event_data(),
        expected_extra_query_data={'service': expected_eda_service},
    )
    mock_user_api()

    await invoke_callback_task(operation_id='create:123')

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 1


# 'held' and 'hold-failed' are being tested in 'reject' action test cases
# 'cleared' and 'clear-failed' are being tested in 'payment' action test cases
@pytest.mark.parametrize(
    'invoice_status', ('init', 'holding', 'clearing', 'refunding'),
)
async def test_create_task_no_notification(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        invoice_status,
):
    eda_event_mock = mock_eda_event()
    invoice_retrieve_mock = mock_invoice_retrieve(status=invoice_status)
    mock_user_api()

    await invoke_callback_task(operation_id='create:123')

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 0


@pytest.mark.parametrize('payment_type', ALL_PAYMENT_TYPES)
async def test_confirm_action(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        payment_type,
        invoke_callback_task,
):
    invoice_retrieve_mock = mock_invoice_retrieve(
        status='held', payment_types=[payment_type],
    )
    mock_user_api()
    eda_event_mock = mock_eda_event(
        expected_action='confirm',
        expected_data=_make_eda_confirm_event_data(),
    )
    await invoke_callback_task(operation_id='create:123')

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 1


@pytest.mark.parametrize(
    [
        'invoice_retrieve_extra',
        'eda_event_extra_data',
        'eda_event_extra_query_data',
    ],
    [
        pytest.param(
            {'service': 'grocery'},
            {},
            {'service': 'grocery'},
            id='Test with service=grocery',
        ),
        pytest.param(
            {
                'transactions': [
                    {
                        **stq_consts.TRANSACTION,
                        'external_payment_id': 'xxx',
                        'operation_id': None,
                        'terminal_id': None,
                        'payment_type': None,
                        'payment_method_id': None,
                    },
                ],
            },
            {'transactions': [{'external_payment_id': 'xxx'}]},
            {},
            id='Test with transaction with only `external_payment_id`',
        ),
        pytest.param(
            {
                'transactions': [
                    {
                        **stq_consts.TRANSACTION,
                        'terminal_id': '42',
                        'operation_id': 'create:123',
                        'payment_type': None,
                        'payment_method_id': None,
                        'external_payment_id': 'xxx',
                    },
                ],
            },
            {
                'transactions': [
                    {
                        'external_payment_id': 'xxx',
                        'terminal_id': '42',
                        'operation_id': 'create:123',
                    },
                ],
            },
            {},
            id='Test with optional fields in transaction',
        ),
    ],
)
async def test_confirm_action_extra_fields(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        invoice_retrieve_extra,
        eda_event_extra_data,
        eda_event_extra_query_data,
):
    invoice_retrieve_mock = mock_invoice_retrieve(
        status='held', **invoice_retrieve_extra,
    )
    mock_user_api()
    expected_eda_event_data = _make_eda_confirm_event_data(
        **eda_event_extra_data,
    )
    eda_event_mock = mock_eda_event(
        expected_action='confirm',
        expected_data=expected_eda_event_data,
        expected_extra_query_data=eda_event_extra_query_data,
    )
    await invoke_callback_task(operation_id='create:123')

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 1


@pytest.mark.parametrize('payment_type', ALL_PAYMENT_TYPES)
@pytest.mark.parametrize(
    ['invoice_retrieve_extra', 'extra_eda_event_data'],
    [
        pytest.param({}, {}, id='no fail reason'),
        pytest.param(
            {'fail_reason': {'code': 'not_enough_funds'}},
            {'reason': {'code': 'not_enough_funds'}},
            id='fail reason with code',
        ),
    ],
)
async def test_reject_action(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        payment_type,
        invoke_callback_task,
        invoice_retrieve_extra,
        extra_eda_event_data,
):
    invoice_retrieve_mock = mock_invoice_retrieve(
        status='hold-failed',
        payment_types=[payment_type],
        **invoice_retrieve_extra,
    )
    eda_event_mock = mock_eda_event(
        expected_action='reject',
        expected_data={'order_id': 'test_order', **extra_eda_event_data},
    )
    mock_user_api()

    await invoke_callback_task(operation_id='create:123')

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 1


@pytest.mark.parametrize('payment_type', ALL_PAYMENT_TYPES)
@pytest.mark.parametrize('invoice_status', ALL_INVOICE_STATUSES)
async def test_item_change_action_basic(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        payment_type,
        invoice_status,
):
    invoice_retrieve_mock = mock_invoice_retrieve(
        status=invoice_status, payment_types=[payment_type],
    )
    mock_user_api()
    eda_event_mock = mock_eda_event(
        expected_action='item_change',
        expected_data=_make_eda_item_change_event_data(status='success'),
    )
    await invoke_callback_task(operation_id='change:123')

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 1


@pytest.mark.parametrize(
    'notification_type', ('operation_finish', 'transaction_clear'),
)
@pytest.mark.parametrize('payment_type', ALL_PAYMENT_TYPES)
@pytest.mark.parametrize('invoice_status', ALL_INVOICE_STATUSES)
async def test_item_change_action_basic_additional_arguments(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        payment_type,
        invoice_status,
        notification_type,
):
    invoice_retrieve_mock = mock_invoice_retrieve(
        status=invoice_status, payment_types=[payment_type],
    )
    mock_user_api()
    eda_event_mock = mock_eda_event(
        expected_action='item_change',
        expected_data=_make_eda_item_change_event_data(status='success'),
    )
    await invoke_callback_task(
        operation_id='change:123', notification_type=notification_type,
    )

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 1


@pytest.mark.parametrize(
    [
        'invoice_status',
        'operation_id',
        'invoice_retrieve_extra',
        'extra_event_data',
    ],
    [
        (
            'cleared',
            'change:123:admin',
            {},
            {'status': 'success', 'change_source': 'admin'},
        ),
        (
            'cleared',
            'change:123:tips',
            {},
            {'status': 'success', 'change_source': 'tips'},
        ),
        ('clear-failed', 'change:123', {}, {'status': 'success'}),
        (
            'clear-failed',
            'change:123',
            {'fail_reason': {'code': 'payment_failed'}},
            {'status': 'success'},
        ),
    ],
)
async def test_item_change_action_extra_fields(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        invoice_status,
        operation_id,
        invoice_retrieve_extra,
        extra_event_data,
):
    invoice_retrieve_mock = mock_invoice_retrieve(
        status=invoice_status, **invoice_retrieve_extra,
    )
    mock_user_api()
    eda_event_mock = mock_eda_event(
        expected_action='item_change',
        expected_data=_make_eda_item_change_event_data(**extra_event_data),
    )
    await invoke_callback_task(operation_id=operation_id)

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 1


# only these statuses seem possible for clear notification
# 'cleared' and 'clear-failed' are being tested in 'payment' action test cases
@pytest.mark.parametrize('invoice_status', ('init', 'clearing', 'refunding'))
async def test_clear_no_notification(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        invoice_status,
):
    eda_event_mock = mock_eda_event()
    invoice_retrieve_mock = mock_invoice_retrieve(status=invoice_status)
    mock_user_api()

    await invoke_callback_task(operation_id='clear')

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 0


# 'cleared' and 'clear-failed' are being tested in 'payment' action test cases
@pytest.mark.parametrize(
    'invoice_status',
    ('init', 'holding', 'held', 'hold-failed', 'clearing', 'refunding'),
)
async def test_cancel_no_notification(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        invoice_status,
):
    eda_event_mock = mock_eda_event()
    invoice_retrieve_mock = mock_invoice_retrieve(status=invoice_status)
    mock_user_api()

    await invoke_callback_task(operation_id='cancel:123')

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 0


# Test cases for `change` task are in its own test
@pytest.mark.parametrize('payment_type', ALL_PAYMENT_TYPES)
@pytest.mark.parametrize('operation_id', ('clear', 'create:123', 'cancel:123'))
@pytest.mark.parametrize(
    ['invoice_status', 'expected_eda_event_data'],
    [
        ('cleared', {'order_id': 'test_order', 'payment_status': 'success'}),
        ('clear-failed', {'order_id': 'test_order', 'payment_status': 'debt'}),
    ],
)
async def test_payment_action(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        payment_type,
        operation_id,
        invoice_status,
        expected_eda_event_data,
):
    eda_event_mock = mock_eda_event(
        expected_action='payment', expected_data=expected_eda_event_data,
    )
    invoice_retrieve_mock = mock_invoice_retrieve(status=invoice_status)
    mock_user_api()

    await invoke_callback_task(operation_id=operation_id)

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 1


# Test cases for `change` task are in its own test
@pytest.mark.parametrize('payment_type', ALL_PAYMENT_TYPES)
@pytest.mark.parametrize('operation_id', ('create:123', 'cancel:123'))
@pytest.mark.parametrize(
    ['invoice_status', 'expected_eda_event_data'],
    [
        ('cleared', {'order_id': 'test_order', 'payment_status': 'success'}),
        ('clear-failed', {'order_id': 'test_order', 'payment_status': 'debt'}),
    ],
)
async def test_payment_action_additional_arguments(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        payment_type,
        operation_id,
        invoice_status,
        expected_eda_event_data,
):
    eda_event_mock = mock_eda_event(
        expected_action='payment', expected_data=expected_eda_event_data,
    )
    invoice_retrieve_mock = mock_invoice_retrieve(status=invoice_status)
    mock_user_api()

    await invoke_callback_task(operation_id=operation_id)

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 1


@pytest.mark.parametrize(
    [
        'invoice_retrieve_extra',
        'eda_event_extra_data',
        'user_api_handler_times_called',
    ],
    (
        pytest.param(
            {}, {}, 0, id='Test with no `external_user_info` in `invoice`',
        ),
        pytest.param(
            {
                'external_user_info': {
                    'user_id': test_consts.DEFAULT_USER_ID,
                    'origin': test_consts.USER_ORIGIN_TAXI,
                },
            },
            {'device_id': '123'},
            1,
            id='Test with `external_user_info`'
            ' with `origin=taxi` in `invoice`',
        ),
        pytest.param(
            {
                'external_user_info': {
                    'user_id': test_consts.DEFAULT_USER_ID,
                    'origin': 'foo',
                },
            },
            {},
            0,
            id='Test with `external_user_info`'
            ' with non-taxi origin in `invoice`',
        ),
    ),
)
async def test_task_external_user_info(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        invoice_retrieve_extra,
        eda_event_extra_data,
        user_api_handler_times_called,
):
    invoice_retrieve_mock = mock_invoice_retrieve(
        status='held', **invoice_retrieve_extra,
    )
    user_api_mock = mock_user_api(
        user_data={
            'id': test_consts.DEFAULT_USER_ID,
            'metrica_device_id': '123',
        },
    )
    expected_eda_event_data = _make_eda_confirm_event_data(
        **eda_event_extra_data,
    )
    eda_event_mock = mock_eda_event(
        expected_action='confirm', expected_data=expected_eda_event_data,
    )
    await invoke_callback_task(operation_id='create:123')

    assert invoice_retrieve_mock.times_called == 1
    assert user_api_mock.times_called == user_api_handler_times_called
    assert eda_event_mock.times_called == 1


@pytest.mark.config(PAYMENTS_EDA_ATTEMPT_TO_PATCH_EDA_BASE_URL=True)
async def test_no_base_eda_url_without_experiment(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
):
    mock_invoice_retrieve(status='held')
    mock_user_api()
    eda_event_mock = mock_eda_event()
    await invoke_callback_task(operation_id='create:123')
    # check that with config set to true but without experiment we still
    # use original eda event url
    assert eda_event_mock.times_called == 1


NEW_BASE_URL = 'new_base_url'


@pytest.mark.config(PAYMENTS_EDA_ATTEMPT_TO_PATCH_EDA_BASE_URL=True)
@pytest.mark.client_experiments3(
    consumer=consts.EXP3_CONSUMER_STQ,
    experiment_name=experiments.EXP3_PAYMENTS_EDA_URLS,
    args=[
        {
            'name': 'yandex_uid',
            'type': 'string',
            'value': test_consts.DEFAULT_YANDEX_UID,
        },
    ],
    # '$mockserver/' prefix is necessary for testsuite routing to work
    value={'patched_base_url': f'$mockserver/{NEW_BASE_URL}'},
)
async def test_get_base_eda_url_from_experiment(
        mockserver,
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
):
    mock_invoice_retrieve(
        status='held', yandex_uid=test_consts.DEFAULT_YANDEX_UID,
    )
    mock_user_api()
    eda_event_mock = mock_eda_event()

    expected_eda_event_data = _make_eda_confirm_event_data()
    new_eda_event_mock = mock_eda_event(
        base_url=NEW_BASE_URL,
        expected_action='confirm',
        expected_data=expected_eda_event_data,
    )

    await invoke_callback_task(operation_id='create:123')
    assert eda_event_mock.times_called == 0
    assert new_eda_event_mock.times_called == 1


@pytest.mark.parametrize(
    'payment_type', ['card', 'applepay', 'googlepay', 'corp', 'badge'],
)
@pytest.mark.parametrize(
    'full_sum_extra_keys', [['total'], ['debt', 'held'], ['held', 'cleared']],
)
async def test_full_sum_create(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        full_sum_extra_keys,
        payment_type,
):
    full_sum_extra = _make_full_sum_extra_with_personal_wallet(
        keys=full_sum_extra_keys, payment_type=payment_type,
    )
    invoice_retrieve_extra = _make_full_sum_invoice_extra(full_sum_extra)
    invoice_retrieve_mock = mock_invoice_retrieve(
        status='held', **invoice_retrieve_extra,
    )
    user_api_mock = mock_user_api()

    expected_action = 'confirm'
    expected_data = _make_eda_confirm_event_data(
        **_make_eda_event_payment_data(keys=full_sum_extra_keys),
    )
    expected_data.update({'transactions': []})
    expected_full_sum = _make_eda_full_sum(full_sum_extra)
    eda_event_mock = mock_eda_event(
        expected_action=expected_action,
        expected_data=expected_data,
        expected_full_sum=expected_full_sum,
    )

    operation_id = 'create:123'
    await invoke_callback_task(operation_id=operation_id)

    assert invoice_retrieve_mock.times_called == 1
    assert user_api_mock.times_called == 0
    assert eda_event_mock.times_called == 1


@pytest.mark.parametrize(
    'payment_type', ['card', 'applepay', 'googlepay', 'corp', 'badge'],
)
@pytest.mark.parametrize(
    'full_sum_extra_keys', [['total'], ['debt', 'held'], ['held', 'cleared']],
)
async def test_full_sum_change(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        full_sum_extra_keys,
        payment_type,
):
    full_sum_extra = _make_full_sum_extra_with_personal_wallet(
        keys=full_sum_extra_keys, payment_type=payment_type,
    )
    invoice_retrieve_extra = _make_full_sum_invoice_extra(full_sum_extra)
    invoice_retrieve_mock = mock_invoice_retrieve(
        status='cleared', **invoice_retrieve_extra,
    )
    user_api_mock = mock_user_api()

    expected_action = 'item_change'
    expected_data = _make_eda_item_change_event_data(
        status='success',
        **_make_eda_event_payment_data(keys=full_sum_extra_keys),
    )
    expected_full_sum = _make_eda_full_sum(full_sum_extra)
    eda_event_mock = mock_eda_event(
        expected_action=expected_action,
        expected_data=expected_data,
        expected_full_sum=expected_full_sum,
    )

    operation_id = 'change:123'
    await invoke_callback_task(operation_id=operation_id)

    assert invoice_retrieve_mock.times_called == 1
    assert user_api_mock.times_called == 0
    assert eda_event_mock.times_called == 1


async def test_data_does_not_contain_personal_wallet(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
):
    keys = ['held']
    payment_type = 'card'
    full_sum_extra = _make_full_sum_extra_with_personal_wallet(
        keys=keys, payment_type=payment_type,
    )
    invoice_retrieve_extra = _make_full_sum_invoice_extra(full_sum_extra)
    invoice_retrieve_mock = mock_invoice_retrieve(
        status='held', **invoice_retrieve_extra,
    )
    user_api_mock = mock_user_api()

    expected_data: typing.Dict[str, typing.Any] = _make_eda_confirm_event_data(
        **_make_eda_event_payment_data(keys=keys),
    )

    expected_full_sum = _make_eda_full_sum(full_sum_extra)

    eda_event_mock = mock_eda_event(
        expected_action='confirm',
        expected_data=expected_data,
        expected_full_sum=expected_full_sum,
    )

    await invoke_callback_task(operation_id=f'create:123')

    assert invoice_retrieve_mock.times_called == 1
    assert user_api_mock.times_called == 0
    assert eda_event_mock.times_called == 1


@pytest.mark.parametrize(
    'payment_types, account_type',
    [
        ([CARD], CARD),
        ([APPLEPAY], CARD),
        ([GOOGLEPAY], CARD),
        ([CORP], CORPORATE),
        ([BADGE], BADGE),
        ([BADGE, CARD], BADGE),
        ([], None),
    ],
)
async def test_account_type(
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        payment_types,
        account_type,
):

    invoice_retrieve_extra = {
        'transactions': [],
        'payment_types': payment_types,
    }
    invoice_retrieve_mock = mock_invoice_retrieve(
        status='held', **invoice_retrieve_extra,
    )
    mock_user_api()

    eda_event_mock = mock_eda_event(
        expected_action='confirm',
        expected_data=_make_eda_confirm_event_data(),
        expected_account_type=account_type,
    )

    await invoke_callback_task(operation_id='create:123')

    assert invoice_retrieve_mock.times_called == 1
    assert eda_event_mock.times_called == 1


@pytest.mark.parametrize(
    ['service', 'cashback_called'],
    [('restaurants', True), ('eats', False), ('grocery', False)],
)
@pytest.mark.config(PAYMENTS_EDA_CASHBACK_ENABLED={'restaurants': True})
async def test_cashback_callback(
        mockserver,
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        service,
        cashback_called,
):
    @mockserver.json_handler('/iiko-integration/v1/order/update')
    def _iiko_int_order_update(_request):
        return {}

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/universal_cashback_processing',
    )
    def _stq_cashback_processing(request):
        request.json['kwargs'].pop('log_extra')
        assert request.json == {
            'task_id': f'{service}_test_order',
            'args': ['test_order', service],
            'kwargs': {},
            'eta': '1970-01-01T00:00:00.000000Z',
        }

    invoice_retrieve_extra = {'service': service}
    mock_invoice_retrieve(status='held', **invoice_retrieve_extra)
    mock_user_api()
    mock_eda_event(
        expected_action='confirm',
        expected_data=_make_eda_confirm_event_data(),
        expected_extra_query_data={'service': service},
    )
    await invoke_callback_task(operation_id='create:123')

    assert _stq_cashback_processing.times_called == int(cashback_called)


@pytest.mark.parametrize(
    ['service', 'notified'], [('restaurants', True), ('eats', False)],
)
@pytest.mark.parametrize(
    ['invoice_status', 'expected_data', 'operation_id_in_request'],
    [
        ('holding', 'HOLDING', True),
        ('held', 'HELD', True),
        ('hold-failed', 'HOLD_FAILED', True),
        ('clearing', 'CLEARING', False),
        ('cleared', 'CLEARED', False),
        ('clear-failed', None, False),
        ('refunding', 'REFUNDING', False),
    ],
)
async def test_notify_restaurants(
        mockserver,
        mock_invoice_retrieve,
        mock_user_api,
        mock_eda_event,
        invoke_callback_task,
        service,
        notified,
        invoice_status,
        expected_data,
        operation_id_in_request,
):
    @mockserver.json_handler('/iiko-integration/v1/order/update')
    def _iiko_int_order_update(request):
        assert 'order_id' not in request.query
        # 'test_order' order_id is set in invoke_callback_task fixture
        assert request.query['invoice_id'] == 'test_order'
        if operation_id_in_request:
            assert request.query['operation_id'] == 'charge_1'
        else:
            assert 'operation_id' not in request.query
        assert request.json == {'invoice_status': expected_data}
        return {}

    invoice_retrieve_extra = {'service': service}
    mock_invoice_retrieve(status=invoice_status, **invoice_retrieve_extra)
    mock_user_api()
    mock_eda_event()
    await invoke_callback_task(operation_id='charge_1')

    if notified and expected_data:
        assert _iiko_int_order_update.times_called == 1
    else:
        assert _iiko_int_order_update.times_called == 0
