import pytest

from tests_contractor_balances import utils

MOCK_NOW = '2020-09-27T09:00:00+00:00'

DRIVER_BALANCE_ONLYCARD_ON_KEY = 'DriverBalance_OnlyCard_On'
DRIVER_BALANCE_ONLYCARD_OFF_KEY = 'DriverBalance_OnlyCard_Off'

BALANCE_REVISION = 8484848484

CONTRACTOR_PROFILE_ID = 'driver11'
PARK_ID = 'park1'
CLID = '1'

CURRENCY_RUB = 'RUB'

ALL_PAYMENTS_AVAILABLE = {'card': True, 'corp': True}

TEST_MESSAGE_BALANCE_PUSH_PARAMS = [
    (
        # balance below limit
        '10',
        '15',
        False,  # block orders
        {'cities': ['Москва'], 'countries': ['Россия'], 'enable': True},
        'Москва',
        'Россия',
        CLID,
        ALL_PAYMENTS_AVAILABLE,
        True,  # final onlycard
    ),
    (
        # balance above limit
        '-10',
        '-15',
        False,  # block orders
        {'cities': ['Москва'], 'countries': ['Россия'], 'enable': True},
        'Москва',
        'Россия',
        CLID,
        ALL_PAYMENTS_AVAILABLE,
        False,  # final onlycard
    ),
    (
        # orders blocked
        '10',
        '15',
        True,  # block orders
        {'cities': ['Москва'], 'countries': ['Россия'], 'enable': True},
        'Москва',
        'Россия',
        None,
        None,
        None,  # final onlycard
    ),
    (
        # onlycard disabled by config
        '10',
        '15',
        False,  # block orders
        {'cities': ['Тбилиси'], 'countries': ['Россия'], 'enable': False},
        'Тбилиси',
        'Азербайджан',
        None,
        None,
        None,  # final onlycard
    ),
    (
        # cities and countries empty in config
        '10',
        '15',
        False,  # block orders
        {'cities': [], 'countries': [], 'enable': False},
        'Тбилиси',
        'Азербайджан',
        None,
        None,
        None,  # final onlycard
    ),
    (
        # city is empty
        '10',
        '15',
        False,  # block orders
        {'cities': ['Тбилиси'], 'countries': ['Россия'], 'enable': True},
        '',
        'Азербайджан',
        None,
        None,
        None,  # final onlycard
    ),
    (
        # country is empty
        '10',
        '15',
        False,  # block orders
        {'cities': ['Тбилиси'], 'countries': ['Россия'], 'enable': True},
        'Тбилиси',
        '',
        None,
        None,
        None,  # final onlycard
    ),
    (
        # onlycard enabled in city
        '10',
        '15',
        False,  # block orders
        {'cities': ['Тбилиси'], 'countries': ['Россия'], 'enable': True},
        'Тбилиси',
        'Азербайджан',
        CLID,
        ALL_PAYMENTS_AVAILABLE,
        True,  # final onlycard
    ),
    (
        # onlycard enabled in country
        '10',
        '15',
        False,  # block orders
        {'cities': ['Москва'], 'countries': ['Россия'], 'enable': True},
        'Санкт-Петербург',
        'Россия',
        CLID,
        ALL_PAYMENTS_AVAILABLE,
        True,  # final onlycard
    ),
    (
        # onlycard disabled in country and city
        '10',
        '15',
        False,  # block orders
        {'cities': ['Москва'], 'countries': ['Россия'], 'enable': True},
        'Москва',
        'Россия',
        None,
        None,
        None,  # final onlycard
    ),
    (
        # no clid
        '10',
        '15',
        False,  # block orders
        {'cities': ['Москва'], 'countries': ['Россия'], 'enable': True},
        'Москва',
        'Россия',
        None,
        None,
        None,  # final onlycard
    ),
    (
        # no available payment method
        '-10',
        '-15',
        False,  # block orders
        {'cities': ['Москва'], 'countries': ['Россия'], 'enable': True},
        'Москва',
        'Россия',
        CLID,
        {'card': False, 'corp': False},
        None,  # final onlycard
    ),
    (
        # card payment method available
        '-10',
        '-15',
        False,  # block orders
        {'cities': ['Москва'], 'countries': ['Россия'], 'enable': True},
        'Москва',
        'Россия',
        CLID,
        {'card': True, 'corp': False},
        False,  # final onlycard
    ),
    (
        # corp payment method available
        '-10',
        '-15',
        False,  # block orders
        {'cities': ['Москва'], 'countries': ['Россия'], 'enable': True},
        'Москва',
        'Россия',
        CLID,
        {'card': False, 'corp': True},
        False,  # final onlycard
    ),
]


TEST_MESSAGE_NEW_PUSH_PARAMS = [
    # balance decreased, limit crossed > limit crossed push send
    ('park1', '1', '-1', '0.1', 'ru', DRIVER_BALANCE_ONLYCARD_ON_KEY),
    # balance increased, limit crossed > limit crossed push send
    ('park1', '-1', '1', '0.1', 'ru', DRIVER_BALANCE_ONLYCARD_OFF_KEY),
    # balance decreased, limit not crossed > alert not send
    ('park1', '2', '1', '0.1', 'ru', None),
    # balance increased, limit not crossed > alert not send
    ('park1', '1', '2', '0.1', 'ru', None),
    # balance changed, limit crossed > limit crossed push send
    ('park1', '0.9999', '1', '1', 'ru', DRIVER_BALANCE_ONLYCARD_OFF_KEY),
    # balance not changed, limit not crossed > alert not send
    ('park1', '0.99999999', '1', '0.1', 'ru', None),
    # balance changed, limit crossed, limit disabled > alert not send
    ('park1', '-2', '2', '0', 'ru', None),
    # park_locale 'en'
    ('park2', '1', '-1', '0.1', 'en', DRIVER_BALANCE_ONLYCARD_ON_KEY),
]


def _make_stq_args(
        balance,
        old_balance,
        balance_limit,
        currency,
        block_orders_on_balance_below_limit,
        park_id=PARK_ID,
        balance_changed_at=MOCK_NOW,
):
    return {
        'park_id': park_id,
        'contractor_profile_id': CONTRACTOR_PROFILE_ID,
        'balance': balance,
        'old_balance': old_balance,
        'currency': currency,
        'balance_limit': balance_limit,
        'block_orders_on_balance_below_limit': (
            block_orders_on_balance_below_limit
        ),
        'balance_revision': BALANCE_REVISION,
        'balance_changed_at': balance_changed_at,
    }


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    CONTRACTOR_BALANCES_MESSAGE_BALANCE_PUSH_ENABLED=True,
    CONTRACTOR_BALANCES_CROSS_LIMIT_NOTIFICATION_ENABLED=False,
)
@pytest.mark.parametrize(
    (
        'balance',
        'balance_limit',
        'block_orders_on_balance_below_limit',
        'config',
        'city_id',
        'country_id',
        'clid',
        'available_methods',
        'final_onlycard',
    ),
    TEST_MESSAGE_BALANCE_PUSH_PARAMS,
)
async def test_message_balance_push(
        taxi_config,
        payment_methods_context,
        parks_list_context,
        client_notify_v2_push_context,
        mock_park_payment_methods,
        mock_parks_list,
        mock_client_notify_v2_push,
        stq_runner,
        balance,
        balance_limit,
        block_orders_on_balance_below_limit,
        config,
        city_id,
        country_id,
        clid,
        available_methods,
        final_onlycard,
):
    parks_list_context.set_data(
        clid=clid, city_id=city_id, country_id=country_id,
    )

    if available_methods is not None:
        payment_methods_context.set_data(available_methods)

    push_id = utils.make_sha1(
        f'{PARK_ID}{CONTRACTOR_PROFILE_ID}'
        f'balance_revision_{BALANCE_REVISION}',
    )
    client_notify_v2_push_context.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        intent='MessageBalance',
        collapse_key='Balance',
        message_id=push_id,
        data={
            'balance': balance,
            'limit': balance_limit,
            'balance_revision': BALANCE_REVISION,
            'onlycard': final_onlycard,
        },
    )

    taxi_config.set(TAXIMETER_LOW_BALANCE_ONLYCARD=config)

    await stq_runner.contractor_balances_update_notification.call(
        task_id='task-id',
        kwargs=_make_stq_args(
            balance,
            '0',
            balance_limit,
            CURRENCY_RUB,
            block_orders_on_balance_below_limit,
            PARK_ID,
        ),
    )

    assert mock_client_notify_v2_push.has_calls
    assert mock_parks_list.has_calls
    assert mock_park_payment_methods.has_calls == (
        available_methods is not None
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    CONTRACTOR_BALANCES_MESSAGE_BALANCE_PUSH_ENABLED=False,
    CONTRACTOR_BALANCES_CROSS_LIMIT_NOTIFICATION_ENABLED=True,
)
@pytest.mark.parametrize(
    (
        'park_id',
        'old_balance',
        'new_balance',
        'balance_limit',
        'park_locale',
        'notification_key',
    ),
    TEST_MESSAGE_NEW_PUSH_PARAMS,
)
async def test_message_new_push(
        stq_runner,
        client_notify_v2_push_context,
        parks_list_context,
        mock_client_notify_v2_push,
        mock_parks_list,
        mock_park_payment_methods,
        park_id,
        old_balance,
        new_balance,
        balance_limit,
        park_locale,
        notification_key,
):
    parks_list_context.set_data(locale=park_locale)

    push_id = utils.make_sha1(
        f'{park_id}{CONTRACTOR_PROFILE_ID}{BALANCE_REVISION}',
    )
    client_notify_v2_push_context.set_data(
        park_id=park_id,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        intent='MessageNew',
        collapse_key=f'Alert:{push_id}',
        message_id=push_id,
        locale=park_locale,
        data={'id': push_id},
        notification={
            'text': {
                'keyset': 'taximeter_backend_driver_messages',
                'key': notification_key,
            },
        },
    )

    await stq_runner.contractor_balances_update_notification.call(
        task_id='task-id',
        kwargs=_make_stq_args(
            new_balance,
            old_balance,
            balance_limit,
            CURRENCY_RUB,
            False,
            park_id,
        ),
    )

    assert mock_client_notify_v2_push.has_calls == (
        notification_key is not None
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    ('balance_changed_at', 'expired'),
    [(MOCK_NOW, False), ('2020-09-27T08:00:00+00:00', True)],
)
async def test_ttl_expiration(
        stq_runner,
        mock_parks_list,
        mock_park_payment_methods,
        mock_client_notify_v2_push,
        balance_changed_at,
        expired,
):
    await stq_runner.contractor_balances_update_notification.call(
        task_id='task-id',
        kwargs=_make_stq_args(
            '10', '0', '15', CURRENCY_RUB, False, PARK_ID, balance_changed_at,
        ),
    )

    assert mock_client_notify_v2_push.has_calls != expired


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('enabled', [True, False])
async def test_message_balance_enabled_config(
        stq_runner,
        taxi_config,
        mock_parks_list,
        mock_park_payment_methods,
        mock_client_notify_v2_push,
        enabled,
):
    taxi_config.set(CONTRACTOR_BALANCES_MESSAGE_BALANCE_PUSH_ENABLED=enabled)

    await stq_runner.contractor_balances_update_notification.call(
        task_id='task-id',
        kwargs=_make_stq_args('10', '0', '15', CURRENCY_RUB, False),
    )

    assert mock_client_notify_v2_push.has_calls == enabled


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('enabled', [True, False])
async def test_message_balance_push_auto_locale_enabled_config(
        mock_parks_list,
        parks_list_context,
        mock_park_payment_methods,
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
        f'{PARK_ID}{CONTRACTOR_PROFILE_ID}'
        f'balance_revision_{BALANCE_REVISION}',
    )
    client_notify_v2_push_context.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        intent='MessageBalance',
        collapse_key='Balance',
        message_id=push_id,
        data={
            'balance': '10',
            'limit': '15',
            'balance_revision': BALANCE_REVISION,
            'onlycard': True,
        },
    )

    await stq_runner.contractor_balances_update_notification.call(
        task_id='task-id',
        kwargs=_make_stq_args('10', '0', '15', CURRENCY_RUB, False),
    )

    assert mock_client_notify_v2_push.has_calls


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.config(
    CONTRACTOR_BALANCES_MESSAGE_BALANCE_PUSH_ENABLED=False,
    CONTRACTOR_BALANCES_CROSS_LIMIT_NOTIFICATION_ENABLED=True,
)
async def test_message_new_push_auto_locale_enabled_config(
        mock_parks_list,
        parks_list_context,
        mock_park_payment_methods,
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
        f'{PARK_ID}{CONTRACTOR_PROFILE_ID}{BALANCE_REVISION}',
    )
    client_notify_v2_push_context.set_data(
        park_id=PARK_ID,
        contractor_profile_id=CONTRACTOR_PROFILE_ID,
        intent='MessageNew',
        collapse_key=f'Alert:{push_id}',
        message_id=push_id,
        locale=(None if enabled else park_locale),
        data={'id': push_id},
        notification={
            'text': {
                'keyset': 'taximeter_backend_driver_messages',
                'key': 'DriverBalance_OnlyCard_Off',
            },
        },
    )

    await stq_runner.contractor_balances_update_notification.call(
        task_id='task-id',
        kwargs=_make_stq_args('10', '0', '5', CURRENCY_RUB, False),
    )

    assert mock_client_notify_v2_push.has_calls
