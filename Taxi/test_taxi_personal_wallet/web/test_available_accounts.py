# pylint: disable=invalid-name, too-many-lines
import typing

from aiohttp import web
import pytest

from test_taxi_personal_wallet import conftest

TANKER_KEY_COMPLEMENT_PREFIX = 'complementary_method.personal_wallet'
TANKER_KEY_COMPLEMENT_COMPAT_DESCRIPTION = (
    TANKER_KEY_COMPLEMENT_PREFIX + '.compatibility_description'
)
TANKER_KEY_SCREEN_PROPORTIES = 'personal_wallet.details_screen_proporties.'

EXPERIMENTS3_CONSUMER = 'taxi_personal_wallet/available_accounts'

DEFAULT_CURRENCY_RULES = {
    'code': 'RUB',
    'text': 'руб.',
    'template': '$VALUE$\N{NO-BREAK SPACE}$SIGN$$CURRENCY$',
    'sign': '₽',
}

SUPERAPP_SEVICES = ['eats', 'grocery']


def _make_visibility(show_to_new_users=True, currency='RUB', enabled=True):
    return {
        'currency': currency,
        'show_to_new_users': show_to_new_users,
        'enabled': enabled,
    }


def _make_visible_body(*currencies):
    return {'currencies': list(currencies)}


def _make_application_args(app_name: str = None):
    if app_name is None:
        app_name = conftest.TEST_APPLICATION
    return [
        {'name': 'application', 'type': 'application', 'value': app_name},
        {'name': 'version', 'type': 'application_version', 'value': '1.2.3'},
        {'name': 'application.brand', 'type': 'string', 'value': 'yataxi'},
    ]


def _build_exps_args(
        name,
        yandex_uid,
        phone_id: typing.Optional[str] = 'phone_id',
        personal_phone_id: typing.Optional[str] = 'personal_phone_id',
        additional_args: typing.List = None,
        app_name: str = None,
        service: str = None,
        value=None,
):
    args = [{'name': 'yandex_uid', 'type': 'string', 'value': yandex_uid}]
    if phone_id is not None:
        args.append({'name': 'phone_id', 'type': 'string', 'value': phone_id})
    if personal_phone_id is not None:
        args.append(
            {
                'name': 'personal_phone_id',
                'type': 'string',
                'value': personal_phone_id,
            },
        )
    if service is not None:
        args.append({'name': 'service', 'type': 'string', 'value': service})
    if additional_args:
        args.extend(additional_args)
    args.extend(_make_application_args(app_name=app_name))

    args_for_exp = {
        'consumer': EXPERIMENTS3_CONSUMER,
        'experiment_name': name,
        'args': args,
        'value': value or True,
    }

    return args_for_exp


def _make_experiment3(
        name,
        *,
        yandex_uid,
        phone_id: typing.Optional[str] = 'phone_id',
        personal_phone_id: typing.Optional[str] = 'personal_phone_id',
        additional_args: typing.List = None,
        app_name: str = None,
        service: str = None,
        value=None,
):
    args_for_exp = _build_exps_args(
        name,
        yandex_uid,
        phone_id,
        personal_phone_id,
        additional_args,
        app_name,
        service,
        value,
    )

    return pytest.mark.client_experiments3(**args_for_exp)


pytestmark = [
    pytest.mark.translations(
        client_messages={
            'personal_wallet_name': {'ru': 'Плюс'},
            'personal_wallet.rule_description': {'ru': 'действует до'},
            'payment_personal_wallet.availability.action_buy_plus': {
                'ru': 'Подключить Яндекс.Плюс',
            },
            'payment_personal_wallet.availability.disabled_reason': {
                'ru': 'нужна подписка на Плюс',
            },
            (TANKER_KEY_COMPLEMENT_PREFIX + '.name'): {
                'ru': 'Плюс - потратить на поездку',
            },
            (TANKER_KEY_COMPLEMENT_COMPAT_DESCRIPTION + '.android'): {
                'ru': 'Работает с картой или GooglePay',
            },
            (TANKER_KEY_COMPLEMENT_COMPAT_DESCRIPTION + '.default'): {
                'ru': 'Работает с картой',
            },
            (TANKER_KEY_SCREEN_PROPORTIES + 'title'): {'ru': 'плюс'},
            (TANKER_KEY_SCREEN_PROPORTIES + 'zero_cashback.subtitle'): {
                'ru': 'кэшбэк и подписка',
            },
            (TANKER_KEY_SCREEN_PROPORTIES + 'have_cashback.subtitle'): {
                'ru': 'ваш кэшбэк',
            },
            (TANKER_KEY_SCREEN_PROPORTIES + 'discount.subtitle'): {
                'ru': 'подписка и скидка',
            },
            'personal_wallet.subtitle.balance': {
                'ru': 'Баланс: %(value)s баллов',
            },
            'personal_wallet.name.cashback': {'ru': 'Потратить на поездку'},
            'complementary_method.personal_wallet.name.restaurants': {
                'ru': 'Потратить на заказ',
            },
            'personal_wallet.name.have_money': {
                'ru': 'Активировать %(value)s баллов',
            },
            'personal_wallet.name.no_subscribe': {
                'ru': '10% вернётся баллами',
            },
            'personal_wallet.menu_name.discount.has_subscription': {
                'ru': 'Плюс',
            },
            'personal_wallet.menu_name.discount.no_subscription': {
                'ru': 'Подключить Яндекс.Плюс',
            },
            'personal_wallet.menu_name.cashback.has_subscription': {
                'ru': 'Плюс',
            },
            'personal_wallet.menu_name.cashback.no_subscription.has_money': {
                'ru': 'Подключить Яндекс.Плюс',
            },
            'personal_wallet.menu_name.cashback.no_subscription.no_money': {
                'ru': 'Подключить кэшбэк',
            },
        },
        tariff={
            'currency_with_sign.default': {
                'ru': '$VALUE$ $SIGN$$CURRENCY$',
                'en': '$VALUE$ $SIGN$$CURRENCY$',
            },
            'currency.rub': {'ru': 'руб.', 'en': 'RUB'},
            'currency.uah': {'ru': 'грн.', 'en': 'UAH'},
            'currency.kzt': {'ru': 'тенге', 'en': 'KZT'},
            'currency.byn': {'ru': 'руб.', 'en': 'BYN'},
            'currency_sign.rub': {'ru': '₽', 'en': '₽'},
            'currency_sign.uah': {'ru': '₴', 'en': '₽'},
            'currency_sign.kzt': {'ru': '₸', 'en': '₽'},
            'currency_sign.byn': {'ru': 'Br', 'en': 'Br'},
        },
    ),
    pytest.mark.config(
        COMPLEMENT_TYPES_COMPATIBILITY_MAPPING={
            'personal_wallet': ['card', 'googlepay', 'applepay'],
        },
    ),
]


@pytest.fixture(name='mock_billing_wallet')
def _mock_billing_wallet(mockserver):
    @mockserver.handler('/billing-wallet/balances')
    async def _balance(request):
        response = {
            'balances': [
                {
                    'amount': '120',
                    'currency': 'RUB',
                    'wallet_id': 'billing-wallet',
                },
            ],
        }
        return web.json_response(response, status=200)


async def test_available_accounts_basic(
        test_wallet_client, mock_billing_wallet,
):
    accounts = await test_wallet_client.available_accounts()
    assert len(accounts) == 1
    assert accounts == [
        {
            'id': 'billing-wallet',
            'name': 'Плюс',
            'name_menu': 'Плюс',
            'money_left_as_str': '120\N{NO-BREAK SPACE}$SIGN$$CURRENCY$',
            'money_left_as_decimal': '120',
            'details_screen_properties': {
                'title': '120',
                'subtitle': 'подписка и скидка',
                'glyph_type': 'default_plus',
            },
            'is_new': False,
            'payment_available': True,
            'deposit_available': False,
            'deposit_payment_methods': [],
            'currency_rules': DEFAULT_CURRENCY_RULES,
            'payment_orders': [],
            'discounts': [],
        },
    ]


@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    phone_id=None,
    value=_make_visible_body(_make_visibility()),
)
async def test_available_accounts_no_taxi_headers(
        test_wallet_client, mock_billing_wallet,
):
    accounts = await test_wallet_client.available_accounts(
        phone_id=None, user_id=None,
    )
    assert len(accounts) == 1
    assert accounts[0]['id'] == 'billing-wallet'


@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    personal_phone_id=None,
    value=_make_visible_body(_make_visibility()),
)
async def test_available_accounts_no_personal_phone_id(
        test_wallet_client, mock_billing_wallet,
):
    accounts = await test_wallet_client.available_accounts(
        personal_phone_id=None,
    )
    assert len(accounts) == 1
    assert accounts[0]['id'] == 'billing-wallet'


@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
)
@_make_experiment3('personal_wallet_glyph', yandex_uid='123')
async def test_available_accounts_glyph(
        test_wallet_client, mock_billing_wallet,
):
    accounts = await test_wallet_client.available_accounts()
    assert len(accounts) == 1
    assert accounts[0]['money_left_as_str'] == '120'


async def test_available_accounts_fallback_to_pg(
        test_wallet_client, mockserver,
):
    @mockserver.handler('/billing-wallet/balances')
    async def _balance(request):
        return web.json_response(status=500)

    accounts = await test_wallet_client.available_accounts(
        yandex_uid='fallback_uid',
    )
    assert len(accounts) == 1
    assert accounts[0]['id'] == 'fallback_wallet'
    assert accounts[0]['money_left_as_decimal'] == '364'


@pytest.mark.parametrize(
    'expected_accounts',
    [
        pytest.param(
            [
                {
                    'name': 'Плюс',
                    'name_menu': 'Плюс',
                    'money_left_as_str': '0\N{NO-BREAK SPACE}$SIGN$$CURRENCY$',
                    'money_left_as_decimal': '0',
                    'is_new': True,
                    'details_screen_properties': {
                        'title': 'плюс',
                        'subtitle': 'подписка и скидка',
                    },
                    'payment_available': True,
                    'deposit_available': False,
                    'deposit_payment_methods': [],
                    'currency_rules': DEFAULT_CURRENCY_RULES,
                    'payment_orders': [],
                    'discounts': [],
                },
            ],
        ),
    ],
)
async def test_available_accounts_new(
        test_wallet_client, mockserver, expected_accounts,
):
    @mockserver.handler('/billing-wallet/balances')
    async def _balance(request):
        response = {'balances': []}
        return web.json_response(response, status=200)

    accounts = await test_wallet_client.available_accounts()
    assert len(accounts) == len(expected_accounts)
    if accounts:
        accounts[0].pop('id', None)
        assert accounts[0] == expected_accounts[0]


@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(
        _make_visibility(show_to_new_users=False),
        _make_visibility(show_to_new_users=False, currency='UAH'),
        _make_visibility(show_to_new_users=False, currency='KZT'),
    ),
)
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        'RUB': {'__default__': 1},
        'KZT': {'__default__': 10},
        'UAH': {'__default__': 0.5},
        '__default__': {'__default__': 1},
    },
)
@pytest.mark.parametrize(
    ['currency', 'amount', 'rounded'],
    [
        # factor 0.5
        ('UAH', '120.00', '120.0'),
        ('UAH', '120.49', '120.0'),
        ('UAH', '120.50', '120.5'),
        ('UAH', '120.99', '120.5'),
        ('UAH', '124', '124.0'),
        # factor 1
        ('RUB', '120.00', '120'),
        ('RUB', '120.50', '120'),
        ('RUB', '120.99', '120'),
        ('RUB', '124', '124'),
        # factor 10
        ('KZT', '121', '120'),
        ('KZT', '125', '120'),
        ('KZT', '129', '120'),
    ],
)
async def test_balance_rounding(
        test_wallet_client, mockserver, currency, amount, rounded,
):
    @mockserver.handler('/billing-wallet/balances')
    async def _balance(request):
        response = {
            'balances': [
                {'amount': amount, 'currency': currency, 'wallet_id': 'id'},
            ],
        }
        return web.json_response(response, status=200)

    accounts = await test_wallet_client.available_accounts()
    assert len(accounts) == 1
    assert accounts[0]['money_left_as_decimal'] == rounded


@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='complement_uid',
    service='taxi',
    value=_make_visible_body(_make_visibility()),
)
@_make_experiment3(
    'complement_personal_wallet_payment',
    yandex_uid='complement_uid',
    service='taxi',
)
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='complement_uid',
    app_name='some-unknown-app-name',
    service='taxi',
    value=_make_visible_body(_make_visibility()),
)
@_make_experiment3(
    'complement_personal_wallet_payment',
    yandex_uid='complement_uid',
    app_name='some-unknown-app-name',
    service='taxi',
)
@pytest.mark.parametrize(
    'balance, expected_name',
    [('0', 'Плюс'), ('120', 'Плюс - потратить на поездку')],
)
@pytest.mark.parametrize(
    'app_name, expected_desc',
    [
        ('android', 'Работает с картой или GooglePay'),
        ('some-unknown-app-name', 'Работает с картой'),
    ],
)
async def test_available_accounts_complement_experiment(
        test_wallet_client,
        mockserver,
        balance,
        expected_name,
        app_name,
        expected_desc,
):
    @mockserver.handler('/billing-wallet/balances')
    async def _balance(request):
        response = {
            'balances': [
                {'amount': balance, 'currency': 'RUB', 'wallet_id': 'id'},
            ],
        }
        return web.json_response(response, status=200)

    accounts = await test_wallet_client.available_accounts(
        yandex_uid='complement_uid', app_name=app_name, service='taxi',
    )
    assert len(accounts) == 1
    assert 'is_complement' in accounts[0] and accounts[0]['is_complement']

    attrs = accounts[0]['complement_attributes']
    assert attrs['name'] == expected_name
    assert attrs['compatibility_description'] == expected_desc
    assert attrs['payment_types'] == ['card', 'googlepay', 'applepay']


def _enable_complements(*services):
    result = []
    for service in [None, 'taxi'] + SUPERAPP_SEVICES:
        result.append(
            _make_experiment3(
                'personal_wallet_visible',
                yandex_uid='complement_services_uid',
                service=service,
                value=_make_visible_body(_make_visibility()),
            ),
        )
    for service in services:
        result.append(
            _make_experiment3(
                'complement_personal_wallet_payment',
                yandex_uid='complement_services_uid',
                service=service,
            ),
        )
    return result


@pytest.mark.parametrize(
    'service,enabled',
    [
        pytest.param(None, False),
        pytest.param(
            None, False, marks=_enable_complements('taxi', *SUPERAPP_SEVICES),
        ),
        pytest.param('taxi', False),
        pytest.param(
            'taxi', False, marks=_enable_complements(*SUPERAPP_SEVICES),
        ),
        pytest.param('taxi', True, marks=_enable_complements('taxi')),
        pytest.param(
            'taxi', True, marks=_enable_complements('taxi', *SUPERAPP_SEVICES),
        ),
        pytest.param('eats', False),
        pytest.param('eats', False, marks=_enable_complements('taxi')),
        pytest.param('eats', True, marks=_enable_complements('eats')),
        pytest.param(
            'eats',
            False,
            marks=_enable_complements(
                *[s for s in SUPERAPP_SEVICES if s != 'eats'],
            ),
        ),
    ],
)
async def test_available_accounts_complement_experiment_services(
        test_wallet_client, mock_billing_wallet, service, enabled,
):
    accounts = await test_wallet_client.available_accounts(
        yandex_uid='complement_services_uid', service=service,
    )
    assert len(accounts) == 1
    account = accounts[0]

    assert ('complement_attributes' in account) == enabled
    assert ('is_complement' in account) == enabled
    assert not enabled or account['is_complement']


@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='portal_uid',
    value=_make_visible_body(_make_visibility()),
)
@pytest.mark.parametrize(
    'bound_uids, expected_accounts',
    [('bound_uid_1,bound_uid_2', 1), ('bound_uid_1,merged_uid', 1)],
)
async def test_available_accounts_ignore_bound_wallets(
        test_wallet_client, mock_billing_wallet, bound_uids, expected_accounts,
):
    accounts = await test_wallet_client.available_accounts(
        yandex_uid='portal_uid', headers={'X-YaTaxi-Bound-Uids': bound_uids},
    )
    assert len(accounts) == expected_accounts


async def test_available_accounts_merge_accounts_turned_off(
        test_wallet_client, mock_billing_wallet, stq,
):
    await test_wallet_client.available_accounts(
        yandex_uid='portal_uid',
        headers={'X-YaTaxi-Bound-Uids': 'bound_uid_1,bound_uid_2'},
    )

    assert not stq.personal_wallet_merge_accounts.times_called


@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
)
async def test_available_accounts_no_experiment_personal_wallet_availability(
        test_wallet_client, mock_billing_wallet,
):
    accounts = await test_wallet_client.available_accounts(pass_flags='')
    assert len(accounts) == 1
    assert accounts[0]['payment_available']
    assert 'availability' not in accounts[0]


@_make_experiment3('personal_wallet_availability', yandex_uid='123')
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
)
async def test_available_accounts_experiment_personal_wallet_availability(
        test_wallet_client, mock_billing_wallet,
):
    accounts = await test_wallet_client.available_accounts(pass_flags='')
    assert len(accounts) == 1
    assert not accounts[0]['payment_available']
    availability = accounts[0]['availability']
    assert not availability['available']
    assert availability['disabled_reason'] == 'нужна подписка на Плюс'


@pytest.mark.parametrize('pass_flags', ['some_flags', 'ya-plus'])
@_make_experiment3('personal_wallet_availability', yandex_uid='123')
@_make_experiment3('cashback_for_plus', yandex_uid='123')
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
)
async def test_available_accounts_pass_flags_availability(
        test_wallet_client, mock_billing_wallet, pass_flags,
):
    accounts = await test_wallet_client.available_accounts(
        pass_flags=pass_flags,
    )
    assert len(accounts) == 1
    assert not accounts[0]['payment_available']
    availability = accounts[0]['availability']
    assert not availability['available']
    assert availability['disabled_reason'] == 'нужна подписка на Плюс'
    assert availability['action']['text'] == 'Подключить Яндекс.Плюс'
    assert availability['action']['type'] == 'buy_plus'


@_make_experiment3('personal_wallet_availability', yandex_uid='123')
@_make_experiment3('cashback_for_plus', yandex_uid='123')
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
)
async def test_available_accounts_pass_flags_with_ya_plus(
        test_wallet_client, mock_billing_wallet,
):
    accounts = await test_wallet_client.available_accounts(
        pass_flags='some_flag,ya-plus,some_flag,cashback-plus',
    )
    assert len(accounts) == 1
    assert accounts[0]['payment_available']
    assert 'availability' not in accounts[0]
    assert accounts[0]['subtitle'] == 'Баланс: 120 баллов'


@_make_experiment3('personal_wallet_availability', yandex_uid='123')
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
)
async def test_available_accounts_flags_with_ya_plus_and_no_cashback_plus(
        test_wallet_client, mock_billing_wallet,
):
    accounts = await test_wallet_client.available_accounts(
        pass_flags='some_flag,ya-plus,some_flag',
    )
    assert len(accounts) == 1
    assert not accounts[0]['payment_available']
    assert 'availability' in accounts[0]


@_make_experiment3(
    'personal_wallet_availability', yandex_uid='123', service='grocery',
)
@_make_experiment3('cashback_for_plus', yandex_uid='123', service='grocery')
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
    service='grocery',
)
async def test_available_accounts_pass_flags_with_ya_plus_grocery(
        test_wallet_client, mock_billing_wallet,
):
    accounts = await test_wallet_client.available_accounts(
        pass_flags='some_flag,ya-plus,some_flag', service='grocery',
    )
    assert len(accounts) == 1
    assert accounts[0]['payment_available'] is True
    assert 'availability' not in accounts[0]


@_make_experiment3('personal_wallet_availability', yandex_uid='123')
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
)
@pytest.mark.parametrize(
    'balance,pass_flags,expected_has_counter',
    [
        pytest.param('0', '', False),
        pytest.param(
            '0',
            '',
            True,
            marks=_make_experiment3('cashback_for_plus', yandex_uid='123'),
        ),
        pytest.param(
            '0',
            'ya-plus',
            False,
            marks=_make_experiment3('cashback_for_plus', yandex_uid='123'),
        ),
        pytest.param(
            '10',
            'ya-plus',
            True,
            marks=_make_experiment3('cashback_for_plus', yandex_uid='123'),
        ),
        pytest.param(
            '0',
            'cashback-plus',
            True,
            marks=_make_experiment3('cashback_for_plus', yandex_uid='123'),
        ),
        pytest.param(
            '10',
            'cashback-plus',
            True,
            marks=_make_experiment3('cashback_for_plus', yandex_uid='123'),
        ),
        pytest.param(
            '0',
            'ya-plus,cashback-plus',
            False,
            marks=_make_experiment3('cashback_for_plus', yandex_uid='123'),
        ),
        pytest.param(
            '10',
            'ya-plus,cashback-plus',
            False,
            marks=_make_experiment3('cashback_for_plus', yandex_uid='123'),
        ),
    ],
)
async def test_counter_pass_in_response(
        test_wallet_client,
        mockserver,
        mock_billing_wallet,
        balance,
        pass_flags,
        expected_has_counter,
):
    @mockserver.handler('/billing-wallet/balances')
    async def _balances(request):
        balances_response = {
            'balances': [
                {'amount': balance, 'currency': 'RUB', 'wallet_id': 'w/1'},
            ],
        }
        return web.json_response(balances_response, status=200)

    accounts = await test_wallet_client.available_accounts(
        pass_flags=pass_flags,
    )
    assert len(accounts) == 1
    assert ('notification_counter' in accounts[0]) == expected_has_counter


@_make_experiment3('cashback_for_plus', yandex_uid='123')
@_make_experiment3('personal_wallet_availability', yandex_uid='123')
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
)
@pytest.mark.parametrize(
    'balance,details_screen_properties',
    [
        pytest.param(
            '120',
            {
                'subtitle': 'ваш кэшбэк',
                'title': '120',
                'glyph_type': 'default_plus',
            },
        ),
        pytest.param('0', {'subtitle': 'кэшбэк и подписка', 'title': 'плюс'}),
    ],
)
async def test_personal_wallet_details_screen_properties(
        test_wallet_client,
        mockserver,
        mock_billing_wallet,
        balance,
        details_screen_properties,
):
    @mockserver.handler('/billing-wallet/balances')
    async def _balances(request):
        balances_response = {
            'balances': [
                {'amount': balance, 'currency': 'RUB', 'wallet_id': 'w/1'},
            ],
        }
        return web.json_response(balances_response, status=200)

    accounts = await test_wallet_client.available_accounts()
    assert len(accounts) == 1
    assert (
        accounts[0]['details_screen_properties'] == details_screen_properties
    )


@_make_experiment3(
    'cashback_for_plus', yandex_uid='complement_uid', service='taxi',
)
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='complement_uid',
    service='taxi',
    value=_make_visible_body(_make_visibility()),
)
@_make_experiment3(
    'complement_personal_wallet_payment',
    yandex_uid='complement_uid',
    service='taxi',
)
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='complement_uid',
    app_name='some-unknown-app-name',
    service='taxi',
    value=_make_visible_body(_make_visibility()),
)
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='complement_uid',
    service='restaurants',
    value=_make_visible_body(_make_visibility()),
)
@_make_experiment3(
    'complement_personal_wallet_payment',
    yandex_uid='complement_uid',
    service='restaurants',
)
@pytest.mark.parametrize(
    'balance, expected_name, pass_flags, service',
    [
        ('0', '10% вернётся баллами', 'ya-plus', 'taxi'),
        ('120', 'Активировать 120 баллов', 'cashback-plus', 'taxi'),
        ('120', 'Потратить на поездку', 'ya-plus,cashback-plus', 'taxi'),
        pytest.param(
            '120',
            'Потратить на заказ',
            'ya-plus,cashback-plus',
            'restaurants',
            marks=_make_experiment3(
                'cashback_for_plus',
                yandex_uid='complement_uid',
                service='restaurants',
            ),
        ),
        pytest.param('120', 'Потратить на заказ', '', 'restaurants'),
    ],
)
async def test_available_accounts_complement_name(
        test_wallet_client,
        mockserver,
        balance,
        expected_name,
        pass_flags,
        service,
):
    @mockserver.handler('/billing-wallet/balances')
    async def _balance(request):
        response = {
            'balances': [
                {'amount': balance, 'currency': 'RUB', 'wallet_id': 'id'},
            ],
        }
        return web.json_response(response, status=200)

    accounts = await test_wallet_client.available_accounts(
        yandex_uid='complement_uid', service=service, pass_flags=pass_flags,
    )
    assert len(accounts) == 1
    assert 'is_complement' in accounts[0] and accounts[0]['is_complement']

    attrs = accounts[0]['complement_attributes']
    assert attrs['name'] == expected_name


@_make_experiment3('personal_wallet_availability', yandex_uid='123')
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
)
@pytest.mark.parametrize(
    'balance,name_menu',
    [
        pytest.param('120', 'Подключить Яндекс.Плюс'),
        pytest.param('0', 'Подключить Яндекс.Плюс'),
    ],
)
async def test_personal_wallet_name_menu_discount_no_subscription(
        test_wallet_client,
        mockserver,
        mock_billing_wallet,
        balance,
        name_menu,
):
    @mockserver.handler('/billing-wallet/balances')
    async def _balances(request):
        balances_response = {
            'balances': [
                {'amount': balance, 'currency': 'RUB', 'wallet_id': 'w/1'},
            ],
        }
        return web.json_response(balances_response, status=200)

    accounts = await test_wallet_client.available_accounts(pass_flags='')
    assert len(accounts) == 1
    assert accounts[0]['name_menu'] == name_menu


@_make_experiment3('cashback_for_plus', yandex_uid='123')
@_make_experiment3('personal_wallet_availability', yandex_uid='123')
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
)
@pytest.mark.parametrize(
    'balance,pass_flags,subtitle',
    [
        ('0', 'ya-plus', None),
        ('120', 'cashback-plus', None),
        ('120', 'ya-plus,cashback-plus', 'Баланс: 120 баллов'),
        ('-120', 'ya-plus,cashback-plus', 'Баланс: -120 баллов'),
    ],
)
async def test_available_accounts_subtitle(
        test_wallet_client, mockserver, balance, pass_flags, subtitle,
):
    @mockserver.handler('/billing-wallet/balances')
    async def _balance(request):
        response = {
            'balances': [
                {'amount': balance, 'currency': 'RUB', 'wallet_id': 'id'},
            ],
        }
        return web.json_response(response, status=200)

    accounts = await test_wallet_client.available_accounts(
        pass_flags=pass_flags,
    )
    assert len(accounts) == 1
    if not subtitle:
        assert 'subtitle' not in accounts[0]
    else:
        assert accounts[0]['subtitle'] == subtitle


@_make_experiment3('cashback_for_plus', yandex_uid='123')
@_make_experiment3('personal_wallet_availability', yandex_uid='123')
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
)
@pytest.mark.parametrize(
    'balance,pass_flags,name_menu',
    [
        ('0', 'ya-plus', 'Плюс'),
        ('120', 'cashback-plus', 'Подключить кэшбэк'),
        ('120', 'ya-plus', 'Подключить кэшбэк'),
        ('120', 'ya-plus,cashback-plus', 'Плюс'),
        ('0', '', 'Подключить Яндекс.Плюс'),
        ('0', 'cashback-plus', 'Подключить Яндекс.Плюс'),
    ],
)
async def test_personal_wallet_name_menu_cashback(
        test_wallet_client,
        mockserver,
        mock_billing_wallet,
        balance,
        pass_flags,
        name_menu,
):
    @mockserver.handler('/billing-wallet/balances')
    async def _balances(request):
        balances_response = {
            'balances': [
                {'amount': balance, 'currency': 'RUB', 'wallet_id': 'w/1'},
            ],
        }
        return web.json_response(balances_response, status=200)

    accounts = await test_wallet_client.available_accounts(
        pass_flags=pass_flags,
    )
    assert len(accounts) == 1
    assert accounts[0]['name_menu'] == name_menu


@pytest.mark.config(PLUS_WALLET_WALLET_CURRENCIES=['RUB', 'KZT', 'BYN'])
@_make_experiment3(name='cashback_for_plus_international', yandex_uid='123')
async def test_return_all_available_wallets(
        test_wallet_client, mock_billing_wallet,
):
    """
    Test for return all user_wallets + generated z_wallets,
    using cashback_for_plus_international experiment.

    Also provided PLUS_WALLET_WALLET_CURRENCIES config,
    that means all necessary currencies.
    """
    accounts = await test_wallet_client.available_accounts()
    assert len(accounts) == 3
    currencies_codes = set(
        account['currency_rules']['code'] for account in accounts
    )

    assert currencies_codes == {'RUB', 'KZT', 'BYN'}

    all_available = all(
        account.get('availability') is None for account in accounts
    )
    assert all_available


@pytest.mark.parametrize('is_rub', [(True,), (False,)])
async def test_return_only_one_wallet(
        test_wallet_client, mockserver, is_rub, client_experiments3,
):
    """
    Test for return only one available wallet
    with currency `RUB` or `KZT` (depends on parametrize),
    without using experiment cashback_for_plus_international.
    """

    @mockserver.handler('/billing-wallet/balances')
    async def _balance(request):
        response = {
            'balances': [
                {
                    'amount': '120',
                    'currency': 'RUB',
                    'wallet_id': 'billing-wallet',
                },
                {
                    'amount': '120',
                    'currency': 'KZT',
                    'wallet_id': 'billing-wallet-kzt',
                },
            ],
        }
        return web.json_response(response, status=200)

    exp_args = _build_exps_args(
        'personal_wallet_visible',
        yandex_uid='123',
        value=_make_visible_body(
            _make_visibility(currency='RUB' if is_rub else 'KZT'),
        ),
    )

    client_experiments3.add_record(**exp_args)

    accounts = await test_wallet_client.available_accounts()
    assert len(accounts) == 1

    assert accounts[0]['currency_rules']['code'] == 'RUB' if is_rub else 'KZT'
    assert accounts[0].get('availability') is None


@pytest.mark.parametrize(
    'balance, currency, expected_balance',
    [
        ('120.125', 'RUB', '120'),
        ('10.125', 'KZT', '10'),
        ('120.999', 'RUB', '120'),
        ('10.999', 'KZT', '10'),
        ('1.4000', 'BYN', '1.4'),
    ],
)
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        '__default__': {'__default__': 1},
        'RUB': {'wallet_show_balance': 1, '__default__': 1},
        'KZT': {'wallet_show_balance': 10, '__default__': 1},
        'BYN': {'wallet_show_balance': 0.1, '__default__': 1},
    },
)
async def test_rounding_balance(
        test_wallet_client, mockserver, balance, currency, expected_balance,
):
    @mockserver.handler('/billing-wallet/balances')
    async def _balances(request):
        balances_response = {
            'balances': [
                {'amount': balance, 'currency': currency, 'wallet_id': 'w/1'},
            ],
        }
        return web.json_response(balances_response, status=200)

    accounts = await test_wallet_client.available_accounts()
    accounts = [account for account in accounts if account['id'] == 'w/1']
    assert len(accounts) == 1

    for account in accounts:
        print(account)
        assert account['money_left_as_decimal'] == expected_balance


@_make_experiment3(name='personal_wallets_from_plus_wallet', yandex_uid='123')
@_make_experiment3(name='cashback_for_plus_international', yandex_uid='123')
@_make_experiment3(
    'personal_wallet_visible',
    yandex_uid='123',
    value=_make_visible_body(_make_visibility()),
)
@pytest.mark.parametrize(
    'balances, currency, expected_balances',
    [
        (['120.125'], 'RUB', ['120']),
        (['10.125'], 'KZT', ['10', '0']),
        (['120.999'], 'RUB', ['120']),
        (['10.999'], 'KZT', ['10', '0']),
    ],
)
async def test_get_available_accounts_from_plus_wallet(
        test_wallet_client, mockserver, balances, currency, expected_balances,
):
    @mockserver.handler('/plus-wallet/v1/balances')
    async def _balances(request):
        yandex_uid = request.query['yandex_uid']
        assert yandex_uid == '123'

        balances_response = {
            'balances': [
                {
                    'balance': balance,
                    'currency': currency,
                    'wallet_id': 'w/' + balance,
                }
                for balance in balances
            ],
        }
        return web.json_response(balances_response, status=200)

    accounts = await test_wallet_client.available_accounts()
    assert len(accounts) == len(expected_balances)

    for i, account in enumerate(accounts):
        assert account['money_left_as_decimal'] == expected_balances[i]
