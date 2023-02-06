import pytest

from tests_contractor_balances import utils

ENTRY_ID = 8484848484
MOCK_NOW = '2021-09-28T19:31:00+00:00'

CONTRACTOR_PROFILE_ID = 'driver11'
PARK_ID = 'park1'

CURRENCY_RUB = 'RUB'
CURRENCY_ILS = 'ILS'

CURRENCY_MAP = {CURRENCY_RUB: '₽', CURRENCY_ILS: '₪'}

AGREEMENT_ID = 'taxi/yandex_ride'
SUB_ACCOUNT = 'tips/googlepay'

TEST_NOTIFICATION_PER_TRANSACTION_PARAMS = [
    (
        [
            # exists in config, notification enabled
            {
                'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
                'sub_account': 'tips/refund/cancel',
            },
            {
                'agreement_id': 'taxi/yandex_ride',
                'sub_account': 'commission/subvention',
                'amount': '10',
            },
            # exists in config, notification disabled
            {'agreement_id': 'taxi/park_ride', 'sub_account': 'payment/cash'},
            # not exists in config
            {'agreement_id': 'taxi/park_ride', 'sub_account': '-'},
        ],
        2,  # sent push count
    ),
    (
        [
            {
                'agreement_id': 'only_negative_push_enabled',
                'sub_account': 'only_negative_push_enabled',
                'amount': '10',
            },
        ],
        0,  # sent push count
    ),
    (
        [
            {
                'agreement_id': 'only_negative_push_enabled',
                'sub_account': 'only_negative_push_enabled',
                'amount': '0',
            },
        ],
        0,  # sent push count
    ),
    (
        [
            {
                'agreement_id': 'only_negative_push_enabled',
                'sub_account': 'only_negative_push_enabled',
                'amount': '-10',
            },
        ],
        1,  # sent push count
    ),
    (
        [
            {
                'agreement_id': 'only_positive_push_enabled',
                'sub_account': 'only_positive_push_enabled',
                'amount': '-10',
            },
        ],
        0,  # sent push count
    ),
    (
        [
            {
                'agreement_id': 'only_positive_push_enabled',
                'sub_account': 'only_positive_push_enabled',
                'amount': '10',
            },
        ],
        1,  # sent push count
    ),
    (
        [
            {
                'agreement_id': 'only_positive_push_enabled',
                'sub_account': 'only_positive_push_enabled',
                'amount': '0',
            },
        ],
        0,  # sent push count
    ),
    (
        [
            {
                'agreement_id': 'neg_and_pos_push_enabled',
                'sub_account': 'neg_and_pos_push_enabled',
                'amount': '-10',
            },
        ],
        1,  # sent push count
    ),
    (
        [
            {
                'agreement_id': 'neg_and_pos_push_enabled',
                'sub_account': 'neg_and_pos_push_enabled',
                'amount': '10',
            },
        ],
        1,  # sent push count
    ),
    (
        [
            {
                'agreement_id': 'neg_and_pos_push_enabled',
                'sub_account': 'neg_and_pos_push_enabled',
                'amount': '0',
            },
        ],
        0,  # sent push count
    ),
]

TEST_TRANSACTION_GROUP_SUM = [
    (
        [
            {
                'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
                'sub_account': 'tips/refund/cancel',
                'amount': '1',
            },
            {
                'agreement_id': 'taxi/yandex_ride',
                'sub_account': 'tips/googlepay',
                'amount': '3',
            },
            {
                'agreement_id': 'taxi/yandex_ride',
                'sub_account': 'commission/subvention',
                'amount': '2',
            },
        ],
        [
            {
                'key': 'DriverBalancePush_Subvention_Msg',
                'params': {'0': f'2,00 {CURRENCY_MAP[CURRENCY_RUB]}'},
            },
            {
                'key': 'DriverBalancePush_Tips_Msg',
                'params': {'0': f'4,00 {CURRENCY_MAP[CURRENCY_RUB]}'},
            },
        ],
    ),
    (  # transactions from different groups with enabled sum
        [
            {
                'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
                'sub_account': 'tips/refund/cancel',
                'amount': '1',
            },
            {
                'agreement_id': 'taxi/park_ride',
                'sub_account': 'promocode/compensation',
                'amount': '-3',
            },
        ],
        [
            {
                'key': 'DriverBalancePush_Tips_Msg',
                'params': {'0': f'1,00 {CURRENCY_MAP[CURRENCY_RUB]}'},
            },
            {
                'key': 'DriverBalancePush_Promocode_Negative_Msg',
                'params': {'0': f'3,00 {CURRENCY_MAP[CURRENCY_RUB]}'},
            },
        ],
    ),
    (  # transactions from different groups with enabled sum
        [
            {
                'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
                'sub_account': 'tips/refund/cancel',
                'amount': '1',
            },
            {
                'agreement_id': 'taxi/yandex_ride',
                'sub_account': 'tips/googlepay',
                'amount': '2',
            },
            {
                'agreement_id': 'taxi/park_ride',
                'sub_account': 'promocode/compensation',
                'amount': '4',
            },
            {
                'agreement_id': 'taxi/park_ride',
                'sub_account': 'promocode/compensation',
                'amount': '-10',
            },
        ],
        [
            {
                'key': 'DriverBalancePush_Tips_Msg',
                'params': {'0': f'3,00 {CURRENCY_MAP[CURRENCY_RUB]}'},
            },
            {
                'key': 'DriverBalancePush_Promocode_Negative_Msg',
                'params': {'0': f'6,00 {CURRENCY_MAP[CURRENCY_RUB]}'},
            },
        ],
    ),
    (  # transactions from single group with disabled sum
        [
            {
                'agreement_id': 'taxi/yandex_ride',
                'sub_account': 'commission/subvention',
                'amount': '1',
            },
            {
                'agreement_id': 'taxi/yandex_ride',
                'sub_account': 'commission/subvention',
                'amount': '2',
            },
            {
                'agreement_id': 'taxi/yandex_ride',
                'sub_account': 'commission/subvention',
                'amount': '3',
            },
        ],
        [
            {
                'key': 'DriverBalancePush_Subvention_Msg',
                'params': {'0': f'1,00 {CURRENCY_MAP[CURRENCY_RUB]}'},
            },
            {
                'key': 'DriverBalancePush_Subvention_Msg',
                'params': {'0': f'2,00 {CURRENCY_MAP[CURRENCY_RUB]}'},
            },
            {
                'key': 'DriverBalancePush_Subvention_Msg',
                'params': {'0': f'3,00 {CURRENCY_MAP[CURRENCY_RUB]}'},
            },
        ],
    ),
    (  # transactions with sum equal zero
        [
            {
                'agreement_id': 'taxi/park_ride',
                'sub_account': 'promocode/compensation',
                'amount': '1',
            },
            {
                'agreement_id': 'taxi/park_ride',
                'sub_account': 'promocode/compensation',
                'amount': '-1',
            },
        ],
        [],
    ),
    (  # transactions with sum equal zero
        [
            {
                'agreement_id': 'taxi/park_ride',
                'sub_account': 'promocode/compensation',
                'amount': '1',
            },
            {
                'agreement_id': 'taxi/park_ride',
                'sub_account': 'promocode/compensation',
                'amount': '-1.001',
            },
        ],
        [],
    ),
    (  # transactions with amount close to zero
        [
            {
                'agreement_id': 'taxi/park_ride',
                'sub_account': 'promocode/compensation',
                'amount': '-0.008',
            },
            {
                'agreement_id': 'taxi/park_ride',
                'sub_account': 'promocode/compensation',
                'amount': '-0.0025',
            },
            {
                'agreement_id': 'taxi/park_ride',
                'sub_account': 'promocode/compensation',
                'amount': '0.0035',
            },
            {
                'agreement_id': 'taxi/park_ride',
                'sub_account': 'promocode/compensation',
                'amount': '-0.003',
            },
        ],
        [
            {
                'key': 'DriverBalancePush_Promocode_Negative_Msg',
                'params': {'0': f'0,01 {CURRENCY_MAP[CURRENCY_RUB]}'},
            },
        ],
    ),
]

TEST_NOTIFICATION_WITH_SINGLE_TRANSACTION_PARAMS = [
    (  # negative amount
        '2021-09-28T19:31:00+00:00',
        'ru',
        'taxi/yandex_ride/mode/driver_fix',
        'tips/refund/cancel',
        '-20.99999',
        CURRENCY_RUB,
        f'21,00 {CURRENCY_MAP[CURRENCY_RUB]}',
        'DriverBalancePush_Tips_Negative_Msg',
        'tips',
    ),
    (  # positive amount
        '2021-09-28T19:31:00+00:00',
        'ru',
        'taxi/yandex_ride',
        'tips/googlepay',
        '20.00001',
        CURRENCY_RUB,
        f'20,00 {CURRENCY_MAP[CURRENCY_RUB]}',
        'DriverBalancePush_Tips_Msg',
        'tips',
    ),
    (  # test locale
        '2021-09-28T19:31:00+00:00',
        'en',
        'taxi/park_ride',
        'promocode/compensation',
        '-20.50001',
        CURRENCY_ILS,
        f'20.50 {CURRENCY_MAP[CURRENCY_ILS]}',
        'DriverBalancePush_Promocode_Negative_Msg',
        'promocode',
    ),
    (  # group not found in config, notification not send
        '2021-09-28T19:31:00+00:00',
        'ru',
        'taxi/park_ride',
        '-',
        '20.1',
        CURRENCY_ILS,
        None,
        None,
        None,
    ),
    (  # notification not set for group, notification not send
        '2021-09-28T19:31:00+00:00',
        'ru',
        'taxi/park_ride',
        'payment/cash',
        '20.1',
        CURRENCY_ILS,
        None,
        None,
        None,
    ),
    (  # the least amount
        '2021-09-28T19:31:00+00:00',
        'ru',
        'taxi/yandex_ride',
        'tips/googlepay',
        '0.01',
        CURRENCY_RUB,
        f'0,01 {CURRENCY_MAP[CURRENCY_RUB]}',
        'DriverBalancePush_Tips_Msg',
        'tips',
    ),
    (  # amount too small, notification not send
        '2021-09-28T19:31:00+00:00',
        'en',
        'taxi/yandex_ride',
        'tips/googlepay',
        '0.001',
        CURRENCY_ILS,
        None,
        None,
        None,
    ),
    (  # ttl expired
        '2021-09-28T19:20:00+00:00',
        'ru',
        'taxi/yandex_ride/mode/driver_fix',
        'tips/refund/cancel',
        '-20.99999',
        CURRENCY_RUB,
        None,
        None,
        None,
    ),
]


TEST_CONFIG_WITH_REDEFINITION = [
    (
        [
            {
                'accounts': [
                    {'agreement_id': 'redefined', 'sub_account': 'redefined'},
                    {'agreement_id': 'redefined', 'sub_account': 'redefined'},
                ],
                'payment_group': 'tips',
            },
        ],
        'DriverBalancePush_Tips_Negative_Msg',
    ),
    (
        [
            {
                'accounts': [
                    {'agreement_id': 'redefined', 'sub_account': 'redefined'},
                ],
                'payment_group': 'tips',
            },
            {
                'accounts': [
                    {'agreement_id': 'redefined', 'sub_account': 'redefined'},
                ],
                'payment_group': 'payment',
            },
        ],
        'DriverBalancePush_Tips_Negative_Msg',
    ),
    (
        [
            {
                'accounts': [
                    {'agreement_id': 'yandex/ride', 'sub_account': 'payment'},
                ],
                'payment_group': 'redefined',
            },
            {
                'accounts': [
                    {'agreement_id': 'taxi/ride', 'sub_account': 'payment'},
                ],
                'payment_group': 'redefined',
            },
        ],
        'DriverBalancePush_Tips_Negative_Msg',
    ),
    # without redefinition
    (
        [
            {
                'accounts': [
                    {
                        'agreement_id': 'taxi/yandex_ride',
                        'sub_account': 'tips/googlepay',
                    },
                ],
                'notification': {
                    'negative_amount_tanker_key': 'NewTankerKey',
                    'positive_amount_tanker_key': 'DriverBalancePush_Tips_Msg',
                    'is_aggregation_enabled': False,
                },
                'payment_group': 'tips',
            },
        ],
        'NewTankerKey',
    ),
]


def _make_stq_args(
        transactions, amount='-1', currency=CURRENCY_RUB, park_id=PARK_ID,
):
    return {
        'park_id': park_id,
        'contractor_profile_id': CONTRACTOR_PROFILE_ID,
        'transactions': [
            {
                'entry_id': ENTRY_ID,
                'account': {
                    'agreement_id': transaction['agreement_id'],
                    'sub_account': transaction['sub_account'],
                    'currency': currency,
                },
                'amount': transaction.pop('amount', amount),
                'event_at': MOCK_NOW,
            }
            for transaction in transactions
        ],
    }


def _make_stq_args_with_single_transaction(
        agreement_id, sub_account, amount, currency, event_at=MOCK_NOW,
):
    return {
        'park_id': PARK_ID,
        'contractor_profile_id': CONTRACTOR_PROFILE_ID,
        'transactions': [
            {
                'entry_id': ENTRY_ID,
                'account': {
                    'agreement_id': agreement_id,
                    'sub_account': sub_account,
                    'currency': currency,
                },
                'amount': amount,
                'event_at': event_at,
            },
        ],
    }


def _make_config(key):
    return [
        {
            'payment_group': 'coupon',
            'accounts': [
                {'agreement_id': AGREEMENT_ID, 'sub_account': SUB_ACCOUNT},
            ],
            'notification': {
                'negative_amount_tanker_key': key,
                'positive_amount_tanker_key': 'key',
                'is_aggregation_enabled': False,
            },
        },
    ]


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    ('transactions', 'push_count'), TEST_NOTIFICATION_PER_TRANSACTION_PARAMS,
)
async def test_notification_per_transaction(
        stq_runner,
        mock_parks_list,
        mock_client_notify_v2_push,
        transactions,
        push_count,
):
    await stq_runner.contractor_balances_transaction_notification.call(
        task_id='task-id', kwargs=_make_stq_args(transactions),
    )

    assert mock_client_notify_v2_push.times_called == push_count


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    ('transactions', 'expected_texts'), TEST_TRANSACTION_GROUP_SUM,
)
async def test_transaction_group_sum(
        mockserver, stq_runner, mock_parks_list, transactions, expected_texts,
):
    expect_call = bool(expected_texts)

    @mockserver.json_handler('/client-notify/v2/push')
    def client_notify(request):
        text = request.json['notification']['text']
        assert text.pop('keyset') == 'taximeter_backend_messages', text
        if text in expected_texts:
            expected_texts.remove(text)
        return {'notification_id': 'id'}

    await stq_runner.contractor_balances_transaction_notification.call(
        task_id='task-id', kwargs=_make_stq_args(transactions),
    )
    assert not expected_texts
    assert client_notify.has_calls == expect_call


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    (
        'event_at',
        'park_locale',
        'agreement_id',
        'sub_account',
        'amount',
        'currency',
        'amount_with_currency',
        'notification_key',
        'notification_type',
    ),
    TEST_NOTIFICATION_WITH_SINGLE_TRANSACTION_PARAMS,
)
async def test_notification_with_single_transaction(
        client_notify_v2_push_context,
        parks_list_context,
        mock_client_notify_v2_push,
        mock_parks_list,
        stq_runner,
        event_at,
        park_locale,
        agreement_id,
        sub_account,
        amount,
        currency,
        amount_with_currency,
        notification_key,
        notification_type,
):
    parks_list_context.set_data(locale=park_locale)

    push_id = utils.make_sha1(
        f'{PARK_ID}{CONTRACTOR_PROFILE_ID}{notification_type}_{ENTRY_ID}',
    )
    client_notify_v2_push_context.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        intent='MessageBalance',
        collapse_key='Balance',
        message_id=push_id,
        locale=park_locale,
        notification={
            'text': {
                'keyset': 'taximeter_backend_messages',
                'key': notification_key,
                'params': {'0': amount_with_currency},
            },
        },
        data={'type': notification_type},
    )

    await stq_runner.contractor_balances_transaction_notification.call(
        task_id='task-id',
        kwargs=_make_stq_args_with_single_transaction(
            agreement_id, sub_account, amount, currency, event_at,
        ),
    )

    assert mock_client_notify_v2_push.has_calls == (
        notification_key is not None
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('update_times', [10, 100])
async def test_config_update(
        mockserver,
        stq_runner,
        taxi_config,
        taxi_contractor_balances,
        mock_parks_list,
        update_times,
):
    keys = [f'key{i}' for i in range(update_times)]

    @mockserver.json_handler('/client-notify/v2/push')
    def _driver_notification(request):
        assert request.json['notification']['text']['key'] == (
            keys[_driver_notification.times_called]
        )
        return {'notification_id': 'id'}

    for key in keys:
        taxi_config.set(
            CONTRACTOR_BALANCES_TRANSACTION_GROUPS=_make_config(key),
        )
        await taxi_contractor_balances.invalidate_caches()
        await stq_runner.contractor_balances_transaction_notification.call(
            task_id='task-id',
            kwargs=_make_stq_args_with_single_transaction(
                AGREEMENT_ID, SUB_ACCOUNT, '-10', CURRENCY_RUB,
            ),
        )

    assert _driver_notification.times_called == len(keys)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    ('new_config', 'notification_key_after_update'),
    TEST_CONFIG_WITH_REDEFINITION,
)
async def test_config_with_redefinition(
        mockserver,
        stq_runner,
        taxi_config,
        taxi_contractor_balances,
        mock_parks_list,
        new_config,
        notification_key_after_update,
):
    notification_key_before_update = 'DriverBalancePush_Tips_Negative_Msg'
    notification_keys = []

    @mockserver.json_handler('/client-notify/v2/push')
    def _driver_notification(request):
        notification_keys.append(request.json['notification']['text']['key'])
        return {'notification_id': 'id'}

    async def call_stq():
        await stq_runner.contractor_balances_transaction_notification.call(
            task_id='task-id',
            kwargs=_make_stq_args_with_single_transaction(
                'taxi/yandex_ride', 'tips/googlepay', '-10', CURRENCY_RUB,
            ),
        )

    await call_stq()
    taxi_config.set(CONTRACTOR_BALANCES_TRANSACTION_GROUPS=new_config)
    await taxi_contractor_balances.invalidate_caches()
    await call_stq()

    assert _driver_notification.times_called == 2
    assert notification_keys[0] == notification_key_before_update
    assert notification_keys[1] == notification_key_after_update


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('enabled', [True, False])
async def test_message_balance_enabled_config(
        mock_parks_list,
        mock_client_notify_v2_push,
        stq_runner,
        taxi_config,
        enabled,
):
    taxi_config.set(CONTRACTOR_BALANCES_MESSAGE_BALANCE_PUSH_ENABLED=enabled)

    await stq_runner.contractor_balances_transaction_notification.call(
        task_id='task-id',
        kwargs=_make_stq_args_with_single_transaction(
            AGREEMENT_ID, SUB_ACCOUNT, '10', CURRENCY_RUB,
        ),
    )

    assert mock_client_notify_v2_push.has_calls == enabled


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('enabled', [True, False])
async def test_push_auto_locale_enabled_config(
        mock_parks_list,
        parks_list_context,
        mock_client_notify_v2_push,
        client_notify_v2_push_context,
        stq_runner,
        taxi_config,
        enabled,
):
    taxi_config.set(CONTRACTOR_BALANCES_PUSH_AUTO_LOCALE_ENABLED=enabled)

    park_locale = 'ru'
    parks_list_context.set_data(locale=park_locale)

    push_id = utils.make_sha1(
        f'{PARK_ID}{CONTRACTOR_PROFILE_ID}tips_{ENTRY_ID}',
    )
    client_notify_v2_push_context.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        intent='MessageBalance',
        collapse_key='Balance',
        message_id=push_id,
        locale=(None if enabled else park_locale),
        notification={
            'text': {
                'keyset': 'taximeter_backend_messages',
                'key': 'DriverBalancePush_Tips_Msg',
                'params': {'0': '10,00 ₽'},
            },
        },
        data={'type': 'tips'},
    )

    await stq_runner.contractor_balances_transaction_notification.call(
        task_id='task-id',
        kwargs=_make_stq_args_with_single_transaction(
            AGREEMENT_ID, SUB_ACCOUNT, '10', CURRENCY_RUB,
        ),
    )

    assert mock_client_notify_v2_push.has_calls
